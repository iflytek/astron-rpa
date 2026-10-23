import hashlib
import importlib
import json
from enum import Enum

import pytest
from astronverse.actionlib import managed_risk as risk
from astronverse.actionlib.atomic import atomicMg


@pytest.fixture(autouse=True)
def reset():
    importlib.reload(risk)
    yield
    importlib.reload(risk)


def configure(tmp_path, rules, **changes):
    path = tmp_path / "request.risk.json"
    contract = {"version": 1, "approval": {"id": "review-1"}, "operations": rules, "maxOperations": 2, "codeHashes": []}
    contract.update(changes)
    path.write_text(json.dumps(contract))
    risk.configure(path)
    return path.with_suffix(".audit.jsonl")


def test_unmanaged_operations_unchanged():
    @atomicMg.atomic("RiskFixture")
    def ordinary(value="ok"):
        return value

    assert ordinary(value="ok") == "ok"


def test_direct_calls_are_checked_and_changed_values_never_execute(tmp_path):
    calls = []

    @atomicMg.atomic("RiskFixture")
    def write(value="default"):
        calls.append(value)
        return value

    approved = risk.argument_digest(write.__wrapped__, (), {"value": "approved"})
    audit = configure(tmp_path, {"RiskFixture.write": {"risk": "high", "argumentHashes": [approved]}})
    assert write(value="approved") == "approved"
    with pytest.raises(risk.ManagedRiskError, match="RISK_ARGUMENTS_DENIED"):
        write(value="unapproved-secret")
    assert calls == ["approved"]
    events = [json.loads(line) for line in audit.read_text().splitlines()]
    assert [e["event"] for e in events] == ["accepted", "denied"]
    assert "unapproved-secret" not in audit.read_text()


def test_allowlist_and_bounded_operation_count(tmp_path):
    def operation(value=1):
        return value

    fingerprint = risk.argument_digest(operation, (), {})
    configure(tmp_path, {"Fixture.call": {"risk": "high", "argumentHashes": [fingerprint]}}, maxOperations=1)
    risk.check_operation(operation, "Fixture.call", (), {})
    with pytest.raises(risk.ManagedRiskError, match="RISK_OPERATION_DENIED"):
        risk.check_operation(operation, "Fixture.call", (), {})
    with pytest.raises(risk.ManagedRiskError, match="RISK_OPERATION_DENIED"):
        risk.check_operation(operation, "Fixture.unknown", (), {})


@pytest.mark.parametrize("operation", ["FileFixture.read", "LegacySystemGroup.read"])
def test_component_class_names_and_legacy_metadata_keys_are_supported(tmp_path, operation):
    class FileFixture:
        @staticmethod
        @atomicMg.atomic("LegacySystemGroup")
        def read(value="approved"):
            return value

    fingerprint = risk.argument_digest(FileFixture.read.__wrapped__, (), {})
    audit = configure(tmp_path, {operation: {"risk": "high", "argumentHashes": [fingerprint]}})
    assert FileFixture.read() == "approved"
    assert json.loads(audit.read_text().splitlines()[0])["operation"] == operation
    with pytest.raises(risk.ManagedRiskError, match="RISK_ARGUMENTS_DENIED"):
        FileFixture.read(value="unapproved")


def test_metadata_argument_denial_does_not_fall_back_to_another_alias(tmp_path):
    calls = []

    class AliasFixture:
        @staticmethod
        @atomicMg.atomic("LegacyAliasGroup")
        def write(value="approved"):
            calls.append(value)

    fingerprint = risk.argument_digest(AliasFixture.write.__wrapped__, (), {})
    configure(
        tmp_path,
        {
            "LegacyAliasGroup.write": {"risk": "high", "argumentHashes": ["a" * 64]},
            "AliasFixture.write": {"risk": "high", "argumentHashes": [fingerprint]},
        },
    )
    with pytest.raises(risk.ManagedRiskError, match="RISK_ARGUMENTS_DENIED"):
        AliasFixture.write()
    assert calls == []


def test_source_hash_checked_before_import(tmp_path, monkeypatch):
    code = b'def main():\n    return "ok"\n'
    module = tmp_path / "approved_code.py"
    module.write_bytes(code)
    monkeypatch.syspath_prepend(str(tmp_path))
    configure(
        tmp_path,
        {"Smart.run_code": {"risk": "high", "argumentHashes": ["a" * 64]}},
        codeHashes=[hashlib.sha256(code).hexdigest()],
    )
    risk.check_module("approved_code", None)
    module.write_bytes(b'raise RuntimeError("must never import")\n')
    with pytest.raises(risk.ManagedRiskError, match="RISK_CODE_DENIED"):
        risk.check_module("approved_code", None)


def test_normalization_binds_defaults_enums_without_handle_reprs():
    class Mode(Enum):
        VALUE = "mode"

    class Handle:
        def __repr__(self):
            raise AssertionError("No handle repr")

    def call(value=Mode.VALUE, connection=None):
        pass

    assert risk.argument_digest(call, (), {}) == risk.argument_digest(call, (), {"value": "mode", "connection": None})
    assert risk.argument_digest(call, (), {"connection": Handle()}) == risk.argument_digest(
        call, (), {"connection": Handle()}
    )

    class Text(str):  # noqa: FURB189 -- exercise scalar subclasses used by component parameter types
        pass

    assert risk.argument_digest(call, (), {"value": Text("reviewed")}) == risk.argument_digest(
        call, (), {"value": "reviewed"}
    )
    assert risk.argument_digest(call, (), {"value": b"first"}) != risk.argument_digest(call, (), {"value": b"changed"})


def test_audit_failure_prevents_operation(tmp_path, monkeypatch):
    configure(
        tmp_path, {"Fixture.call": {"risk": "high", "argumentHashes": [risk.argument_digest(lambda: None, (), {})]}}
    )
    monkeypatch.setattr(risk, "record", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("disk full")))
    with pytest.raises(OSError):
        risk.check_operation(lambda: None, "Fixture.call", (), {})


def test_checked_source_is_executed_even_if_module_cache_is_stale(tmp_path, monkeypatch):
    import sys
    import types

    source = b'def main():\n    return "approved"\n'
    (tmp_path / "risk_cached_fixture.py").write_bytes(source)
    monkeypatch.syspath_prepend(str(tmp_path))
    stale = types.ModuleType("risk_cached_fixture")
    stale.__spec__ = importlib.util.spec_from_file_location("risk_cached_fixture", tmp_path / "risk_cached_fixture.py")
    stale.main = lambda: "unapproved"
    monkeypatch.setitem(sys.modules, "risk_cached_fixture", stale)
    configure(
        tmp_path,
        {"Smart.run_code": {"risk": "high", "argumentHashes": ["a" * 64]}},
        codeHashes=[hashlib.sha256(source).hexdigest()],
    )
    assert risk.import_reviewed_module("risk_cached_fixture", None).main() == "approved"
