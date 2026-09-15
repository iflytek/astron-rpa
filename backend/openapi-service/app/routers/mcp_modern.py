"""2026-07-28 request-scoped MCP binding alongside the legacy SDK adapter.

This adapter advertises tools only. It implements no sessions, subscriptions,
sampling or resumable streams. JSON responses are permitted by Streamable HTTP.
Business authorization and dispatch are shared with the legacy endpoint.
"""

import base64
import json

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

VERSION = "2026-07-28"
LEGACY = {"2025-03-26", "2025-06-18", "2025-11-25"}
SUPPORTED = [VERSION, *sorted(LEGACY, reverse=True)]
PREFIX = "io.modelcontextprotocol/"


def error(code, message, identifier=None, status=400, data=None):
    payload = {"jsonrpc": "2.0", "error": {"code": code, "message": message}}
    if identifier is not None:
        payload["id"] = identifier
    if data is not None:
        payload["error"]["data"] = data
    return JSONResponse(payload, status_code=status)


def decode_name(value):
    if value.startswith("=?base64?") and value.endswith("?="):
        return base64.b64decode(value[9:-2], validate=True).decode("utf-8")
    if not value or value != value.strip() or any(ord(char) < 32 or ord(char) > 126 for char in value):
        raise ValueError
    return value


class DualProtocolMCP:
    def __init__(self, legacy, list_tools, call_tool, allowed_origins=()):
        self.legacy = legacy
        self.list_tools = list_tools
        self.call_tool = call_tool
        self.allowed_origins = set(allowed_origins)

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)
        origins = request.headers.getlist("origin")
        if origins and (len(origins) != 1 or origins[0] not in self.allowed_origins):
            await Response(status_code=403)(scope, receive, send)
            return
        version = request.headers.get("mcp-protocol-version")
        body = b""
        if request.method == "POST":
            async for chunk in request.stream():
                body += chunk
                if len(body) > 1024 * 1024:
                    await Response(status_code=413)(scope, receive, send)
                    return
        try:
            message = json.loads(body) if body else {}
        except (ValueError, UnicodeError):
            await error(-32700, "Invalid JSON")(scope, receive, send)
            return
        params = message.get("params", {}) if isinstance(message, dict) else {}
        meta = params.get("_meta", {}) if isinstance(params, dict) else {}
        modern = (version is not None and version not in LEGACY) or "mcp-method" in request.headers
        modern = modern or (isinstance(meta, dict) and PREFIX + "protocolVersion" in meta)
        if not modern:
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return await receive()

            await self.legacy(scope, replay, send)
            return
        response = await self.handle(request, message)
        await response(scope, receive, send)

    async def handle(self, request, message):
        if request.method != "POST":
            return Response(status_code=405, headers={"Allow": "POST"})
        if request.headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
            return Response(status_code=415)
        accepted = {part.split(";", 1)[0].strip() for part in request.headers.get("accept", "").split(",")}
        if not {"application/json", "text/event-stream"}.issubset(accepted):
            return Response(status_code=406)
        if (
            not isinstance(message, dict)
            or message.get("jsonrpc") != "2.0"
            or not isinstance(message.get("method"), str)
        ):
            return error(-32600, "Invalid request")
        identifier = message.get("id")
        if identifier is not None and type(identifier) not in (str, int):
            return error(-32600, "Invalid request identifier")
        method, params = message["method"], message.get("params", {})
        if not isinstance(params, dict):
            return error(-32602, "Invalid request parameters", identifier)
        meta = params.get("_meta", {})
        if not isinstance(meta, dict):
            return error(-32602, "Invalid request metadata", identifier)
        pairs = [("mcp-protocol-version", meta.get(PREFIX + "protocolVersion")), ("mcp-method", method)]
        if method in {"tools/call", "prompts/get", "resources/read"}:
            pairs.append(("mcp-name", params.get("uri" if method == "resources/read" else "name")))
        try:
            for header, expected in pairs:
                values = request.headers.getlist(header)
                if len(values) != 1 or not isinstance(expected, str):
                    raise ValueError
                actual = decode_name(values[0]) if header == "mcp-name" else values[0]
                if actual != expected:
                    raise ValueError
        except (ValueError, UnicodeError):
            return error(-32020, "Required request headers are missing or do not match the body", identifier)
        version = request.headers["mcp-protocol-version"]
        if version != VERSION:
            return error(
                -32022, "Unsupported protocol version", identifier, data={"supported": SUPPORTED, "requested": version}
            )
        if not isinstance(meta.get(PREFIX + "clientCapabilities"), dict):
            return error(-32602, "Per-request clientCapabilities are required", identifier)
        if identifier is None:
            # No HTTP client notifications are advertised by this implementation.
            return error(-32601, "Notification not supported", status=404)
        user = str(request.state.mcp_user_id)
        if method == "server/discover":
            result = {"supportedVersions": SUPPORTED, "capabilities": {"tools": {}}}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            if params.get("cursor"):
                return error(-32602, "Pagination cursor is not supported", identifier)
            result = {
                "tools": [tool.model_dump(by_alias=True, exclude_none=True) for tool in await self.list_tools(user)]
            }
        elif method == "tools/call":
            if not isinstance(params.get("name"), str) or not isinstance(params.get("arguments", {}), dict):
                return error(-32602, "Invalid tool arguments", identifier)
            result = await self.call_tool(user, params["name"], params.get("arguments", {}), identifier)
            if hasattr(result, "model_dump"):
                result = result.model_dump(by_alias=True, exclude_none=True)
            elif isinstance(result, list):
                result = {"content": [item.model_dump(by_alias=True, exclude_none=True) for item in result]}
            else:
                result = {
                    "content": [{"type": "text", "text": json.dumps(result, allow_nan=False)}],
                    "structuredContent": result,
                    "isError": False,
                }
        else:
            return error(-32601, "Method not found", identifier, status=404)
        result["_meta"] = {PREFIX + "serverInfo": {"name": "iflyrpa-mcp", "version": "1.2.0"}}
        return JSONResponse(
            {"jsonrpc": "2.0", "id": identifier, "result": result}, headers={"Cache-Control": "no-store"}
        )
