import json
import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Any
from urllib.parse import parse_qs

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

APIKeyValidator = Callable[[str], Awaitable[str | None]]


class MCPAuthenticationError(ValueError):
    """Raised when an MCP request does not contain one unambiguous credential."""


def _get_header_values(scope: Mapping[str, Any], name: bytes) -> list[str]:
    values = []
    for raw_name, raw_value in scope.get("headers", []):
        if raw_name.lower() == name:
            values.append(raw_value.decode("latin-1").strip())
    return values


def extract_mcp_api_key(scope: Mapping[str, Any], *, allow_query_api_key: bool = False) -> str:
    """Extract exactly one MCP API key from the supported credential locations."""
    credentials: list[str] = []

    authorization_values = _get_header_values(scope, b"authorization")
    if len(authorization_values) > 1:
        raise MCPAuthenticationError("Multiple Authorization headers are not allowed")
    if authorization_values:
        parts = authorization_values[0].split()
        if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
            raise MCPAuthenticationError("Invalid Authorization header")
        credentials.append(parts[1])

    api_key_header_values = _get_header_values(scope, b"x-api-key")
    if len(api_key_header_values) > 1 or (api_key_header_values and not api_key_header_values[0]):
        raise MCPAuthenticationError("Invalid X-API-Key header")
    if api_key_header_values:
        credentials.append(api_key_header_values[0])

    query_values = parse_qs(
        scope.get("query_string", b"").decode("latin-1"),
        keep_blank_values=True,
    ).get("key", [])
    if query_values:
        if not allow_query_api_key:
            raise MCPAuthenticationError("Query parameter API keys are disabled")
        if len(query_values) != 1 or not query_values[0].strip():
            raise MCPAuthenticationError("Invalid query parameter API key")
        credentials.append(query_values[0].strip())

    if len(credentials) != 1:
        raise MCPAuthenticationError("Exactly one API key credential is required")

    return credentials[0]


class MCPAPIKeyAuthMiddleware:
    """Authenticate every Streamable HTTP request before it reaches the MCP SDK."""

    def __init__(
        self,
        app: ASGIApp,
        validator: APIKeyValidator,
        *,
        allow_query_api_key: bool = False,
    ) -> None:
        self.app = app
        self.validator = validator
        self.allow_query_api_key = allow_query_api_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            api_key = extract_mcp_api_key(
                scope,
                allow_query_api_key=self.allow_query_api_key,
            )
            user_id = await self.validator(api_key)
        except MCPAuthenticationError:
            await self._send_error(send, 401, "Invalid authentication credentials", authenticate=True)
            return
        except Exception:
            logger.exception("MCP API key validation failed")
            await self._send_error(send, 503, "Authentication service unavailable")
            return

        if not user_id:
            await self._send_error(send, 401, "Invalid authentication credentials", authenticate=True)
            return

        scope.setdefault("state", {})["mcp_user_id"] = str(user_id)
        await self.app(scope, receive, send)

    @staticmethod
    async def _send_error(send: Send, status_code: int, detail: str, *, authenticate: bool = False) -> None:
        body = json.dumps({"detail": detail}).encode("utf-8")
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("ascii")),
        ]
        if authenticate:
            headers.append((b"www-authenticate", b"Bearer"))

        await send({"type": "http.response.start", "status": status_code, "headers": headers})
        await send({"type": "http.response.body", "body": body})
