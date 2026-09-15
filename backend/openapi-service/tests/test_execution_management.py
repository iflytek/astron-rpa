import asyncio
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.workflow import Execution, Workflow
from app.schemas.workflow import ExecutionCreate
from app.security.workflow_authorization import WorkflowAccessError, external_execution_dict
from app.services import execution_management as management
from app.services.execution import ExecutionService, _execution_tasks
from app.services.workflow_control import WorkflowControlService
from tests.test_workflow_control import AsyncSessionAdapter


@pytest.fixture
def store(tmp_path, monkeypatch):
    engine = create_engine("sqlite:///" + str(tmp_path / "executions.db"))
    Workflow.__table__.create(engine)
    Execution.__table__.create(engine)
    with Session(engine) as db:
        db.add_all(
            [
                Workflow(
                    project_id="project",
                    user_id="owner",
                    version=1,
                    status=1,
                    name="Project",
                    parameters=json.dumps({"type": "object", "properties": {"value": {"type": "integer"}}}),
                )
            ]
        )
        db.commit()

    def factory():
        return AsyncSessionAdapter(Session(engine, expire_on_commit=False))

    monkeypatch.setattr("app.services.execution.AsyncSessionLocal", factory)
    monkeypatch.setattr(
        management,
        "request",
        AsyncMock(return_value={"protocol": 1, "clientId": "client", "supportsCancel": True}),
    )
    # Acceptance/idempotency tests isolate the durable transaction from observation.
    monkeypatch.setattr(ExecutionService, "_run_workflow", AsyncMock())
    yield engine, factory
    engine.dispose()


@pytest.mark.asyncio
async def test_concurrent_duplicate_survives_new_sessions_and_reauthorizes(store, monkeypatch):
    engine, factory = store

    async def capability(*_, **_kwargs):
        await asyncio.sleep(0.01)  # Both requests pass the initial absence check.
        return {"protocol": 1, "clientId": "client", "supportsCancel": True}

    monkeypatch.setattr(management, "capabilities", capability)
    data = ExecutionCreate(project_id="project", params={"value": 0}, idempotency_key="stable-key")

    async def accept(request=data):
        async with factory() as db:
            return await ExecutionService(db).execute_authorized_workflow(request, "owner", wait=False)

    first, second = await asyncio.gather(accept(), accept())
    assert first.id == second.id
    assert (await accept()).id == first.id
    with pytest.raises(WorkflowAccessError, match="another request"):
        await accept(data.model_copy(update={"params": {"value": 1}}))
    with Session(engine) as db:
        assert len(db.execute(select(Execution)).scalars().all()) == 1
        db.get(Workflow, "project").version = 2
        db.commit()
    with pytest.raises(WorkflowAccessError):
        await accept()
    await asyncio.gather(*list(_execution_tasks))


def receipt(record, state="running", **changes):
    stamp = datetime.now(UTC).isoformat()
    return {
        "protocol": 1,
        "executionId": record.id,
        "clientId": "client",
        "runId": "run-1",
        "status": state,
        "startedAt": stamp,
        "finishedAt": stamp if state in ("succeeded", "cancelled", "timeout", "failed") else None,
        "result": {"value": 0},
        "supportsCancel": True,
        **changes,
    }


async def accepted(factory):
    async with factory() as db:
        record = await ExecutionService(db).execute_authorized_workflow(
            ExecutionCreate(project_id="project", params={"value": 0}), "owner", wait=False
        )
        return record.id


@pytest.mark.asyncio
@pytest.mark.parametrize("crash", ["before_send", "after_accept", "after_result"])
async def test_claimed_execution_only_reconciles_after_crash(store, monkeypatch, crash):
    _, factory = store
    execution_id = await accepted(factory)
    sent = []

    async def dropped(user, command, timeout=5):
        sent.append(command["action"])
        raise TimeoutError

    monkeypatch.setattr(management, "request", dropped)
    async with factory() as db:
        service = ExecutionService(db)
        record = await service.get_execution_internal(execution_id)
        if crash == "before_send":
            record.dispatch_state = "SENT"
            await db.commit()
        else:
            await management.reconcile(service, record)
        assert record.dispatch_state == "SENT"

    async def recover(user, command, timeout=5):
        sent.append(command["action"])
        if crash == "before_send":
            return {"error": "EXECUTION_NOT_FOUND"}
        return receipt(record, "succeeded" if crash == "after_result" else "running")

    monkeypatch.setattr(management, "request", recover)
    async with factory() as db:
        service = ExecutionService(db)
        record = await service.get_execution_internal(execution_id)
        await management.reconcile(service, record)
        assert (
            record.status == {"before_send": "UNKNOWN", "after_accept": "RUNNING", "after_result": "COMPLETED"}[crash]
        )
    assert sent.count("start") == (0 if crash == "before_send" else 1)
    assert sent[-1] == "get"
    await asyncio.gather(*list(_execution_tasks))


@pytest.mark.asyncio
async def test_receipt_binding_atomic_terminals_cancel_and_timeouts(store):
    _, factory = store
    execution_id = await accepted(factory)
    async with factory() as db:
        service = ExecutionService(db)
        record = await service.get_execution_internal(execution_id)
        assert not await management.apply_receipt(service, record, receipt(record, clientId="other"))
        assert not await management.apply_receipt(service, record, receipt(record, executionId=str(uuid4())))
        assert not await management.apply_receipt(service, record, receipt(record, startedAt=None))
        assert await management.apply_receipt(service, record, receipt(record))
        assert not await management.apply_receipt(service, record, receipt(record, runId="next-run"))
        with pytest.raises(WorkflowAccessError):
            await service.request_cancellation(record.id, "other")
        pending = await service.request_cancellation(record.id, "owner")
        assert pending.cancel_requested
        assert pending.status == "RUNNING"
        assert await management.apply_receipt(service, record, receipt(record, "succeeded"))
        assert not await management.apply_receipt(service, record, receipt(record, "cancelled"))
        await service.update_execution_status(record.id, "UNKNOWN")
        await db.refresh(record)
        assert record.status == "COMPLETED"
        assert (await service.request_cancellation(record.id, "owner")).status == "COMPLETED"
    await asyncio.gather(*list(_execution_tasks))


@pytest.mark.asyncio
async def test_timeout_requires_stop_receipt_and_secret_inputs_are_not_public(store):
    _, factory = store
    execution_id = await accepted(factory)
    async with factory() as db:
        service = ExecutionService(db)
        record = await service.get_execution_internal(execution_id)
        record.secret_fields = '["credential"]'
        record.parameters = '{"credential":"private-value"}'
        await db.commit()
        assert "private-value" not in json.dumps(external_execution_dict(record), default=str)
        assert not await management.apply_receipt(service, record, receipt(record, "timeout", finishedAt=None))
        assert record.status == "PENDING"
        assert await management.apply_receipt(service, record, receipt(record, "timeout"))
        snapshot = WorkflowControlService.execution_result(record)
        assert snapshot["terminal"]
        assert snapshot["status"] == "timeout"
        assert "private-value" not in record.parameters
    await asyncio.gather(*list(_execution_tasks))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("prop", "value"), [({"type": "boolean"}, False), ({"type": "string", "writeOnly": True}, "private")]
)
async def test_legacy_client_cannot_receive_managed_json_or_secrets(store, monkeypatch, prop, value):
    engine, factory = store
    monkeypatch.setattr(management, "capabilities", AsyncMock(return_value=None))
    with Session(engine) as db:
        db.get(Workflow, "project").parameters = json.dumps({"type": "object", "properties": {"value": prop}})
        db.commit()
    async with factory() as db:
        with pytest.raises(WorkflowAccessError, match="execution-management Client"):
            await ExecutionService(db).execute_authorized_workflow(
                ExecutionCreate(project_id="project", params={"value": value}), "owner", wait=False
            )
    with Session(engine) as db:
        assert db.execute(select(Execution)).scalars().all() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("feature", ["idempotency", "deadline", "json", "secret"])
@pytest.mark.parametrize(
    ("failure", "code"),
    [
        (ConnectionError, "CLIENT_OFFLINE"),
        (TimeoutError, "CLIENT_CAPABILITY_UNCONFIRMED"),
        (OSError, "CLIENT_CAPABILITY_UNCONFIRMED"),
        (None, "CLIENT_PROTOCOL_UNSUPPORTED"),
    ],
)
async def test_required_capability_errors_do_not_create_or_dispatch(store, monkeypatch, feature, failure, code):
    engine, factory = store
    options = {}
    value = 0
    prop = {"type": "integer"}
    if feature == "idempotency":
        options["idempotency_key"] = "stable-key"
    elif feature == "deadline":
        options["execution_timeout"] = 5
    elif feature == "json":
        prop, value = {"type": "boolean"}, False
    else:
        prop, value = {"type": "string", "writeOnly": True}, "private-input"
    with Session(engine) as db:
        db.get(Workflow, "project").parameters = json.dumps({"type": "object", "properties": {"value": prop}})
        db.commit()
    probe = (
        AsyncMock(side_effect=failure("private-probe-detail")) if failure else AsyncMock(return_value={"protocol": 0})
    )
    monkeypatch.setattr(management, "request", probe)
    async with factory() as db:
        with pytest.raises(WorkflowAccessError) as error:
            await ExecutionService(db).execute_authorized_workflow(
                ExecutionCreate(project_id="project", params={"value": value}, **options), "owner", wait=False
            )
    assert error.value.code == code
    assert "private" not in str(error.value)
    probe.assert_awaited_once_with("owner", {"action": "capabilities"}, timeout=2)
    ExecutionService._run_workflow.assert_not_awaited()
    with Session(engine) as db:
        assert db.execute(select(Execution)).scalars().all() == []


@pytest.mark.asyncio
async def test_existing_idempotent_execution_is_available_while_client_offline(store, monkeypatch):
    engine, factory = store
    data = ExecutionCreate(project_id="project", params={"value": 0}, idempotency_key="stable-key")
    async with factory() as db:
        first = await ExecutionService(db).execute_authorized_workflow(data, "owner", wait=False)
    probe = AsyncMock(side_effect=ConnectionError("CLIENT_OFFLINE"))
    monkeypatch.setattr(management, "request", probe)
    async with factory() as db:
        again = await ExecutionService(db).execute_authorized_workflow(data, "owner", wait=False)
    assert again.id == first.id
    probe.assert_not_awaited()
    with Session(engine) as db:
        assert len(db.execute(select(Execution)).scalars().all()) == 1
    await asyncio.gather(*list(_execution_tasks))


@pytest.mark.asyncio
async def test_offline_discovery_and_legacy_scalar_acceptance_keep_compatibility(store, monkeypatch):
    _, factory = store
    monkeypatch.setattr(management, "request", AsyncMock(side_effect=ConnectionError("CLIENT_OFFLINE")))
    async with factory() as db:
        detail = await WorkflowControlService(db).get_workflow("project", "owner")
        assert detail["supportsCancel"] is False
        record = await ExecutionService(db).execute_authorized_workflow(
            ExecutionCreate(project_id="project", params={"value": 0}), "owner", wait=False
        )
        assert record.protocol != 1
    await asyncio.gather(*list(_execution_tasks))


@pytest.mark.asyncio
@pytest.mark.parametrize("age", [0, 31])
async def test_unclaimed_dispatch_recovers_once_or_expires_without_dispatch(store, monkeypatch, age):
    _, factory = store
    execution_id = await accepted(factory)
    sent = []

    async def client_reply(user, command, timeout=5):
        sent.append(command["action"])
        return receipt(record)

    monkeypatch.setattr(management, "request", client_reply)
    async with factory() as db:
        service = ExecutionService(db)
        record = await service.get_execution_internal(execution_id)
        record.start_time = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=age)
        record.secret_fields = '["credential"]'
        record.parameters = '{"credential":"private-value"}'
        await db.commit()
    async with factory() as db:
        service = ExecutionService(db)
        record = await service.get_execution_internal(execution_id)
        await management.reconcile(service, record)
        await management.reconcile(service, record)
        if age:
            await db.refresh(record)
            assert sent == []
            assert record.status == "FAILED"
            assert record.error == "DISPATCH_EXPIRED"
            assert "private-value" not in record.parameters
        else:
            assert sent == ["start", "get"]
            assert record.status == "RUNNING"
    await asyncio.gather(*list(_execution_tasks))
