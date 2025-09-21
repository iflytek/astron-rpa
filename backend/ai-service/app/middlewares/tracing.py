import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import contextvars
import logging

request_id_ctx_var = contextvars.ContextVar("request_id", default=None)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set the request ID in the context variable
        request_id_ctx_var.set(request_id)

        # Process the request
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get() or "-"
        return True


def get_request_id():
    return request_id_ctx_var.get()
