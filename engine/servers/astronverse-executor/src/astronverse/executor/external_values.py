"""JSON value checks for managed external runs, before report serialization."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import psutil


def json_value(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        json.dumps(value, allow_nan=False)
        return value
    if type(value) is list:
        return [json_value(item) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: json_value(item) for key, item in value.items()}
    raise ValueError("UNSUPPORTED_RESULT")


def save_result(path, run_id, status, result, started_at, error=None):
    """An atomic terminal receipt lets Scheduler recover after its own restart."""
    target = Path(path)
    temporary = target.with_suffix(".tmp")
    payload = {
        "runId": run_id,
        "status": status,
        "result": json_value(result),
        "error": error,
        "processId": os.getpid(),
        "processStarted": psutil.Process().create_time(),
        "startedAt": started_at,
        "finishedAt": datetime.now(UTC).isoformat(),
    }
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.chmod(0o600)
    os.replace(temporary, target)
