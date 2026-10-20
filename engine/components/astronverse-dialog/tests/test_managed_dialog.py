import sys
from types import SimpleNamespace

import pytest
from astronverse.dialog import InputType, SelectType, TimeType, managed
from astronverse.dialog.dialog import Dialog


def test_managed_dialog_dispatch_is_opt_in_and_preserves_legacy_host(monkeypatch):
    from astronverse.actionlib.atomic import atomicMg

    calls = []

    def reply(message, _timeout, callback):
        calls.append(message)
        callback(SimpleNamespace(data={"input_content": "legacy"}))

    monkeypatch.delenv("ASTRON_RPA_MANAGED_DESKTOP", raising=False)
    monkeypatch.setattr(atomicMg, "cfg", lambda: {"WS": SimpleNamespace(send_reply=reply)})
    assert Dialog.input_box() == "legacy"
    assert len(calls) == 1
    monkeypatch.setenv("ASTRON_RPA_MANAGED_DESKTOP", "1")
    monkeypatch.setattr(managed, "show", lambda kind, **options: (kind, options))
    kind, options = Dialog.input_box(input_type=InputType.PASSWORD, default_input_pwd="test-secret")
    assert kind == "input"
    assert options["password"]
    assert options["default"] == "test-secret"
    assert len(calls) == 1
    assert Dialog.message_box(auto_check=True, wait_time=2)[1]["seconds"] == 2
    assert Dialog.select_box(select_type=SelectType.MULTI, options=["a", "b"])[1]["multiple"]
    assert Dialog.select_time_box(time_type=TimeType.TIME_RANGE)[1]["multiple"]


@pytest.mark.parametrize(
    ("format_string", "value"),
    [
        ("YYYY-MM-DD", "2026-10-14"),
        ("YYYY/MM/DD HH:mm", "2026/10/14 10:30"),
        ("YYYY-MM-DD HH:mm:ss", "2026-10-14 10:30:05"),
    ],
)
def test_native_date_values_match_declared_formats(format_string, value):
    assert managed.time_value([value], format_string, False) == value


def test_native_date_ranges_reject_invalid_or_reversed_values():
    assert managed.time_value(["2026-10-14", "2026-10-15"], "YYYY-MM-DD", True) == ["2026-10-14", "2026-10-15"]
    for values in (["2026-10-15", "2026-10-14"], ["not a date", "2026-10-15"], ["2026-10-14"]):
        with pytest.raises(ValueError):
            managed.time_value(values, "YYYY-MM-DD", True)


def test_missing_native_host_returns_only_safe_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    with pytest.raises(managed.ManagedDialogError) as error:
        managed.show("input", title="synthetic")
    assert error.value.code == "DESKTOP_HUMAN_UNAVAILABLE"
