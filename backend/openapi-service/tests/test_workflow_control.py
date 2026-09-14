import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from starlette.applications import Starlette
from starlette.routing import Mount

from app.models.workflow import Execution, Workflow
from app.routers import streamable_mcp
from app.schemas.mcp import CONTROL_TOOLS
from app.security.mcp_auth import MCPAPIKeyAuthMiddleware
from app.services.execution import ExecutionService, _execution_tasks
from app.services.workflow_control import (
    WorkflowControlError,
    WorkflowControlService,
    validate_arguments,
    workflow_input_schema,
)


class AsyncSessionAdapter:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        self.session.close()

    async def close(self):
        self.session.close()

    def add(self, item):
        self.session.add(item)

    async def execute(self, statement):
        return self.session.execute(statement)

    async def flush(self):
        self.session.flush()

    async def refresh(self, item):
        self.session.refresh(item)

    async def commit(self):
        self.session.commit()

    async def rollback(self):
        self.session.rollback()


@pytest.fixture
def database():
    engine = create_engine("sqlite:///:memory:")
    Workflow.__table__.create(engine)
    Execution.__table__.create(engine)
    with Session(engine) as session:
        session.add_all(
            [
                Workflow(project_id="allowed", user_id="owner", name="Allowed", version=2, status=1, parameters="[]"),
                Workflow(project_id="disabled", user_id="owner", name="Disabled", version=1, status=0),
                Workflow(project_id="foreign", user_id="other", name="Other", version=1, status=1),
                Workflow(
                    project_id="alias", example_project_id="example", user_id="owner", name="Alias", version=1, status=1
                ),
                Execution(id="existing", project_id="allowed", user_id="owner", version=2, status="PENDING"),
            ]
        )
        session.commit()
    yield engine
    engine.dispose()


@pytest.mark.asyncio
async def test_list_get_and_query_use_real_user_and_release_filters(database):
    with Session(database) as db:
        service = WorkflowControlService(AsyncSessionAdapter(db))
        listed = await service.list_workflows("owner")
        assert {w["projectId"] for w in listed["workflows"]} == {"allowed", "alias"}
        assert "user_id" not in json.dumps(listed)
        assert (await service.get_workflow("allowed", "owner"))["version"] == 2
        assert (await service.get_execution("existing", "owner"))["status"] == "accepted"
        with pytest.raises(WorkflowControlError) as foreign:
            await service.get_execution("existing", "other")
        with pytest.raises(WorkflowControlError) as missing:
            await service.get_execution("missing", "other")
        assert foreign.value.code == missing.value.code == "EXECUTION_NOT_FOUND"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("project", "version", "error_code"),
    [
        ("foreign", None, "WORKFLOW_NOT_FOUND"),
        ("disabled", None, "WORKFLOW_NOT_FOUND"),
        ("missing", None, "WORKFLOW_NOT_FOUND"),
        ("example", None, "WORKFLOW_NOT_FOUND"),
        ("allowed", 1, "VERSION_NOT_ALLOWED"),
        ("allowed", 3, "VERSION_NOT_ALLOWED"),
    ],
)
async def test_unauthorized_start_does_not_create_or_dispatch(database, project, version, error_code):
    with Session(database) as db:
        service = WorkflowControlService(AsyncSessionAdapter(db))
        service.executions.execute_authorized_workflow = AsyncMock()
        with pytest.raises(WorkflowControlError) as error:
            await service.execute_workflow(project, "owner", {}, version)
        assert error.value.code == error_code
        service.executions.execute_authorized_workflow.assert_not_awaited()
        assert len(db.execute(select(Execution)).scalars().all()) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["disabled", "republished", "unversioned"])
async def test_query_rechecks_current_external_access_and_version(database, change):
    with Session(database) as db:
        if change == "disabled":
            db.get(Workflow, "allowed").status = 0
        elif change == "republished":
            db.get(Workflow, "allowed").version = 3
        else:
            db.get(Execution, "existing").version = None
        db.commit()
        service = WorkflowControlService(AsyncSessionAdapter(db))
        with pytest.raises(WorkflowControlError, match="Execution not found"):
            await service.get_execution("existing", "owner")


def test_scalar_schema_preserves_zero_defaults_and_rejects_boolean_numbers():
    workflow = Workflow(
        parameters=json.dumps(
            [
                {"varName": "count", "varType": "Int", "varDirection": 0, "varValue": 0},
                {"varName": "ratio", "varType": "Float", "varDirection": 0, "varValue": "0"},
                {"varName": "message", "varType": "Str", "varDirection": 0, "varValue": ""},
                {"varName": "output", "varType": "Str", "varDirection": 1},
            ]
        )
    )
    schema = workflow_input_schema(workflow)
    assert schema["required"] == ["message"]
    assert schema["properties"]["count"]["default"] == 0
    assert schema["properties"]["ratio"]["default"] == 0.0
    validate_arguments({"count": 0, "ratio": 0.0, "message": "ok"}, schema)
    for arguments in [{"count": True, "message": "ok"}, {"ratio": float("nan"), "message": "ok"}, {"extra": 1}]:
        with pytest.raises(WorkflowControlError, match="Arguments do not match"):
            validate_arguments(arguments, schema)


@pytest.mark.parametrize(
    "parameters",
    [
        "not-json",
        "null",
        "false",
        '[{"varDirection":0,"varType":"PATH","varName":"file"}]',
        '[{"varDirection":0,"varType":"Password","varName":"secret","varValue":"secret-value"}]',
        '{"type":"object","properties":{"x":{"type":"array"}}}',
        '{"type":"object","$ref":"https://example.invalid/schema"}',
        '[{"varDirection":0,"varType":"Int","varName":"n","varValue":1.5}]',
        '[{"varDirection":0,"varType":"Float","varName":"n","varValue":"nan"}]',
    ],
)
def test_unsupported_or_malformed_schema_fails_closed(parameters):
    with pytest.raises(WorkflowControlError) as error:
        workflow_input_schema(Workflow(parameters=parameters))
    assert error.value.code == "UNSUPPORTED_PARAMETERS"
    assert "secret-value" not in str(error.value)


@pytest.mark.parametrize(
    ("status", "result", "error", "expected_state", "expected_code"),
    [
        ("COMPLETED", {"code": "0000", "data": {"count": 0, "ratio": 1.5}}, None, "succeeded", None),
        ("FAILED", {"code": "5001", "msg": "secret-path", "data": "secret-value"}, None, "failed", "EXECUTION_FAILED"),
        ("FAILED", {}, "RPA client is offline or disconnected", "failed", "CLIENT_OFFLINE"),
        ("FAILED", {"code": "5001", "msg": "有任务在运行中"}, None, "failed", "CLIENT_BUSY"),
        ("UNKNOWN", {}, "secret-value", "unknown", "EXECUTION_RESULT_TIMEOUT"),
        ("CANCELLED", {}, None, "unknown", "EXECUTION_STATE_UNKNOWN"),
    ],
)
def test_execution_result_distinguishes_business_outcome_and_redacts_errors(
    status, result, error, expected_state, expected_code
):
    execution = Execution(
        id="e",
        project_id="p",
        version=1,
        status=status,
        result=json.dumps(result),
        error=error,
        parameters='{"password":"secret-value"}',
        start_time=datetime(2026, 1, 1),
        end_time=datetime(2026, 1, 2),
    )
    payload = WorkflowControlService.execution_result(execution)
    assert payload["status"] == expected_state
    assert payload["terminal"] is (expected_state in ("failed", "succeeded"))
    assert payload["supportsCancel"] is False
    assert "secret-" not in json.dumps(payload)
    if expected_code:
        assert payload["error"]["code"] == expected_code
    else:
        assert payload["result"] == {"count": 0, "ratio": 1.5}
    if expected_state == "unknown":
        assert payload["finishedAt"] is None


@pytest.mark.parametrize("result", [None, "invalid", "[]", "{}", '{"code":"5001"}'])
def test_completed_record_without_valid_success_reply_is_not_reported_as_success(result):
    with pytest.raises(WorkflowControlError) as error:
        WorkflowControlService.execution_result(Execution(status="COMPLETED", result=result))
    assert error.value.code == "RESULT_UNAVAILABLE"


@asynccontextmanager
async def mcp_session(manager, user_id):
    auth = MCPAPIKeyAuthMiddleware(manager.handle_request, AsyncMock(return_value=user_id))
    asgi = Starlette(routes=[Mount("/mcp", app=auth)])

    async with AsyncClient(transport=ASGITransport(app=asgi), headers={"Authorization": "Bearer test-key"}) as client:
        async with streamable_http_client(
            "http://test/mcp/",
            terminate_on_close=False,
            http_client=client,
        ) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session


@pytest.mark.asyncio
async def test_real_mcp_async_start_disconnect_and_query_share_one_execution(database, monkeypatch):
    monkeypatch.setattr("sse_starlette.sse.AppStatus.should_exit_event", None)

    def session_factory():
        return AsyncSessionAdapter(Session(database, expire_on_commit=False))

    monkeypatch.setattr(streamable_mcp, "AsyncSessionLocal", session_factory)
    monkeypatch.setattr("app.services.execution.AsyncSessionLocal", session_factory)
    collision = types.Tool(name="astron_workflow_execute", inputSchema={"type": "object"})
    monkeypatch.setattr(streamable_mcp.tools_config, "get_tools_for_user", AsyncMock(return_value=[collision]))
    started, finish = asyncio.Event(), asyncio.Event()
    dispatches = []

    async def dispatch(worker, record):
        dispatches.append(record.id)
        started.set()
        await finish.wait()
        await worker.update_execution_status(record.id, "COMPLETED", result={"code": "0000", "data": {"value": 0}})

    monkeypatch.setattr(ExecutionService, "_execute_workflow_logic", dispatch)
    manager = StreamableHTTPSessionManager(streamable_mcp.app, stateless=True, json_response=False)
    async with manager.run():
        async with mcp_session(manager, "owner") as session:
            listed = await session.list_tools()
            assert {t.name for t in listed.tools} == set(CONTROL_TOOLS)
            assert len(listed.tools) == 4  # Reserved names cannot shadow fixed tools.
            invalid = await session.call_tool(
                "astron_workflow_execute", {"projectId": "allowed", "userId": "secret-value"}
            )
            assert invalid.isError
            assert "secret-value" not in invalid.model_dump_json()
            assert not dispatches
            started_result = await session.call_tool("astron_workflow_execute", {"projectId": "allowed"})
            assert not started_result.isError
            execution_id = started_result.structuredContent["executionId"]
            assert started_result.structuredContent["status"] == "accepted"
            await asyncio.wait_for(started.wait(), timeout=2)
            assert not finish.is_set()
            pending = await session.call_tool("astron_execution_get", {"executionId": execution_id})
            assert pending.structuredContent["terminal"] is False
        # The caller has stopped waiting and closed its MCP connection.
        assert dispatches == [execution_id]
        async with mcp_session(manager, "other") as session:
            denied = await session.call_tool("astron_execution_get", {"executionId": execution_id})
            assert denied.isError
            assert denied.structuredContent["error"]["code"] == "EXECUTION_NOT_FOUND"
        finish.set()
        await asyncio.wait_for(asyncio.gather(*list(_execution_tasks)), timeout=2)
        async with mcp_session(manager, "owner") as session:
            completed = await session.call_tool("astron_execution_get", {"executionId": execution_id})
            assert completed.structuredContent["status"] == "succeeded"
            assert completed.structuredContent["result"] == {"value": 0}
            assert json.loads(completed.content[0].text) == completed.structuredContent
        assert dispatches == [execution_id]


@pytest.mark.asyncio
async def test_worker_result_timeout_is_unknown_and_does_not_claim_to_stop_client(database, monkeypatch):
    monkeypatch.setattr(
        "app.services.execution.AsyncSessionLocal",
        lambda: AsyncSessionAdapter(Session(database, expire_on_commit=False)),
    )

    async def timeout(worker, record):
        raise TimeoutError

    monkeypatch.setattr(ExecutionService, "_execute_workflow_logic", timeout)
    service = ExecutionService(AsyncSessionAdapter(Session(database)))
    await service._run_workflow_with_new_session("existing", workflow_timeout=1)
    with Session(database) as db:
        record = db.get(Execution, "existing")
        assert record.status == "UNKNOWN"
        assert record.end_time is None
        assert "may still be running" in record.error


@pytest.mark.asyncio
async def test_mcp_internal_errors_do_not_expose_database_or_argument_details(database, monkeypatch, caplog):
    monkeypatch.setattr("sse_starlette.sse.AppStatus.should_exit_event", None)
    monkeypatch.setattr(
        streamable_mcp, "AsyncSessionLocal", lambda: AsyncSessionAdapter(Session(database, expire_on_commit=False))
    )
    monkeypatch.setattr(streamable_mcp.tools_config, "get_tools_for_user", AsyncMock(return_value=[]))
    monkeypatch.setattr(
        WorkflowControlService, "get_execution", AsyncMock(side_effect=RuntimeError("SQL parameters: private-value"))
    )
    manager = StreamableHTTPSessionManager(streamable_mcp.app, stateless=True, json_response=False)
    async with manager.run(), mcp_session(manager, "owner") as session:
        result = await session.call_tool("astron_execution_get", {"executionId": "existing"})
    assert result.isError
    assert result.structuredContent["error"]["code"] == "INTERNAL_ERROR"
    assert "private-value" not in result.model_dump_json()
    assert "private-value" not in caplog.text
