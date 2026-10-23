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
        self.origin = origin
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = directory / (hashlib.sha256(origin.encode()).hexdigest() + ".sqlite3")
        self.lock = threading.RLock()
        self.active = {}
        self.recovering = set()
        self.cleaning = set()
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
                    if receipt.get("error") == "EXECUTION_START_UNCONFIRMED" and receipt.get("runId") is None:
                        # Keep the pre-bind failure evidence for _read below.
                        continue
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
        """Read a receipt without holding the lock across file I/O.

        Recovery may upload a completed file result and terminate an owned
        Office process. Only the journal snapshot and the final compare-and-
        swap are protected by ``self.lock``; concurrent readers observe the
        durable ``unknown`` state while one reader performs recovery.
        """
        with self.lock:
            row = self._read_snapshot(owner, execution_id)
            if not row:
                return None, None
            receipt = json.loads(row[1])
            key = (owner, execution_id)
            if (
                receipt["status"] == "unknown"
                and receipt.get("error") == "EXECUTION_START_UNCONFIRMED"
                and receipt.get("runId") is None
                and key not in self.active
            ):
                # bind() durably records runId before process launch. Once the
                # preparation worker has exited, absence proves zero launches.
                # A bound but unconfirmed launch must remain unknown.
                receipt.update(status="failed", error="EXECUTION_FAILED", finishedAt=now(), supportsCancel=False)
                with self._db() as db:
                    db.execute(
                        "UPDATE runs SET receipt=? WHERE owner=? AND id=?",
                        (json.dumps(receipt), owner, execution_id),
                    )
            recover = (
                receipt["status"] == "unknown"
                and receipt.get("runId")
                and key not in self.recovering
                and key not in self.active
            )
            if recover:
                self.recovering.add(key)

        if recover:
            try:
                receipt = self._recover_receipt(owner, execution_id, receipt)
            finally:
                with self.lock:
                    self.recovering.discard(key)
        if receipt["status"] in TERMINAL and receipt.get("fileWorkflow"):
            with self.lock:
                cleanup = key not in self.active and key not in self.cleaning
                if cleanup:
                    self.cleaning.add(key)
            if cleanup:
                try:
                    self._cleanup_files(owner, execution_id)
                finally:
                    with self.lock:
                        self.cleaning.discard(key)
        return row[0], receipt

    def _read_snapshot(self, owner, execution_id):
        with self._db() as db:
            return db.execute(
                "SELECT fingerprint,receipt FROM runs WHERE owner=? AND id=?", (owner, execution_id)
            ).fetchone()

    def _recover_receipt(self, owner, execution_id, receipt):
        original = receipt.copy()
        try:
            recovered = json.loads(self.result_path(owner, execution_id).read_text(encoding="utf-8"))
            if not (
                recovered.get("runId") == receipt["runId"]
                and recovered.get("status") in TERMINAL
                and recovered.get("finishedAt")
                and recovered.get("startedAt")
                and process_stopped(recovered)
            ):
                return receipt
            if receipt.get("desktopError"):
                # An interrupted desktop result must never publish files, even
                # if the process wrote a late success receipt before it stopped.
                recovered.update(status="failed", result=None, error=receipt["desktopError"])
            if receipt.get("fileWorkflow") and recovered["status"] == "succeeded":
                try:
                    workspace = self._file_workspace(owner, execution_id)
                    recovered["result"] = workspace.finish(recovered.get("result"))
                    workspace.cleanup()
                except Exception:
                    recovered.update(status="failed", result=None, error="FILE_TRANSFER_FAILED")
            receipt.update({key: recovered.get(key) for key in ("status", "result", "error", "finishedAt")})
            receipt["supportsCancel"] = False
            receipt["startedAt"] = receipt.get("startedAt") or recovered["startedAt"]
            receipt["result"] = None if receipt.get("secretResult") else json_value(receipt["result"])
            if receipt["status"] == "cancelled" and receipt.get("stopReason") == "timeout":
                receipt["status"] = "timeout"
            with self.lock:
                current = self._read_snapshot(owner, execution_id)
                if current and json.loads(current[1]) == original:
                    with self._db() as db:
                        db.execute(
                            "UPDATE runs SET receipt=? WHERE owner=? AND id=?",
                            (json.dumps(receipt, allow_nan=False), owner, execution_id),
                        )
                elif current:
                    return json.loads(current[1])
            return receipt
        except (OSError, ValueError, TypeError):
            return original

    def result_path(self, owner, execution_id):
        name = hashlib.sha256(json.dumps([owner, execution_id]).encode()).hexdigest()
        return self.path.parent / self.path.stem / (name + ".json")

    def _file_workspace(self, owner, execution_id, bundle=None):
        from astronverse.scheduler.core.executor.managed_files import FileWorkspace

        return FileWorkspace(self.result_path(owner, execution_id).with_suffix(".files"), self.origin, bundle)

    def _cleanup_files(self, owner, execution_id):
        from astronverse.scheduler.core.executor.managed_files import FileWorkspace

        directory = self.result_path(owner, execution_id).with_suffix(".files")
        # Cleanup must not depend on a complete transfer manifest after a crash.
        try:
            FileWorkspace.cleanup_directory(directory)
        except (OSError, ValueError):
            pass  # A locked file must not invalidate a durable terminal receipt.

    def _change(self, owner, execution_id, **changes):
        _, receipt = self._read(owner, execution_id)
        with self.lock:
            row = self._read_snapshot(owner, execution_id)
            receipt = json.loads(row[1]) if row else None
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
            rows = db.execute("SELECT receipt FROM runs").fetchall()
        for (serialized,) in rows:
            receipt = json.loads(serialized)
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
                "fileTransferVersion": 1,
                "desktopProtocolVersion": 1,
                "riskProtocolVersion": 1,
                "busy": self.manager.status()
                or bool(self.active)
                or bool(self.recovering)
                or bool(self.cleaning)
                or self._unresolved_process(),
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
        _, receipt = self._read(owner, execution_id)
        if receipt is None:
            return {"error": "EXECUTION_NOT_FOUND", "clientId": self.client_id}
        if action == "cancel":
            cancel = False
            with self.lock:
                row = self._read_snapshot(owner, execution_id)
                receipt = json.loads(row[1]) if row else None
                if receipt is None:
                    return {"error": "EXECUTION_NOT_FOUND", "clientId": self.client_id}
                if command.get("runId") != receipt.get("runId"):
                    return {"error": "EXECUTION_TARGET_MISMATCH"}
                if receipt["status"] not in TERMINAL:
                    if not receipt["supportsCancel"]:
                        return {"error": "CANCEL_UNSUPPORTED"}
                    cancel = True
            if cancel:
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
        self._read(owner, execution_id)
        with self.lock:
            row = self._read_snapshot(owner, execution_id)
            previous, receipt = (row[0], json.loads(row[1])) if row else (None, None)
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
                **({"fileWorkflow": True} if payload.get("fileBundle") else {}),
            }
            if self.active or self.recovering or self.cleaning or self.manager.status() or self._unresolved_process():
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
        guard = None
        params = payload.get("params", {})
        try:
            _, receipt = self._read(owner, execution_id)
            if receipt["cancelRequested"]:
                self._change(owner, execution_id, status="cancelled")  # No process was launched.
                return

            if payload.get("desktopContract") is not None:
                from astronverse.scheduler.core.executor.managed_desktop import DesktopError, DesktopGuard

                if type(payload.get("executionTimeout")) is not int or not 1 <= payload["executionTimeout"] <= 3600:
                    raise DesktopError("DESKTOP_CONTRACT_INVALID")
                guard = DesktopGuard(payload["desktopContract"])
                guard.check(initial=True)

            if payload.get("fileBundle"):
                params = self._file_workspace(owner, execution_id, payload["fileBundle"]).prepare(params)

            def bind(instance):
                # ExecutorManager invokes this before starting the exact process.
                if guard:
                    try:
                        guard.check()
                    except DesktopError as error:
                        self._change(owner, execution_id, status="failed", error=error.code)
                        raise
                cancelled = False
                with self.lock:
                    row = self._read_snapshot(owner, execution_id)
                    receipt = json.loads(row[1]) if row else None
                    if receipt["cancelRequested"]:
                        cancelled = True
                    else:
                        self.active[(owner, execution_id)] = instance
                        receipt["runId"] = instance.exec_id
                        with self._db() as db:
                            db.execute(
                                "UPDATE runs SET receipt=? WHERE owner=? AND id=?",
                                (json.dumps(receipt, allow_nan=False), owner, execution_id),
                            )
                        path = self.result_path(owner, execution_id)
                        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                        instance.ins.set_param("managed_receipt", quote(str(path)))
                        if payload.get("riskContract"):
                            path.with_suffix(".risk.json").write_text(
                                json.dumps(payload["riskContract"], allow_nan=False), encoding="utf-8"
                            )
                            instance.ins.set_param("managed_risk", "y")
                            instance.ins.set_param("wait_tip_ws", "n")
                        if guard:
                            instance.ins.set_param("managed_desktop", "y")
                            # Managed forms have their own host. The designer's
                            # log overlay can steal focus and is not a prerequisite.
                            instance.ins.set_param("wait_tip_ws", "n")
                        if payload.get("fileBundle"):
                            instance.ins.set_param("managed_files", "y")
                if cancelled:
                    self._change(owner, execution_id, status="cancelled")
                    raise RuntimeError("Execution cancelled before process launch")

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
                    target=self._observe, args=(owner, execution_id, payload, instance, guard), daemon=True
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
                        for key, value in params.items()
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
        except Exception as error:
            if not observing:
                from astronverse.scheduler.core.executor.managed_desktop import DesktopError
                from astronverse.scheduler.core.executor.managed_files import FileTransferError

                if isinstance(error, (FileTransferError, DesktopError)):
                    self._change(owner, execution_id, status="failed", error=error.code)
                else:
                    self._change(
                        owner, execution_id, status="unknown", error="EXECUTION_START_UNCONFIRMED", supportsCancel=False
                    )
        finally:
            if not observing:
                try:
                    _, receipt = self._read(owner, execution_id)
                    if payload.get("fileBundle") and receipt["status"] in TERMINAL:
                        self._cleanup_files(owner, execution_id)
                finally:
                    with self.lock:
                        self.active.pop((owner, execution_id), None)

    def _observe(self, owner, execution_id, payload, executor, guard=None):
        from astronverse.scheduler.core.executor.executor import ExecuteStatus

        try:
            deadline = executor.launched_at + payload["executionTimeout"] if payload.get("executionTimeout") else None
            stop_reason = None
            stop_at = None
            desktop_error = None
            next_desktop_check = 0
            while True:
                # The concrete process handle is retained; never use stop_current/project.
                alive = executor.ins.is_alive()
                if not alive and executor.report_log_time < 0:
                    if desktop_error:
                        self._change(owner, execution_id, status="failed", error=desktop_error)
                    elif payload.get("riskContract"):
                        # Risk runs redact business values and diagnostics from
                        # reports. Their durable terminal receipt is authoritative.
                        if stop_reason:
                            self._change(owner, execution_id, status=stop_reason)
                        else:
                            _, current = self._read(owner, execution_id)
                            recovered = self._recover_receipt(owner, execution_id, current)
                            if recovered["status"] not in TERMINAL:
                                self._change(
                                    owner,
                                    execution_id,
                                    status="unknown",
                                    error="EXECUTION_OBSERVATION_FAILED",
                                    supportsCancel=False,
                                )
                    elif executor.execute_status == ExecuteStatus.SUCCESS:
                        try:
                            result = json_value(executor.execute_data)
                            # A workflow accepting secrets has no public result summary.
                            if payload.get("secretFields"):
                                result = None
                            if payload.get("fileBundle"):
                                workspace = self._file_workspace(owner, execution_id)
                                result = workspace.finish(result)
                                workspace.cleanup()
                            self._change(owner, execution_id, status="succeeded", result=result)
                        except Exception as error:
                            if not payload.get("fileBundle") and not isinstance(error, (TypeError, ValueError)):
                                raise
                            from astronverse.scheduler.core.executor.managed_files import FileTransferError

                            code = (
                                error.code
                                if isinstance(error, FileTransferError)
                                else ("FILE_TRANSFER_FAILED" if payload.get("fileBundle") else "UNSUPPORTED_RESULT")
                            )
                            self._change(owner, execution_id, status="failed", error=code)
                    elif stop_reason:
                        self._change(owner, execution_id, status=stop_reason)
                    elif executor.execute_status == ExecuteStatus.CANCEL:
                        self._change(owner, execution_id, status="cancelled")
                    else:
                        code = (
                            executor.execute_reason
                            if executor.execute_reason
                            in (
                                "UNSUPPORTED_RESULT",
                                "DESKTOP_HUMAN_UNAVAILABLE",
                                "RISK_OPERATION_DENIED",
                                "RISK_ARGUMENTS_DENIED",
                                "RISK_CODE_DENIED",
                                "RISK_CONTRACT_INVALID",
                                "RISK_AUDIT_FAILED",
                            )
                            else "EXECUTION_FAILED"
                        )
                        self._change(owner, execution_id, status="failed", error=code)
                    return
                if alive and stop_reason is None:
                    _, receipt = self._read(owner, execution_id)
                    if guard and time.monotonic() >= next_desktop_check:
                        from astronverse.scheduler.core.executor.managed_desktop import DesktopError

                        try:
                            guard.check()
                        except DesktopError as error:
                            desktop_error = error.code
                        next_desktop_check = time.monotonic() + 0.5
                    if (
                        desktop_error
                        or receipt["cancelRequested"]
                        or (deadline is not None and time.time() >= deadline)
                    ):
                        stop_reason = (
                            "failed" if desktop_error else ("cancelled" if receipt["cancelRequested"] else "timeout")
                        )
                        stop_at = time.monotonic()
                        self._change(
                            owner,
                            execution_id,
                            stopReason=stop_reason,
                            **({"desktopError": desktop_error} if desktop_error else {}),
                        )
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
            try:
                if payload.get("fileBundle") and not executor.ins.is_alive():
                    self._cleanup_files(owner, execution_id)
            finally:
                with self.lock:
                    self.active.pop((owner, execution_id), None)
