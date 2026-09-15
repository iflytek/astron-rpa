import base64
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.responses import Response

from app.routers.mcp_modern import PREFIX, VERSION, DualProtocolMCP
from app.schemas.mcp import CONTROL_TOOLS
from app.security.mcp_auth import MCPAPIKeyAuthMiddleware


def message(method="tools/list", params=None, version=VERSION):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {"_meta": {PREFIX + "protocolVersion": version, PREFIX + "clientCapabilities": {}}, **(params or {})},
    }


def headers(method="tools/list", name=None, version=VERSION):
    result = {
        "Authorization": "Bearer test-key",
        "MCP-Protocol-Version": version,
        "Mcp-Method": method,
        "Accept": "application/json, text/event-stream",
    }
    if name:
        result["Mcp-Name"] = name
    return result


@pytest.fixture
def endpoint():
    calls = AsyncMock(return_value={"executionId": "one"})
    listing = AsyncMock(return_value=list(CONTROL_TOOLS.values()))

    async def legacy_response(scope, receive, send):
        await Response(status_code=204)(scope, receive, send)

    legacy = AsyncMock(side_effect=legacy_response)
    app = MCPAPIKeyAuthMiddleware(DualProtocolMCP(legacy, listing, calls), AsyncMock(return_value="owner"))
    return app, calls, legacy


@pytest.mark.asyncio
async def test_modern_discover_list_call_without_initialize_or_session(endpoint):
    app, calls, _ = endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://service") as client:
        for method in ("server/discover", "tools/list", "ping"):
            response = await client.post("/", json=message(method), headers=headers(method))
            assert response.status_code == 200
            assert "mcp-session-id" not in response.headers
            assert response.json()["result"]["_meta"][PREFIX + "serverInfo"]["name"] == "iflyrpa-mcp"
        tool = "astron_workflow_execute"
        h = headers("tools/call", tool)
        h.update({"Mcp-Session-Id": "ignored", "Last-Event-ID": "ignored"})
        response = await client.post("/", json=message("tools/call", {"name": tool, "arguments": {}}), headers=h)
        assert response.json()["result"]["structuredContent"] == {"executionId": "one"}
        calls.assert_awaited_once_with("owner", tool, {}, 1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fault", "code"),
    [
        ("version_missing", -32020),
        ("method_missing", -32020),
        ("name_missing", -32020),
        ("version_mismatch", -32020),
        ("method_mismatch", -32020),
        ("name_mismatch", -32020),
        ("bad_base64", -32020),
        ("unknown_version", -32022),
        ("missing_capabilities", -32602),
    ],
)
async def test_modern_invalid_request_never_dispatches(endpoint, fault, code):
    app, calls, _ = endpoint
    data = message("tools/call", {"name": "astron_workflow_execute", "arguments": {}})
    h = headers("tools/call", "astron_workflow_execute")
    if fault.endswith("_missing"):
        h.pop(
            {"version_missing": "MCP-Protocol-Version", "method_missing": "Mcp-Method", "name_missing": "Mcp-Name"}[
                fault
            ]
        )
    elif fault.endswith("_mismatch"):
        h[
            {"version_mismatch": "MCP-Protocol-Version", "method_mismatch": "Mcp-Method", "name_mismatch": "Mcp-Name"}[
                fault
            ]
        ] = "different"
    elif fault == "bad_base64":
        h["Mcp-Name"] = "=?base64?@?="
    elif fault == "unknown_version":
        h["MCP-Protocol-Version"] = data["params"]["_meta"][PREFIX + "protocolVersion"] = "2099-01-01"
    else:
        data["params"]["_meta"].pop(PREFIX + "clientCapabilities")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://service") as client:
        response = await client.post("/", json=data, headers=h)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == code
    calls.assert_not_awaited()


@pytest.mark.asyncio
async def test_modern_encoded_name_unknown_method_and_http_contract(endpoint):
    app, calls, _ = endpoint
    name = "工具"
    encoded = "=?base64?" + base64.b64encode(name.encode()).decode() + "?="
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://service") as client:
        response = await client.post(
            "/", json=message("tools/call", {"name": name}), headers=headers("tools/call", encoded)
        )
        assert response.status_code == 200
        calls.assert_awaited_once_with("owner", name, {}, 1)
        for verb in ("GET", "DELETE"):
            response = await client.request(verb, "/", headers=headers())
            assert response.status_code == 405
        response = await client.post("/", json=message("initialize"), headers=headers("initialize"))
        assert response.status_code == 404
        assert response.json()["error"]["code"] == -32601
        response = await client.post("/", json=message(), headers={**headers(), "Origin": "https://untrusted.example"})
        assert response.status_code == 403
        response = await client.post("/", json=message(), headers={**headers(), "Accept": "application/json"})
        assert response.status_code == 406


@pytest.mark.asyncio
async def test_modern_requires_authentication_and_legacy_route_is_preserved(endpoint):
    app, calls, legacy = endpoint
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://service") as client:
        response = await client.post(
            "/", json=message(), headers={k: v for k, v in headers().items() if k != "Authorization"}
        )
        assert response.status_code == 401
        response = await client.post(
            "/", json={"jsonrpc": "2.0", "id": 1, "method": "initialize"}, headers={"Authorization": "Bearer test-key"}
        )
        assert response.status_code == 204
    calls.assert_not_awaited()
    legacy.assert_awaited_once()
