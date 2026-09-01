from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount

from app import database
from app.main import app as openapi_app
from app.models.api_key import OpenAPIDB
from app.routers.streamable_mcp import app as mcp_server
from app.routers.streamable_mcp import tools_config
from app.security.mcp_auth import MCPAPIKeyAuthMiddleware
from app.services.streamable_mcp import ToolsConfig
from app.utils.api_key import APIKeyUtils


class AsyncSessionAdapter:
    """Minimal async facade over a real in-memory SQLAlchemy session."""

    def __init__(self, session):
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def rollback(self):
        self.session.rollback()

    async def close(self):
        self.session.close()


async def empty_tools_app(scope, receive, send):
    response = JSONResponse(
        {
            "tools": [],
            "user_id": scope["state"]["mcp_user_id"],
        }
    )
    await response(scope, receive, send)


async def request_mcp(auth_app, *, headers=None, params=None):
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post("/mcp", headers=headers, params=params)


def make_asgi_http_client_factory(asgi_app):
    @asynccontextmanager
    async def asgi_http_client_factory(headers=None, timeout=None, auth=None):
        transport = ASGITransport(app=asgi_app)
        async with AsyncClient(transport=transport, headers=headers, timeout=timeout, auth=auth) as client:
            yield client

    return asgi_http_client_factory


@pytest.mark.asyncio
async def test_mcp_mount_rejects_missing_credentials_before_protocol_handling():
    transport = ASGITransport(app=openapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/mcp/")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_mcp_mount_rejects_query_key_with_default_configuration():
    transport = ASGITransport(app=openapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/mcp/", params={"key": "legacy-key"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_mcp_missing_credentials_returns_401():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(auth_app)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    validator.assert_not_awaited()


@pytest.mark.asyncio
async def test_mcp_bearer_authenticates_before_returning_empty_tools():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(
        auth_app,
        headers={"Authorization": "Bearer valid-key"},
    )

    assert response.status_code == 200
    assert response.json() == {"tools": [], "user_id": "user-1"}
    validator.assert_awaited_once_with("valid-key")


@pytest.mark.asyncio
async def test_mcp_x_api_key_authenticates():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(auth_app, headers={"X-API-Key": "valid-key"})

    assert response.status_code == 200
    validator.assert_awaited_once_with("valid-key")


@pytest.mark.asyncio
async def test_actual_mcp_endpoint_accepts_bearer_and_x_api_key(monkeypatch):
    validator = AsyncMock(side_effect=lambda key: f"user-for-{key}")
    get_tools = AsyncMock(return_value=[])
    execute_workflow = AsyncMock(
        return_value={
            "success": True,
            "execution_id": "execution-1",
            "project_id": "project-1",
            "message": {"code": "0000", "data": {}},
        }
    )
    monkeypatch.setattr(tools_config, "get_tools_for_user", get_tools)
    monkeypatch.setattr(tools_config, "execute_workflow_by_name", execute_workflow)
    test_session_manager = StreamableHTTPSessionManager(
        app=mcp_server,
        event_store=None,
        json_response=False,
        stateless=True,
    )
    test_auth_app = MCPAPIKeyAuthMiddleware(test_session_manager.handle_request, validator)
    test_asgi_app = Starlette(routes=[Mount("/mcp", app=test_auth_app)])
    httpx_client_factory = make_asgi_http_client_factory(test_asgi_app)

    credential_cases = [
        ({"Authorization": "Bearer bearer-key"}, "bearer-key"),
        ({"X-API-Key": "header-key"}, "header-key"),
    ]

    async with test_session_manager.run():
        for headers, expected_key in credential_cases:
            async with streamablehttp_client(
                "http://test/mcp/",
                headers=headers,
                terminate_on_close=False,
                httpx_client_factory=httpx_client_factory,
            ) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as client_session:
                    await client_session.initialize()
                    result = await client_session.list_tools()
                    call_result = await client_session.call_tool("workflow-tool", {"value": 1})

            assert result.tools == []
            assert call_result.isError is False
            assert validator.await_args.args == (expected_key,)

    validated_keys = {call.args[0] for call in validator.await_args_list}
    assert validated_keys == {"bearer-key", "header-key"}
    listed_user_ids = {call.args[0] for call in get_tools.await_args_list}
    assert listed_user_ids == {"user-for-bearer-key", "user-for-header-key"}
    assert execute_workflow.await_count == 2
    assert execute_workflow.await_args_list[0].args == (
        "workflow-tool",
        "user-for-bearer-key",
        {"value": 1},
    )
    assert execute_workflow.await_args_list[1].args == (
        "workflow-tool",
        "user-for-header-key",
        {"value": 1},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "authorization",
    ["valid-key", "Basic valid-key", "Bearer", "Bearer key extra"],
)
async def test_mcp_malformed_bearer_returns_401(authorization):
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(
        auth_app,
        headers={"Authorization": authorization},
    )

    assert response.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.asyncio
async def test_mcp_invalid_or_revoked_key_returns_401():
    validator = AsyncMock(return_value=None)
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(
        auth_app,
        headers={"Authorization": "Bearer revoked-key"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    validator.assert_awaited_once_with("revoked-key")


@pytest.mark.asyncio
async def test_mcp_query_key_is_disabled_by_default():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(auth_app, params={"key": "legacy-key"})

    assert response.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.asyncio
async def test_mcp_query_key_can_be_enabled_for_migration():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(
        empty_tools_app,
        validator,
        allow_query_api_key=True,
    )

    response = await request_mcp(auth_app, params={"key": "legacy-key"})

    assert response.status_code == 200
    validator.assert_awaited_once_with("legacy-key")


@pytest.mark.asyncio
async def test_mcp_rejects_conflicting_credential_sources():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(
        auth_app,
        headers={
            "Authorization": "Bearer bearer-key",
            "X-API-Key": "header-key",
        },
    )

    assert response.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers",
    [
        [("Authorization", "Bearer first"), ("Authorization", "Bearer second")],
        {"X-API-Key": ""},
        [("X-API-Key", "first"), ("X-API-Key", "second")],
    ],
)
async def test_mcp_rejects_duplicate_or_empty_headers(headers):
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(auth_app, headers=headers)

    assert response.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        {"key": ""},
        [("key", "first"), ("key", "second")],
    ],
)
async def test_mcp_rejects_empty_or_duplicate_query_keys(params):
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(
        empty_tools_app,
        validator,
        allow_query_api_key=True,
    )

    response = await request_mcp(auth_app, params=params)

    assert response.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.asyncio
async def test_mcp_rejects_header_and_enabled_query_key_together():
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(
        empty_tools_app,
        validator,
        allow_query_api_key=True,
    )

    response = await request_mcp(
        auth_app,
        headers={"Authorization": "Bearer bearer-key"},
        params={"key": "query-key"},
    )

    assert response.status_code == 401
    validator.assert_not_awaited()


@pytest.mark.asyncio
async def test_mcp_non_http_scope_passes_through():
    downstream = AsyncMock()
    validator = AsyncMock(return_value="user-1")
    auth_app = MCPAPIKeyAuthMiddleware(downstream, validator)
    receive = AsyncMock()
    send = AsyncMock()
    scope = {"type": "lifespan"}

    await auth_app(scope, receive, send)

    downstream.assert_awaited_once_with(scope, receive, send)
    validator.assert_not_awaited()


@pytest.mark.asyncio
async def test_mcp_validator_failure_returns_503_without_exposing_error():
    validator = AsyncMock(side_effect=RuntimeError("database connection failed"))
    auth_app = MCPAPIKeyAuthMiddleware(empty_tools_app, validator)

    response = await request_mcp(
        auth_app,
        headers={"Authorization": "Bearer secret-key"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "Authentication service unavailable"}
    assert "secret-key" not in response.text


@pytest.mark.asyncio
async def test_api_key_lookup_accepts_active_and_rejects_revoked_key(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    OpenAPIDB.__table__.create(engine)
    active_key = "active-test-api-key"
    revoked_key = "revoked-test-api-key"

    with Session(engine) as session:
        session.add_all(
            [
                OpenAPIDB(
                    user_id="user-active",
                    api_key=APIKeyUtils.hash_api_key(active_key),
                    prefix=active_key[:8],
                    is_active=1,
                ),
                OpenAPIDB(
                    user_id="user-revoked",
                    api_key=APIKeyUtils.hash_api_key(revoked_key),
                    prefix=revoked_key[:8],
                    is_active=0,
                ),
            ]
        )
        session.commit()

    monkeypatch.setattr(
        database,
        "AsyncSessionLocal",
        lambda: AsyncSessionAdapter(Session(engine)),
    )
    config = ToolsConfig()

    assert await config.get_uid_from_raw_key(active_key) == "user-active"
    assert await config.get_uid_from_raw_key(revoked_key) is None

    engine.dispose()
