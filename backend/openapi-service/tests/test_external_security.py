"""Cross-transport security contracts using real models and MCP/REST routers."""

import json
from contextlib import asynccontextmanager
from functools import lru_cache
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount

from app import database as database_module
from app.database import get_db
from app.dependencies import get_user_id_from_api_key, get_user_id_with_fallback
from app.main import app
from app.models.api_key import OpenAPIDB
from app.models.workflow import Execution, Workflow
from app.redis import get_redis
from app.routers import streamable_mcp
from app.schemas.api_key import ApiKeyCreate
from app.security.api_key import validate_api_key
from app.security.mcp_auth import MCPAPIKeyAuthMiddleware
from app.security.workflow_authorization import WorkflowAccessError
from app.services.api_key import ApiKeyService
from app.services.execution import ExecutionService
from app.services.streamable_mcp import ToolsConfig
from app.services.workflow_control import WorkflowControlService
from app.utils.api_key import APIKeyUtils
from tests.test_workflow_control import AsyncSessionAdapter


@lru_cache
def hashed(key):
    return APIKeyUtils.hash_api_key(key)


@pytest.fixture
def security_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    for model in (OpenAPIDB, Workflow, Execution):
        model.__table__.create(engine)
    with Session(engine) as session:
        for key, user, active in [("owner-key", "owner", 1), ("other-key", "other", 1), ("revoked-key", "owner", 0)]:
            session.add(OpenAPIDB(name=key, user_id=user, prefix=key[:8], api_key=hashed(key), is_active=active))
        for project, user, enabled, version in [
            ("allowed", "owner", 1, 2),
            ("disabled", "owner", 0, 2),
            ("foreign", "other", 1, 2),
            ("unpublished", "owner", 1, 0),
        ]:
            session.add(
                Workflow(
                    project_id=project,
                    user_id=user,
                    status=enabled,
                    version=version,
                    name=project,
                    english_name=project,
                    parameters="[]",
                )
            )
            session.add(Execution(id=project, project_id=project, user_id=user, version=version, status="PENDING"))
        session.add(Execution(id="old-release", project_id="allowed", user_id="owner", version=1, status="PENDING"))
        session.commit()

    def factory():
        return AsyncSessionAdapter(Session(engine, expire_on_commit=False))

    monkeypatch.setattr(database_module, "AsyncSessionLocal", factory)
    monkeypatch.setattr(streamable_mcp, "AsyncSessionLocal", factory)
    monkeypatch.setattr("app.services.execution.AsyncSessionLocal", factory)

    async def db_override():
        async with factory() as db:
            yield db
            await db.commit()

    async def redis_override():
        yield None

    app.dependency_overrides[get_db] = db_override
    app.dependency_overrides[get_redis] = redis_override
    yield engine, factory
    app.dependency_overrides.clear()
    engine.dispose()


@asynccontextmanager
async def rest_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


def request(headers):
    return Request(
        {
            "type": "http",
            "headers": [(k.lower().encode(), v.encode()) for k, v in headers],
            "query_string": b"",
            "method": "GET",
            "path": "/",
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("headers", "query", "expected"),
    [
        ([], "", 401),
        ([("Authorization", "Bearer owner-key")], "", 200),
        ([("X-API-Key", "owner-key")], "", 200),
        ([("Authorization", "Bearer revoked-key")], "", 401),
        ([("Authorization", "Bearer unknown")], "", 401),
        ([("Authorization", "Basic owner-key")], "", 401),
        ([("Authorization", "")], "", 401),
        ([("X-API-Key", "")], "", 401),
        ([("Authorization", "Bearer owner-key"), ("X-API-Key", "owner-key")], "", 401),
        ([("Authorization", "Bearer owner-key"), ("Authorization", "Bearer owner-key")], "", 401),
        ([("X-API-Key", "owner-key"), ("X-API-Key", "other-key")], "", 401),
        ([], "?key=owner-key", 401),
        ([("Authorization", "Bearer owner-key")], "?key=owner-key", 401),
    ],
)
async def test_rest_and_mcp_share_credential_rules(security_db, headers, query, expected):
    async with rest_client() as client:
        response = await client.get("/executions/get" + query, headers=headers)

    async def authenticated(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = MCPAPIKeyAuthMiddleware(authenticated, ToolsConfig().get_uid_from_raw_key)
    async with AsyncClient(transport=ASGITransport(app=middleware), base_url="http://test") as client:
        mcp_response = await client.post("/mcp" + query, headers=headers)
    assert response.status_code == mcp_response.status_code == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("authorization", ["", "Basic owner-key", "Bearer bad", "Bearer revoked-key"])
async def test_invalid_key_never_falls_back_to_forged_identity(security_db, authorization):
    _, factory = security_db
    async with factory() as db:
        with pytest.raises(HTTPException) as error:
            await get_user_id_with_fallback(request([("Authorization", authorization)]), db, "owner", "owner")
        assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_keys_override_caller_identity_and_management_rejects_api_key(security_db):
    async with rest_client() as client:
        headers = {"Authorization": "Bearer other-key", "X-User-Id": "owner", "user_id": "owner"}
        result = await client.get("/workflows/get", headers=headers)
        assert {w["project_id"] for w in result.json()["data"]["records"]} == {"foreign"}
        for path, body in [
            ("/api-keys/create", {"name": "attack"}),
            ("/api-keys/remove", {"id": 1}),
            ("/workflows/upsert", {"project_id": "allowed", "status": 1}),
        ]:
            assert (await client.post(path, headers=headers, json=body)).status_code == 401


@pytest.mark.asyncio
async def test_session_key_management_routes_keep_hash_mask_and_owner_boundary(security_db):
    # These are trusted gateway assertions on the private service connection.
    # Public header stripping/session authentication is tested in OpenResty.
    engine, _ = security_db
    async with rest_client() as client:
        created = await client.post("/api-keys/create", headers={"user_id": "owner"}, json={"name": "session-key"})
        assert created.status_code == 201
        raw = created.json()["data"]["api_key"]
        listed = await client.get("/api-keys/get?pageSize=50", headers={"user_id": "owner"})
        assert listed.status_code == 200
        assert raw not in listed.text
        record = next(item for item in listed.json()["data"]["records"] if item["name"] == "session-key")
        denied = await client.post("/api-keys/remove", headers={"user_id": "other"}, json={"id": str(record["id"])})
        assert denied.json()["data"] is None
        assert await ToolsConfig().get_uid_from_raw_key(raw) == "owner"
        removed = await client.post("/api-keys/remove", headers={"user_id": "owner"}, json={"id": str(record["id"])})
        assert removed.status_code == 200
        assert await ToolsConfig().get_uid_from_raw_key(raw) is None
    with Session(engine) as db:
        stored = db.get(OpenAPIDB, record["id"])
        assert stored.api_key != raw
        assert APIKeyUtils.verify_api_key(raw, stored.api_key)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/users/register", "/users/get-key", "/workflows/copy-workflow"])
async def test_unverified_phone_delegation_is_closed(security_db, path):
    async with rest_client() as client:
        result = await client.post(
            path,
            headers={"Authorization": "Bearer owner-key"},
            json={"phone": "12345678901", "phone_number": "12345678901", "project_id": "allowed", "version": 2},
        )
    assert result.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/workflows/execute", "/workflows/execute-async"])
@pytest.mark.parametrize(
    ("payload", "status"),
    [
        ({"project_id": "foreign"}, 404),
        ({"project_id": "missing"}, 404),
        ({"project_id": "disabled"}, 404),
        ({"project_id": "unpublished"}, 404),
        ({"project_id": "allowed", "version": 1}, 403),
        ({"project_id": "allowed", "version": 0}, 403),
        ({"project_id": "allowed", "phone_number": "12345678901"}, 403),
        ({"project_id": "allowed", "exec_position": "EDITOR"}, 403),
        ({"project_id": "allowed", "user_id": "other"}, 422),
        ({"project_id": "allowed", "tenant_id": "other"}, 422),
    ],
)
async def test_denied_rest_start_never_creates_or_dispatches(security_db, monkeypatch, path, payload, status):
    engine, _ = security_db
    dispatch = AsyncMock()
    monkeypatch.setattr(ExecutionService, "execute_workflow", dispatch)
    async with rest_client() as client:
        result = await client.post(path, headers={"Authorization": "Bearer owner-key"}, json=payload)
    assert result.status_code == status
    dispatch.assert_not_awaited()
    with Session(engine) as session:
        assert len(session.execute(select(Execution)).scalars().all()) == 5


@pytest.mark.asyncio
async def test_rest_start_pins_current_release_and_preserves_response(security_db, monkeypatch):
    dispatch = AsyncMock(
        return_value=Execution(
            id="new", project_id="allowed", user_id="owner", version=2, status="PENDING", parameters="{}"
        )
    )
    monkeypatch.setattr(ExecutionService, "execute_workflow", dispatch)
    async with rest_client() as client:
        for path in ("/workflows/execute", "/workflows/execute-async"):
            result = await client.post(
                path,
                headers={"Authorization": "Bearer owner-key", "user_id": "other"},
                json={"project_id": "allowed", "params": {"value": 0}},
            )
            assert result.status_code in (200, 202)
            assert result.json()["data"]
            data, user = dispatch.await_args.args
            assert user == "owner"
            assert data.version == 2
            assert data.params == {"value": 0}


@pytest.mark.asyncio
async def test_discovery_detail_and_execution_visibility_align(security_db):
    _, factory = security_db
    async with factory() as db:
        fixed = WorkflowControlService(db)
        assert {w["projectId"] for w in (await fixed.list_workflows("owner"))["workflows"]} == {"allowed"}
    tools = await ToolsConfig().get_tools_for_user("owner")
    assert [tool.name for tool in tools] == ["allowed"]
    async with rest_client() as client:
        headers = {"Authorization": "Bearer owner-key"}
        listed = await client.get("/executions/get", headers=headers)
        assert listed.json()["data"]["total"] == 1
        assert [e["id"] for e in listed.json()["data"]["executions"]] == ["allowed"]
        for execution in ["foreign", "disabled", "unpublished", "old-release", "missing"]:
            result = await client.get("/executions/" + execution, headers=headers)
            assert result.status_code == 404
            assert result.json()["data"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["revoke-access", "republish"])
async def test_current_permissions_apply_to_rest_and_mcp_results(security_db, change):
    engine, factory = security_db
    with Session(engine) as session:
        workflow = session.get(Workflow, "allowed")
        if change == "revoke-access":
            workflow.status = 0
        else:
            workflow.version = 3
        session.commit()
    async with factory() as db:
        with pytest.raises(WorkflowAccessError, match="Execution not found"):
            await WorkflowControlService(db).get_execution("allowed", "owner")
    async with rest_client() as client:
        result = await client.get("/executions/allowed", headers={"Authorization": "Bearer owner-key"})
    assert result.status_code == 404


@pytest.mark.asyncio
async def test_dynamic_start_rechecks_release_before_dispatch(security_db, monkeypatch):
    tools = ToolsConfig()
    monkeypatch.setattr(tools, "get_project_id_by_name", AsyncMock(return_value=("allowed", 1)))
    dispatch = AsyncMock()
    monkeypatch.setattr(ExecutionService, "execute_workflow", dispatch)
    result = await tools.execute_workflow_by_name("allowed", "owner", {})
    assert result["success"] is False
    dispatch.assert_not_awaited()


@pytest.mark.asyncio
async def test_rotation_hash_masking_owner_checks_and_revocation(security_db):
    engine, factory = security_db
    async with factory() as db:
        service = ApiKeyService(db)
        new_key = await service.create_api_key(ApiKeyCreate(name="rotation"), "owner")
        await db.commit()
        listed = await service.get_api_keys("owner", 1, 100)
        assert new_key not in json.dumps(listed, default=str)
        record = (await db.execute(select(OpenAPIDB).where(OpenAPIDB.name == "rotation"))).scalar_one()
        assert record.api_key != new_key
        assert APIKeyUtils.verify_api_key(new_key, record.api_key)
        assert await service.delete_api_key(record.id, "other") is False
        assert await service.get_api_key(record.id, "other") is None
        old = (await db.execute(select(OpenAPIDB).where(OpenAPIDB.name == "owner-key"))).scalar_one()
        assert await service.validate_api_key(new_key) == "owner"
        assert await service.validate_api_key("owner-key") == "owner"
        assert await service.delete_api_key(old.id, "owner") is True
        await db.commit()
    # New requests, including MCP, do not reuse a cached validation result.
    for key, expected in [("owner-key", 401), (new_key, 200)]:
        async with rest_client() as client:
            assert (
                await client.get("/executions/get", headers={"Authorization": "Bearer " + key})
            ).status_code == expected
        assert await ToolsConfig().get_uid_from_raw_key(key) == ("owner" if expected == 200 else None)
    with Session(engine) as session:
        assert session.get(Execution, "allowed").status == "PENDING"


@pytest.mark.asyncio
async def test_corrupt_hash_long_key_and_validator_failure_do_not_leak(security_db, caplog):
    _, factory = security_db
    async with factory() as db:
        db.add(OpenAPIDB(user_id="owner", prefix="bad-hash", api_key="private-invalid-hash", is_active=1))
        await db.commit()
        assert await validate_api_key(db, "bad-hash") is None
        assert await validate_api_key(db, "owner-key" + "x" * 73) is None
    broken = AsyncMock()
    broken.execute.side_effect = RuntimeError("private-sql-value")
    with pytest.raises(HTTPException) as error:
        await get_user_id_from_api_key(request([("Authorization", "Bearer owner-key")]), broken)
    assert error.value.status_code == 503
    assert "private" not in str(error.value) + caplog.text


@pytest.mark.asyncio
async def test_http_validation_and_stored_errors_do_not_echo_sensitive_values(security_db):
    engine, _ = security_db
    with Session(engine) as db:
        db.get(Execution, "allowed").error = "SQL parameters: private-database-value"
        db.commit()
    async with rest_client() as client:
        headers = {"Authorization": "Bearer owner-key"}
        invalid = await client.post(
            "/workflows/execute-async",
            headers=headers,
            json={"project_id": "allowed", "version": "private-input-value"},
        )
        assert invalid.status_code == 422
        assert "private-input-value" not in invalid.text
        result = await client.get("/executions/allowed", headers=headers)
        assert result.status_code == 200
        assert "private-database-value" not in result.text


@pytest.mark.asyncio
async def test_execution_failure_logs_omit_unlabelled_sensitive_values(monkeypatch, caplog):
    database = AsyncMock()
    database.execute.side_effect = RuntimeError("private-sql-parameter-value")
    service = ExecutionService(database)
    assert await service.update_execution_status("example", "FAILED") is None
    monkeypatch.setattr(
        "app.dependencies.get_ws_service", AsyncMock(side_effect=RuntimeError("private-dispatch-value"))
    )
    with pytest.raises(RuntimeError):
        await service._execute_workflow_logic(Execution(id="example", user_id="owner", parameters="{}"))
    assert "private-sql-parameter-value" not in caplog.text
    assert "private-dispatch-value" not in caplog.text


def test_dynamic_password_defaults_are_not_advertised():
    tool = ToolsConfig.workflow_to_tool(
        {
            "name": "legacy",
            "description": "test",
            "parameters": [
                {"varName": "password", "varDirection": 0, "varType": "Password", "varValue": "private-default"},
            ],
        }
    )
    assert "private-default" not in tool.model_dump_json()
    assert tool.inputSchema["properties"]["password"]["writeOnly"] is True


@pytest.mark.asyncio
async def test_discovery_failure_is_not_an_empty_authorized_list(monkeypatch):
    tools = ToolsConfig()
    monkeypatch.setattr(tools, "_get_workflow_service", AsyncMock(side_effect=RuntimeError("private-sql")))
    with pytest.raises(RuntimeError, match="^Workflow discovery unavailable$"):
        await tools.get_tools_for_user("owner")


@pytest.mark.asyncio
async def test_existing_stop_targets_only_authenticated_user(security_db, monkeypatch):
    sent = []

    async def send(message, timeout, callback):
        sent.append(message)
        reply = type("Reply", (), {"data": {"code": "0000"}})()
        callback(reply)

    manager = type("Manager", (), {"send_reply": staticmethod(send)})()
    monkeypatch.setattr(
        "app.dependencies.get_ws_service", AsyncMock(return_value=type("WS", (), {"ws_manager": manager})())
    )
    async with rest_client() as client:
        result = await client.post(
            "/workflows/stop-current", headers={"Authorization": "Bearer other-key", "user_id": "owner"}
        )
    assert result.status_code == 202
    assert len(sent) == 1
    assert sent[0].send_uuid == "other"


@pytest.mark.asyncio
async def test_real_mcp_connection_check_and_revocation_have_no_execution_side_effect(security_db, monkeypatch):
    engine, factory = security_db
    monkeypatch.setattr("sse_starlette.sse.AppStatus.should_exit_event", None)
    manager = StreamableHTTPSessionManager(streamable_mcp.app, stateless=True, json_response=False)
    secured = MCPAPIKeyAuthMiddleware(manager.handle_request, ToolsConfig().get_uid_from_raw_key)
    asgi = Starlette(routes=[Mount("/mcp", app=secured)])
    async with manager.run():
        async with AsyncClient(
            transport=ASGITransport(app=asgi), headers={"Authorization": "Bearer owner-key"}
        ) as http:
            async with streamable_http_client("http://test/mcp/", http_client=http, terminate_on_close=False) as (
                read,
                write,
                _,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    assert len((await session.list_tools()).tools) >= 4
                    async with factory() as db:
                        record = (await db.execute(select(OpenAPIDB).where(OpenAPIDB.name == "owner-key"))).scalar_one()
                        await ApiKeyService(db).delete_api_key(record.id, "owner")
                        await db.commit()
                    # Even on an existing HTTP client, the next request revalidates.
                    response = await http.post(
                        "http://test/mcp/", json={"jsonrpc": "2.0", "id": 8, "method": "tools/list"}
                    )
                    assert response.status_code == 401
    with Session(engine) as db:
        assert len(db.execute(select(Execution)).scalars().all()) == 5
