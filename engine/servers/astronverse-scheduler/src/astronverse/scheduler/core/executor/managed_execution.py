"""Durable remote execution receipts around the existing ExecutorManager.

The journal is scoped to a deployment origin and authenticated user. A receipt
is committed before launching a process; an uncertain receipt is never replayed.
It stores no input payloads. Retain receipts for the lifetime of the deployment.
"""

import hashlib
import json
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import psutil

TERMINAL = {"succeeded", "failed", "cancelled", "timeout"}
STOP_CONFIRMATION_SECONDS = 10


def process_stopped(receipt):
    pid, created = receipt.get("processId"), receipt.get("processStarted")
    if type(pid) is not int or pid <= 0 or not isinstance(created, (int, float)):
        return False
    try:
        return psutil.Process(pid).create_time() != created
    except psutil.NoSuchProcess:
        return True
    except psutil.Error:
        return False


def now():
    return datetime.now(UTC).isoformat()


def json_value(value):
    """Do not stringify runtime objects or accept non-JSON mapping keys."""
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        json.dumps(value, allow_nan=False)
        return value
    if type(value) is list:
        return [json_value(item) for item in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: json_value(item) for key, item in value.items()}
    raise ValueError("Unsupported execution value")


class ManagedExecution:
    def __init__(self, manager, directory: Path, origin: str):
        self.manager = manager
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = directory / (hashlib.sha256(origin.encode()).hexdigest() + ".sqlite3")
        self.lock = threading.RLock()
        self.active = {}
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS identity (id TEXT PRIMARY KEY)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS runs (owner TEXT, id TEXT, fingerprint TEXT, receipt TEXT, "
                "PRIMARY KEY(owner,id))"
            )
            row = db.execute("SELECT id FROM identity").fetchone()
            self.client_id = row[0] if row else str(uuid4())
            if not row:
                db.execute("INSERT INTO identity VALUES (?)", (self.client_id,))
            # Scheduler restart is not evidence of completion or permission to rerun.
            for owner, execution_id, serialized in db.execute("SELECT owner,id,receipt FROM runs").fetchall():
                receipt = json.loads(serialized)
                if receipt["status"] not in TERMINAL:
                    receipt.update(status="unknown", supportsCancel=False, error="CLIENT_RESTARTED")
                    db.execute(
                        "UPDATE runs SET receipt=? WHERE owner=? AND id=?", (json.dumps(receipt), owner, execution_id)
                    )
        self.path.chmod(0o600)

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            db.execute("PRAGMA synchronous=FULL")
            with db:
                yield db
        finally:
            db.close()

    def _read(self, owner, execution_id):
        with self._db() as db:
            row = db.execute(
                "SELECT fingerprint,receipt FROM runs WHERE owner=? AND id=?", (owner, execution_id)
            ).fetchone()
        if not row:
            return None, None
        receipt = json.loads(row[1])
        if receipt["status"] == "unknown" and receipt.get("runId"):
            try:
                recovered = json.loads(self.result_path(owner, execution_id).read_text(encoding="utf-8"))
                if (
                    recovered.get("runId") == receipt["runId"]
                    and recovered.get("status") in TERMINAL
                    and recovered.get("finishedAt")
                    and recovered.get("startedAt")
                    and process_stopped(recovered)
                ):
                    receipt.update({key: recovered.get(key) for key in ("status", "result", "error", "finishedAt")})
                    receipt["startedAt"] = receipt.get("startedAt") or recovered["startedAt"]
                    receipt["result"] = None if receipt.get("secretResult") else json_value(receipt["result"])
                    if receipt["status"] == "cancelled" and receipt.get("stopReason") == "timeout":
                        receipt["status"] = "timeout"
                    with self._db() as db:
                        db.execute(
                            "UPDATE runs SET receipt=? WHERE owner=? AND id=?",
                            (json.dumps(receipt, allow_nan=False), owner, execution_id),
                        )
            except (OSError, ValueError, TypeError):
                pass
        return row[0], receipt

    def result_path(self, owner, execution_id):
        name = hashlib.sha256(json.dumps([owner, execution_id]).encode()).hexdigest()
        return self.path.parent / self.path.stem / (name + ".json")

    def _change(self, owner, execution_id, **changes):
        with self.lock:
            _, receipt = self._read(owner, execution_id)
            if receipt is None or receipt["status"] in TERMINAL:
                return receipt
            receipt.update(changes)
            if receipt["status"] in TERMINAL:
                receipt.update(finishedAt=now(), supportsCancel=False)
            with self._db() as db:
                db.execute(
                    "UPDATE runs SET receipt=? WHERE owner=? AND id=?",
                    (json.dumps(receipt, allow_nan=False), owner, execution_id),
                )
            return receipt

    def _unresolved_process(self):
        # A new Scheduler must not overlap a still-running orphan with new work.
        with self._db() as db:
            rows = db.execute("SELECT owner,id FROM runs").fetchall()
        for owner, execution_id in rows:
            _, receipt = self._read(owner, execution_id)
            if receipt["status"] not in TERMINAL and receipt.get("runId") and not process_stopped(receipt):
                return True
        return False

    def handle(self, command):
        if not isinstance(command, dict) or command.get("protocol") != 1:
            return {"error": "CLIENT_PROTOCOL_UNSUPPORTED"}
        action = command.get("action")
        if action == "capabilities":
            return {
                "protocol": 1,
                "clientId": self.client_id,
                "supportsCancel": True,
                "busy": self.manager.status() or bool(self.active) or self._unresolved_process(),
            }
        owner, execution_id = command.get("owner"), command.get("executionId")
        if (
            not isinstance(owner, str)
            or not owner
            or not isinstance(execution_id, str)
            or len(execution_id) != 36
            or command.get("clientId") != self.client_id
        ):
            return {"error": "EXECUTION_TARGET_MISMATCH"}
        if action == "start":
            return self.start(owner, execution_id, command)
        with self.lock:
            _, receipt = self._read(owner, execution_id)
            if receipt is None:
                return {"error": "EXECUTION_NOT_FOUND", "clientId": self.client_id}
            if action == "cancel":
                if command.get("runId") != receipt.get("runId"):
                    return {"error": "EXECUTION_TARGET_MISMATCH"}
                if receipt["status"] not in TERMINAL:
                    if not receipt["supportsCancel"]:
                        return {"error": "CANCEL_UNSUPPORTED"}
                    receipt = self._change(owner, execution_id, cancelRequested=True)
            elif action != "get":
                return {"error": "INVALID_COMMAND"}
            return receipt

    def start(self, owner, execution_id, command):
        payload = command.get("payload")
        try:
            encoded = json.dumps(json_value(payload), sort_keys=True, separators=(",", ":"), allow_nan=False)
            fingerprint = hashlib.sha256(encoded.encode()).hexdigest()
            if not isinstance(payload, dict) or not isinstance(payload.get("params", {}), dict):
                raise ValueError
            timeout = payload.get("executionTimeout")
            if timeout is not None and (type(timeout) is not int or not 1 <= timeout <= 86400):
                raise ValueError
        except (ValueError, TypeError):
            return {"error": "INVALID_ARGUMENTS"}
        with self.lock:
            previous, receipt = self._read(owner, execution_id)
            if receipt:
                return receipt if previous == fingerprint else {"error": "IDEMPOTENCY_CONFLICT"}
            receipt = {
                "protocol": 1,
                "executionId": execution_id,
                "clientId": self.client_id,
                "projectId": payload.get("projectId"),
                "secretResult": bool(payload.get("secretFields")),
                "runId": None,
                "status": "accepted",
                "acceptedAt": now(),
                "startedAt": None,
                "finishedAt": None,
                "result": None,
                "error": None,
                "supportsCancel": True,
                "cancelRequested": False,
            }
            if self.active or self.manager.status() or self._unresolved_process():
                receipt.update(status="failed", error="CLIENT_BUSY", finishedAt=now(), supportsCancel=False)
            with self._db() as db:
                db.execute("INSERT INTO runs VALUES (?,?,?,?)", (owner, execution_id, fingerprint, json.dumps(receipt)))
            if receipt["status"] == "accepted":
                self.active[(owner, execution_id)] = None
                threading.Thread(target=self._run, args=(owner, execution_id, payload), daemon=True).start()
            return receipt

    def _run(self, owner, execution_id, payload):
        # Import here to keep persistence/protocol tests independent of desktop services.
        from astronverse.scheduler.core.executor.executor import ProjectExecPosition

        observing = False
        try:
            with self.lock:
                _, receipt = self._read(owner, execution_id)
                if receipt["cancelRequested"]:
                    self._change(owner, execution_id, status="cancelled")  # No process was launched.
                    return

            def bind(instance):
                # ExecutorManager invokes this before starting the exact process.
                with self.lock:
                    _, receipt = self._read(owner, execution_id)
                    if receipt["cancelRequested"]:
                        self._change(owner, execution_id, status="cancelled")
                        raise RuntimeError("Execution cancelled before process launch")
                    self.active[(owner, execution_id)] = instance
                    self._change(owner, execution_id, runId=instance.exec_id)
                    path = self.result_path(owner, execution_id)
                    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    instance.ins.set_param("managed_receipt", quote(str(path)))

            def started(instance):
                nonlocal observing
                proc = instance.ins.proc
                self._change(
                    owner,
                    execution_id,
                    status="running",
                    startedAt=datetime.fromtimestamp(instance.launched_at, UTC).isoformat(),
                    processId=proc.pid,
                    processStarted=psutil.Process(proc.pid).create_time(),
                )
                observing = True
                threading.Thread(
                    target=self._observe, args=(owner, execution_id, payload, instance), daemon=True
                ).start()

            executor = self.manager.create(
                project_id=payload["projectId"],
                version=payload["version"],
                exec_position=ProjectExecPosition.EXECUTOR,
                run_param=json.dumps(
                    [
                        {
                            "varName": key,
                            "varValue": value,
                            "encoding": "json",
                            "secret": key in payload.get("secretFields", []),
                        }
                        for key, value in payload.get("params", {}).items()
                    ],
                    allow_nan=False,
                ),
                recording_config=json.loads(payload["recordingConfig"]) if payload.get("recordingConfig") else None,
                on_prepared=bind,
                on_started=started,
                external_secrets=bool(payload.get("secretFields")),
            )
            if executor is None and not observing:
                self._change(
                    owner, execution_id, status="unknown", error="EXECUTION_START_UNCONFIRMED", supportsCancel=False
                )
        except Exception:
            if not observing:
                self._change(
                    owner, execution_id, status="unknown", error="EXECUTION_START_UNCONFIRMED", supportsCancel=False
                )
        finally:
            if not observing:
                with self.lock:
                    self.active.pop((owner, execution_id), None)

    def _observe(self, owner, execution_id, payload, executor):
        from astronverse.scheduler.core.executor.executor import ExecuteStatus

        try:
            deadline = executor.launched_at + payload["executionTimeout"] if payload.get("executionTimeout") else None
            stop_reason = None
            stop_at = None
            while True:
                # The concrete process handle is retained; never use stop_current/project.
                alive = executor.ins.is_alive()
                if not alive and executor.report_log_time < 0:
                    if executor.execute_status == ExecuteStatus.SUCCESS:
                        try:
                            result = json_value(executor.execute_data)
                            # A workflow accepting secrets has no public result summary.
                            if payload.get("secretFields"):
                                result = None
                            self._change(owner, execution_id, status="succeeded", result=result)
                        except (TypeError, ValueError):
                            self._change(owner, execution_id, status="failed", error="UNSUPPORTED_RESULT")
                    elif stop_reason:
                        self._change(owner, execution_id, status=stop_reason)
                    elif executor.execute_status == ExecuteStatus.CANCEL:
                        self._change(owner, execution_id, status="cancelled")
                    else:
                        code = (
                            "UNSUPPORTED_RESULT"
                            if executor.execute_reason == "UNSUPPORTED_RESULT"
                            else "EXECUTION_FAILED"
                        )
                        self._change(owner, execution_id, status="failed", error=code)
                    return
                if alive and stop_reason is None:
                    with self.lock:
                        _, receipt = self._read(owner, execution_id)
                    if receipt["cancelRequested"] or (deadline is not None and time.time() >= deadline):
                        stop_reason = "cancelled" if receipt["cancelRequested"] else "timeout"
                        stop_at = time.monotonic()
                        self._change(owner, execution_id, stopReason=stop_reason)
                        try:
                            self.manager.close(executor)
                        except Exception:
                            self._change(
                                owner, execution_id, status="unknown", error="STOP_UNCONFIRMED", supportsCancel=False
                            )
                if alive and stop_at is not None and time.monotonic() - stop_at >= STOP_CONFIRMATION_SECONDS:
                    self._change(owner, execution_id, status="unknown", error="STOP_UNCONFIRMED", supportsCancel=False)
                    stop_at = None  # Continue observing; do not resend stop or rewrite every poll.
                time.sleep(0.1)
        except Exception:
            self._change(
                owner, execution_id, status="unknown", error="EXECUTION_OBSERVATION_FAILED", supportsCancel=False
            )
        finally:
            with self.lock:
                self.active.pop((owner, execution_id), None)
