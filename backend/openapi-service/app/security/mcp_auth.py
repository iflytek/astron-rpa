import json
import logging
from collections.abc import Awaitable, Callable

from starlette.types import ASGIApp, Receive, Scope, Send

from app.security.api_key import APIKeyAuthenticationError as MCPAuthenticationError
from app.security.api_key import extract_api_key as extract_mcp_api_key

logger = logging.getLogger(__name__)

APIKeyValidator = Callable[[str], Awaitable[str | None]]


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
        except Exception as exc:
            logger.error("MCP API key validation failed: %s", type(exc).__name__)  # noqa: TRY400 -- omit sensitive exception text
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
