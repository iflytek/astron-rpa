"""Low-cardinality process metrics and allowlisted structured events.

Scrape every OpenAPI process. IDs belong in logs, never metric labels. Execution
observations are not admission counts; transitions count only successful DB CAS.
"""

import json
import logging
import os
import threading
import time
from collections import Counter

from app.middlewares.tracing import correlation_ctx, get_request_id, safe_id
from app.utils.sensitive_logging import redact_sensitive_text

_lock = threading.Lock()
_counts = Counter()
_started = time.time()
_buckets = (0.1, 0.5, 1, 2, 5, 15, 30, 60, float("inf"))
_fields = {"tool", "rpc_id", "execution_id", "run_id", "outcome", "error_code", "worker_id", "client_id"}


class JsonFormatter(logging.Formatter):
    converter = time.gmtime

    def format(self, record):
        value = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "pid": os.getpid(),
            "trace_id": get_request_id(),
            **(correlation_ctx.get() or {}),
            "message": redact_sensitive_text(record.getMessage()),
        }
        value.update(getattr(record, "safe_event", {}))
        if record.exc_info:
            value["exception_type"] = record.exc_info[0].__name__
        return json.dumps(value, ensure_ascii=False, allow_nan=False)


def event(name, **fields):
    from app.logger import get_logger

    safe = {key: safe_id(value) for key, value in fields.items() if key in _fields}
    get_logger("app.events").info(name, extra={"safe_event": safe})


def increment(name, label=""):
    with _lock:
        _counts[(name, label)] += 1


def execution_transition(status):
    if status in {"PENDING", "RUNNING", "UNKNOWN", "COMPLETED", "FAILED", "CANCELLED", "TIMEOUT"}:
        increment("astron_execution_transitions_total", status.lower())


def execution_finished(status, code, seconds=None):
    from app.services.execution_management import ERRORS

    execution_transition(status)
    if code in ERRORS:
        increment("astron_execution_errors_total", code)
    if seconds is not None and seconds >= 0:
        with _lock:
            _counts[("astron_execution_duration_seconds_sum", "")] += seconds
            _counts[("astron_execution_duration_seconds_count", "")] += 1


def http_observed(scope, status, seconds):
    path = scope.get("path", "")
    if path.startswith("/health/"):
        return
    route = (
        "mcp"
        if path.startswith("/mcp")
        else "rest"
        if path.startswith(("/workflows", "/executions", "/files"))
        else "other"
    )
    outcome = str(status // 100) + "xx" if 100 <= status < 600 else "other"
    with _lock:
        _counts[("astron_http_requests_total", f"{route}:{outcome}")] += 1
        _counts[("astron_http_duration_seconds_sum", route)] += seconds
        _counts[("astron_http_duration_seconds_count", route)] += 1
        for bound in _buckets:
            if seconds <= bound:
                _counts[("astron_http_duration_seconds_bucket", f"{route}:{bound}")] += 1
    event("http_request", outcome=outcome)


def render_metrics(online, ready=True):
    with _lock:
        values = sorted(_counts.items())
    lines = [
        f"astron_process_start_time_seconds {_started}",
        f"astron_clients_online {online}",
        f"astron_ready {int(ready)}",
    ]
    for (name, label), value in values:
        if name == "astron_http_requests_total":
            route, status = label.split(":")
            labels = f'route="{route}",status="{status}"'
        elif name.endswith("_bucket"):
            route, bound = label.split(":")
            labels = f'route="{route}",le="{"+Inf" if bound == "inf" else bound}"'
        elif name.startswith("astron_http_duration"):
            labels = f'route="{label}"'
        else:
            labels = f'outcome="{label}"'
        lines.append(f"{name}{{{labels}}} {value}")
    return "\n".join(lines) + "\n"
