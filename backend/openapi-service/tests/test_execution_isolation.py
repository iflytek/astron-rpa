import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/test")
os.environ.setdefault("DATABASE_USERNAME", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.models.workflow import Execution
from app.routers.executions import get_execution as get_execution_route
from app.schemas import ResCode
from app.schemas.workflow import ExecutionCreate
from app.services.execution import ExecutionService


class AsyncSessionAdapter:
    """Minimal async facade over a real in-memory SQLAlchemy session."""

    def __init__(self, session):
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def commit(self):
        self.session.commit()

    async def rollback(self):
        self.session.rollback()


def empty_scalar_result():
    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    return result


@pytest.mark.asyncio
async def test_external_execution_lookup_filters_by_execution_and_user_id():
    db = AsyncMock()
    db.execute.return_value = empty_scalar_result()
    service = ExecutionService(db)

    execution = await service.get_execution("execution-owned-by-a", "user-b")

    assert execution is None
    statement = db.execute.await_args.args[0]
    compiled = statement.compile()
    assert "execution-owned-by-a" in compiled.params.values()
    assert "user-b" in compiled.params.values()
    assert "user_id" in str(statement.whereclause)


@pytest.mark.asyncio
async def test_user_cannot_read_or_cancel_another_users_execution():
    engine = create_engine("sqlite:///:memory:")
    Execution.__table__.create(engine)

    with Session(engine, expire_on_commit=False) as session:
        session.add(
            Execution(
                id="execution-owned-by-a",
                project_id="project-a",
                user_id="user-a",
                status="PENDING",
            )
        )
        session.commit()
        service = ExecutionService(AsyncSessionAdapter(session))

        assert await service.get_execution("execution-owned-by-a", "user-a") is not None
        assert await service.get_execution("execution-owned-by-a", "user-b") is None
        assert await service.cancel_execution("execution-owned-by-a", "user-b") is False

        stored_execution = session.get(Execution, "execution-owned-by-a")
        assert stored_execution.status == "PENDING"

    engine.dispose()


@pytest.mark.asyncio
async def test_cross_user_and_unknown_execution_have_the_same_404_response():
    service = AsyncMock()
    service.get_execution.return_value = None

    cross_user_response = Response()
    cross_user_body = await get_execution_route(
        response=cross_user_response,
        execution_id="execution-owned-by-a",
        user_id="user-b",
        service=service,
    )

    unknown_response = Response()
    unknown_body = await get_execution_route(
        response=unknown_response,
        execution_id="unknown-execution",
        user_id="user-b",
        service=service,
    )

    assert cross_user_response.status_code == 404
    assert unknown_response.status_code == 404
    assert cross_user_body.code == unknown_body.code == ResCode.ERR
    assert cross_user_body.data is unknown_body.data is None


@pytest.mark.asyncio
async def test_status_update_uses_internal_execution_lookup():
    db = AsyncMock()
    service = ExecutionService(db)
    updated_execution = MagicMock()
    service.get_execution_internal = AsyncMock(return_value=updated_execution)

    result = await service.update_execution_status("execution-1", "RUNNING")

    assert result is updated_execution
    service.get_execution_internal.assert_awaited_once_with("execution-1")


@pytest.mark.asyncio
async def test_create_execution_pins_authenticated_user_to_record():
    db = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    service = ExecutionService(db)

    execution = await service.create_execution(
        ExecutionCreate(project_id="project-1", params={"value": 1}),
        "authenticated-user",
    )

    assert execution.user_id == "authenticated-user"
    db.add.assert_called_once_with(execution)


@pytest.mark.asyncio
async def test_execute_workflow_does_not_forward_a_second_dispatch_identity(monkeypatch):
    db = AsyncMock()
    service = ExecutionService(db)
    execution = Execution(
        id="execution-1",
        project_id="project-1",
        user_id="authenticated-user",
        status="PENDING",
    )
    service.create_execution = AsyncMock(return_value=execution)
    service._run_workflow_with_new_session_sync = AsyncMock()
    monkeypatch.setattr("app.services.execution.asyncio.sleep", AsyncMock())

    await service.execute_workflow(
        ExecutionCreate(project_id="project-1"),
        "authenticated-user",
        wait=True,
        workflow_timeout=123,
    )

    service.create_execution.assert_awaited_once()
    assert service.create_execution.await_args.args[1] == "authenticated-user"
    service._run_workflow_with_new_session_sync.assert_awaited_once_with("execution-1", 123)


@pytest.mark.asyncio
async def test_background_runner_uses_identity_from_persisted_execution():
    db = AsyncMock()
    service = ExecutionService(db)
    execution = Execution(
        id="execution-1",
        project_id="project-1",
        user_id="recorded-user",
        status="PENDING",
    )
    service.get_execution_internal = AsyncMock(return_value=execution)
    service._execute_workflow_logic = AsyncMock()

    await service._run_workflow("execution-1", workflow_timeout=123)

    service.get_execution_internal.assert_awaited_once_with("execution-1")
    service._execute_workflow_logic.assert_awaited_once_with(execution)


@pytest.mark.asyncio
async def test_websocket_dispatch_uses_only_recorded_execution_identity(monkeypatch):
    db = AsyncMock()
    service = ExecutionService(db)
    service.update_execution_status = AsyncMock()
    websocket_service = MagicMock()

    async def reply_with_success(base_msg, timeout, callback):
        callback(MagicMock(data={"code": "0000"}))

    websocket_service.ws_manager.send_reply = AsyncMock(side_effect=reply_with_success)
    monkeypatch.setattr(
        "app.dependencies.get_ws_service",
        AsyncMock(return_value=websocket_service),
    )
    execution = Execution(
        id="execution-1",
        project_id="project-1",
        user_id="recorded-user",
        status="PENDING",
        parameters="{}",
        exec_position="EXECUTOR",
    )

    await service._execute_workflow_logic(execution)

    dispatched_message = websocket_service.ws_manager.send_reply.await_args.args[0]
    assert dispatched_message.send_uuid == "recorded-user"
    service.update_execution_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_websocket_dispatch_fails_closed_without_recorded_identity(monkeypatch):
    service = ExecutionService(AsyncMock())
    websocket_service = MagicMock()
    websocket_service.ws_manager.send_reply = AsyncMock()
    monkeypatch.setattr(
        "app.dependencies.get_ws_service",
        AsyncMock(return_value=websocket_service),
    )
    execution = Execution(
        id="execution-without-user",
        project_id="project-1",
        user_id=None,
        status="PENDING",
    )

    with pytest.raises(ValueError, match="has no authenticated user identity"):
        await service._execute_workflow_logic(execution)

    websocket_service.ws_manager.send_reply.assert_not_awaited()
