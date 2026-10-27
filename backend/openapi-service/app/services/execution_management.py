"""Durable dispatch and reconciliation for the shared execution service.

Only NEW receipts can send start, once, after a transactional claim. SENT
receipts can only query/cancel the bound Client; absence is never a retry signal.
"""

import asyncio
import hashlib
import json
from datetime import UTC, datetime

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from sqlalchemy import select, update

from app.models.workflow import Execution
from app.security.workflow_authorization import WorkflowAccessError
from app.services.workflow_schema import validate_json_value

TERMINAL = ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT")
CLIENT_STATES = {
    "accepted": "PENDING",
    "running": "RUNNING",
    "succeeded": "COMPLETED",
    "failed": "FAILED",
    "cancelled": "CANCELLED",
    "timeout": "TIMEOUT",
    "unknown": "UNKNOWN",
}
ERRORS = {
    "RISK_OPERATION_DENIED",
    "RISK_ARGUMENTS_DENIED",
    "RISK_CODE_DENIED",
    "RISK_AUDIT_FAILED",
    "RISK_CONTRACT_INVALID",
    "CLIENT_BUSY",
    "CLIENT_OFFLINE",
    "EXECUTION_FAILED",
    "UNSUPPORTED_RESULT",
    "CLIENT_RESTARTED",
    "EXECUTION_START_UNCONFIRMED",
    "EXECUTION_OBSERVATION_FAILED",
    "EXECUTION_NOT_FOUND",
    "EXECUTION_TARGET_MISMATCH",
    "CANCEL_UNSUPPORTED",
    "DISPATCH_EXPIRED",
    "STOP_UNCONFIRMED",
    "FILE_TRANSFER_FAILED",
    "FILE_OUTPUT_INVALID",
    "OFFICE_UNAVAILABLE",
    "DESKTOP_UNAVAILABLE",
    "DESKTOP_LOCKED",
    "DESKTOP_SESSION_CHANGED",
    "DESKTOP_RESOLUTION_MISMATCH",
    "DESKTOP_SOFTWARE_UNAVAILABLE",
    "DESKTOP_POPUP_BLOCKED",
    "DESKTOP_CONTRACT_INVALID",
    "DESKTOP_HUMAN_UNAVAILABLE",
}


def _validate_data_result(record, value):
    """Validate a JSON-data result against the frozen execution contract."""
    if not record.data_contract:
        return True
    try:
        contract = json.loads(record.data_contract)
        if not isinstance(contract, dict) or contract.get("version") != 1:
            return False
        limits = contract.get("limits")
        validate_json_value(value, limits=limits)
        schema = contract.get("outputSchema")
        if contract.get("fileContract"):
            from app.services.office_file import validate_file_result

            if not validate_file_result(record, contract["fileContract"], value):
                return False
        if schema is not None:
            Draft202012Validator(schema).validate(value)
        return True
    except (
        KeyError,
        TypeError,
        ValueError,
        RecursionError,
        json.JSONDecodeError,
        SchemaError,
        ValidationError,
        WorkflowAccessError,
    ):
        return False


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


async def request(user_id, data, timeout=5):
    from app.dependencies import get_ws_service

    service = await get_ws_service()
    return await service.ws_manager.execution_request(user_id, data, timeout)


async def capabilities(user_id, *, required=False):
    """Probe without dispatching; required features must preserve transport errors."""
    try:
        reply = await request(user_id, {"action": "capabilities"}, timeout=2)
        if isinstance(reply, dict) and reply.get("protocol") == 1 and isinstance(reply.get("clientId"), str):
            return reply
    except ConnectionError:
        if required:
            raise WorkflowAccessError("CLIENT_OFFLINE", "RPA client is offline or disconnected") from None
    except (OSError, TimeoutError):
        if required:
            raise WorkflowAccessError(
                "CLIENT_CAPABILITY_UNCONFIRMED", "Client execution capabilities could not be confirmed"
            ) from None
    return None


def instant(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Client timestamps must include timezone")
    return parsed.astimezone(UTC).replace(tzinfo=None)


async def apply_receipt(service, record, receipt):
    if (
        not isinstance(receipt, dict)
        or receipt.get("protocol") != 1
        or receipt.get("executionId") != record.id
        or receipt.get("clientId") != record.client_id
    ):
        return False
    run_id = receipt.get("runId")
    if record.run_id and run_id != record.run_id:
        return False
    status = CLIENT_STATES.get(receipt.get("status"))
    if status is None:
        return False
    started = instant(receipt.get("startedAt"))
    finished = instant(receipt.get("finishedAt"))
    if started and finished and finished < started:
        return False
    if status == "RUNNING" and (not run_id or started is None):
        return False
    if status in TERMINAL and finished is None:
        return False
    # Cancellation before launch is valid: the durable Client receipt proves zero start.
    if status in ("COMPLETED", "TIMEOUT") and (not run_id or started is None):
        return False
    raw_result = receipt.get("result")
    if record.data_contract and status in TERMINAL and status != "COMPLETED":
        # Failure/cancellation receipts have no JSON-data business result.
        raw_result = None
    try:
        json.dumps(raw_result, allow_nan=False)
    except (TypeError, ValueError, RecursionError):
        return False
    code = receipt.get("error")
    if status == "COMPLETED" and not _validate_data_result(record, raw_result):
        # Do not persist or expose a result that violates the frozen contract.
        status = "FAILED"
        code = "UNSUPPORTED_RESULT"
        raw_result = None
    values = {
        "status": status,
        "run_id": run_id,
        "error": code if code in ERRORS else None,
        "cancel_supported": receipt.get("supportsCancel") is True,
    }
    if started:
        values["started_at"] = record.started_at or started
    if status in TERMINAL:
        values.update(end_time=finished, dispatch_state="DONE")
        values["result"] = json.dumps(
            {"code": "0000" if status == "COMPLETED" else "5001", "data": None if record.secret_fields else raw_result},
            allow_nan=False,
        )
        # Inputs are needed only until the one permitted start. Keep a redacted
        # record for compatibility; the immutable request hash supports retries.
        params = record.get_parameters_as_dict()
        for key in json.loads(record.secret_fields or "[]"):
            if key in params:
                params[key] = "[REDACTED]"
        values["parameters"] = json.dumps(params, allow_nan=False)
    allowed = ["PENDING", "UNKNOWN"] if status == "PENDING" else ["PENDING", "RUNNING", "UNKNOWN"]
    statement = update(Execution).where(
        Execution.id == record.id,
        Execution.protocol == 1,
        Execution.client_id == record.client_id,
        Execution.status.in_(allowed),
    )
    if record.run_id:
        statement = statement.where(Execution.run_id == record.run_id)
    else:
        statement = statement.where(Execution.run_id.is_(None) | (Execution.run_id == run_id))
    result = await service.db.execute(statement.values(**values))
    await service.db.commit()
    await service.db.refresh(record)
    if result.rowcount and status in TERMINAL:
        from app.services.observability import event, execution_finished, increment

        execution_finished(status, code, (finished - started).total_seconds() if started and finished else None)
        if code == "CLIENT_BUSY":
            increment("astron_client_busy_total")
        event(
            "execution_terminal",
            execution_id=record.id,
            run_id=record.run_id,
            outcome=status,
            error_code=code if code in ERRORS else None,
        )
    if record.status in TERMINAL and record.data_contract and json.loads(record.data_contract).get("fileContract"):
        from app.services.integration_files import store

        store().revoke(record.id)
    return bool(result.rowcount)


async def reconcile(service, record):
    if record.status in TERMINAL:
        return
    command = {"action": "get", "clientId": record.client_id, "executionId": record.id}
    if record.dispatch_state == "NEW":
        age = (datetime.now(UTC).replace(tzinfo=None) - record.start_time).total_seconds()
        if age > 30:
            await service.update_execution_status(record.id, "FAILED", error="DISPATCH_EXPIRED")
            return
        claimed = await service.db.execute(
            update(Execution)
            .where(Execution.id == record.id, Execution.dispatch_state == "NEW", Execution.status == "PENDING")
            .values(dispatch_state="SENT")
        )
        await service.db.commit()
        if claimed.rowcount:
            # Only the atomic NEW -> SENT claim creates a file bundle. Later
            # reconcile passes observe SENT and query the existing execution,
            # so they do not accumulate additional transfer grants.
            bundle = None
            contract = json.loads(record.data_contract or "{}")
            if contract.get("fileContract"):
                from app.services.office_file import execution_bundle

                try:
                    bundle = execution_bundle(record, contract["fileContract"])
                except WorkflowAccessError:
                    from app.services.integration_files import store

                    store().revoke(record.id)
                    await service.update_execution_status(record.id, "FAILED", error="FILE_TRANSFER_FAILED")
                    return
            command.update(
                action="start",
                payload={
                    "projectId": record.project_id,
                    "version": record.version,
                    "params": record.get_parameters_as_dict(),
                    "executionTimeout": record.execution_timeout,
                    "recordingConfig": record.recording_config,
                    "secretFields": json.loads(record.secret_fields or "[]"),
                    **({"fileBundle": bundle} if bundle else {}),
                    **({"desktopContract": contract["desktopContract"]} if contract.get("desktopContract") else {}),
                    **({"riskContract": contract["riskContract"]} if contract.get("riskContract") else {}),
                },
            )
    try:
        receipt = await request(record.user_id, command)
        if not await apply_receipt(service, record, receipt):
            await service.update_execution_status(record.id, "UNKNOWN", error="EXECUTION_OBSERVATION_FAILED")
            return
        if record.cancel_requested and record.status not in TERMINAL:
            receipt = await request(
                record.user_id,
                {"action": "cancel", "clientId": record.client_id, "executionId": record.id, "runId": record.run_id},
            )
            await apply_receipt(service, record, receipt)
    except (OSError, TimeoutError, ValueError, TypeError):
        # No automatic start retry after the claim, including failure before send.
        await service.update_execution_status(record.id, "UNKNOWN", error="EXECUTION_OBSERVATION_FAILED")


async def run_managed(service, record):
    while record.status not in TERMINAL:
        await reconcile(service, record)
        if record.status == "UNKNOWN":
            return  # Periodic recovery owns future observation, without a hot loop.
        await asyncio.sleep(0.5)
        await service.db.refresh(record)


async def recover_executions():
    from app.database import AsyncSessionLocal
    from app.services.execution import ExecutionService, _execution_task_done, _execution_tasks

    cursor = ""
    observing = set()
    while True:
        try:
            if len(observing) >= 32:
                await asyncio.sleep(2)
                continue
            async with AsyncSessionLocal() as db:
                ids = (
                    (
                        await db.execute(
                            select(Execution.id)
                            .where(Execution.protocol == 1, Execution.status.not_in(TERMINAL), Execution.id > cursor)
                            .order_by(Execution.id)
                            .limit(32 - len(observing))
                        )
                    )
                    .scalars()
                    .all()
                )
            cursor = ids[-1] if ids else ""
            active = {task.get_name() for task in _execution_tasks}
            for execution_id in ids:
                name = f"execution-{execution_id}"
                if name in active:
                    continue

                async def observe(identifier=execution_id):
                    async with AsyncSessionLocal() as db:
                        service = ExecutionService(db)
                        record = await service.get_execution_internal(identifier)
                        if record:
                            await reconcile(service, record)

                task = asyncio.create_task(observe(), name=name)
                observing.add(task)
                task.add_done_callback(observing.discard)
                _execution_tasks.add(task)
                task.add_done_callback(_execution_task_done)
        except Exception:
            from app.logger import get_logger

            get_logger(__name__).error("Execution recovery scan unavailable")
        await asyncio.sleep(2)
