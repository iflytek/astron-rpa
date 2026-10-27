import contextvars
import logging
import re
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders

request_id_ctx_var = contextvars.ContextVar("request_id", default=None)
correlation_ctx = contextvars.ContextVar("correlation", default=None)


def safe_id(value):
    value = str(value) if value is not None else ""
    return value if re.fullmatch(r"[A-Za-z0-9_.:-]{1,96}", value) else None


class RequestTracingMiddleware:
    """Correlate the full streaming response without buffering bodies."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = Headers(scope=scope)
        request_id = safe_id(headers.get("x-request-id")) or uuid.uuid4().hex
        token = request_id_ctx_var.set(request_id)
        context = correlation_ctx.set(
            {
                "n8n_execution_id": safe_id(headers.get("x-n8n-execution-id")),
                "n8n_item_index": safe_id(headers.get("x-n8n-item-index")),
            }
        )
        started = time.monotonic()
        status = 500

        async def traced_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, traced_send)
        finally:
            from app.services.observability import http_observed

            try:
                http_observed(scope, status, time.monotonic() - started)
            finally:
                correlation_ctx.reset(context)
                request_id_ctx_var.reset(token)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get() or "-"
        return True


def get_request_id():
    return request_id_ctx_var.get()
