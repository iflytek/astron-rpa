"""Additional guards for approved managed runs. Disabled for ordinary workflows.

Trusted Python can bypass Python-level hooks; this is an execution contract and
audit mechanism, not a sandbox for untrusted code.
"""

import hashlib
import importlib.util
import inspect
import json
import os
import sys
import threading
from enum import Enum
from pathlib import Path, PurePath


class ManagedRiskError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


_contract = None
_audit = None
_count = 0
_violation = None
_lock = threading.RLock()


def configure(path):
    global _contract, _audit, _count, _violation
    contract = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        contract.get("version") != 1
        or not isinstance(contract.get("operations"), dict)
        or not contract["operations"]
        or type(contract.get("maxOperations")) is not int
        or not 1 <= contract["maxOperations"] <= 10000
        or not isinstance(contract.get("codeHashes"), list)
        or not isinstance(contract.get("approval"), dict)
    ):
        raise ManagedRiskError("RISK_CONTRACT_INVALID")
    _contract, _audit, _count = contract, Path(path).with_suffix(".audit.jsonl"), 0
    _violation = None


def active():
    return _contract is not None


def reject(code):
    global _violation
    _violation = code
    raise ManagedRiskError(code)


def assert_safe():
    if _violation:
        raise ManagedRiskError(_violation)


def normalize(value):
    if isinstance(value, Enum):
        return normalize(value.value)
    if isinstance(value, str):
        workspace = os.environ.get("ASTRON_RPA_MANAGED_FILES_DIRECTORY")
        if workspace and value.replace("\\", "/").casefold().startswith(
            workspace.replace("\\", "/").rstrip("/").casefold() + "/"
        ):
            return "$workspace/" + value.replace("\\", "/")[len(workspace.rstrip("/\\")) + 1 :]
        return str(value)
    if isinstance(value, PurePath):
        return normalize(str(value))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"$bytesSHA256": hashlib.sha256(value).hexdigest()}
    if value is None or type(value) in (bool, int, float, str):
        return value
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return {k: normalize(v) for k, v in value.items()}
    # Local handles never cross the JSON boundary. Their type is stable across
    # fresh connections; addresses/repr may contain credentials and are not used.
    return {"$localHandle": type(value).__module__ + "." + type(value).__qualname__}


def argument_digest(func, args, kwargs):
    bound = inspect.signature(func).bind(*args, **{k: v for k, v in kwargs.items() if not k.startswith("__")})
    bound.apply_defaults()
    values = {k: normalize(v) for k, v in bound.arguments.items() if k not in ("self", "cls")}
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if len(encoded) > 1024 * 1024:
        raise ValueError("RISK_ARGUMENTS_DENIED")
    return hashlib.sha256(encoded).hexdigest()


def record(event, **values):
    # Only identifiers, hashes and counts. Fail closed if the audit cannot persist.
    try:
        with _audit.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"event": event, "approvalId": _contract["approval"]["id"], **values}) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        reject("RISK_AUDIT_FAILED")


def check_operation(func, key, args, kwargs):
    global _count
    if not active():
        return
    with _lock:
        assert_safe()
        rule = _contract["operations"].get(key)
        # Some public operations use Class.method (Compress, Clipboard, keyboard
        # and mouse), while FTP/process declarations retain legacy metadata keys.
        # Resolve only an approved identity for this same function. Never retry a
        # different identity after its argument constraint has failed.
        if rule is None:
            parts = func.__qualname__.split(".")
            if len(parts) >= 2 and parts[-2] != "<locals>":
                key = ".".join(parts[-2:])
                rule = _contract["operations"].get(key)
        if not rule or _count >= _contract["maxOperations"]:
            record("denied", operation=key)
            reject("RISK_OPERATION_DENIED")
        try:
            fingerprint = argument_digest(func, args, kwargs)
        except (ValueError, TypeError, RecursionError):
            reject("RISK_ARGUMENTS_DENIED")
        if rule["argumentHashes"] and fingerprint not in rule["argumentHashes"]:
            record("denied", operation=key, argumentsHash=fingerprint)
            reject("RISK_ARGUMENTS_DENIED")
        _count += 1
        record("accepted", operation=key, argumentsHash=fingerprint, risk=rule["risk"], ordinal=_count)


def check_code(source):
    if not active():
        return
    fingerprint = hashlib.sha256(source).hexdigest()
    with _lock:
        accepted = fingerprint in _contract["codeHashes"]
        record("code-accepted" if accepted else "code-denied", codeHash=fingerprint)
        if not accepted:
            reject("RISK_CODE_DENIED")


def check_module(path, package):
    if not active():
        return
    # Published packages are trusted. Review also covers their imports and side
    # effects; find_spec is not a safe loader for arbitrary untrusted packages.
    spec = importlib.util.find_spec(path, package)
    if spec is None or spec.origin is None or Path(spec.origin).suffix != ".py":
        reject("RISK_CODE_DENIED")
    source = Path(spec.origin).read_bytes()
    check_code(source)
    return spec, source


def import_reviewed_module(path, package):
    if not active():
        return importlib.import_module(path, package=package)
    spec, source = check_module(path, package)
    # Execute the bytes that were actually checked. import_module may otherwise
    # reuse sys.modules or timestamp-based bytecode unrelated to those bytes.
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(spec.name)
    sys.modules[spec.name] = module
    try:
        exec(compile(source, spec.origin, "exec"), module.__dict__)  # noqa: S102 -- execute the reviewed, hash-checked release bytes
    except BaseException:
        if previous is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous
        raise
    return module
