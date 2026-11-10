import secrets
from ipaddress import ip_address
from typing import Optional

from astronverse.scheduler.logger import logger
from fastapi import Request
from fastapi.websockets import WebSocket
from starlette.responses import JSONResponse

LOCAL_HOSTS = {"localhost"}
REMOTE_ALLOWED_PREFIXES = ("/terminal/", "/executor/")

# Browser origins of the desktop client: packaged renderer (rpa://) and the Vite dev server
ALLOWED_ORIGINS = [
    "rpa://localhost",
    "rpa://extensions",
    "http://localhost:1420",
    "http://127.0.0.1:1420",
]


def _is_loopback_host(client_host: str) -> bool:
    if client_host in LOCAL_HOSTS:
        return True

    try:
        return ip_address(client_host).is_loopback
    except ValueError:
        return False


def is_local_request(request: Request) -> bool:
    client_host = request.client.host if request.client else ""
    return _is_loopback_host(client_host)


def is_local_websocket(ws: WebSocket) -> bool:
    client_host = ws.client.host if ws.client else ""
    return _is_loopback_host(client_host)


def is_remote_allowed_path(path: str) -> bool:
    return path in {"/terminal", "/executor"} or path.startswith(REMOTE_ALLOWED_PREFIXES)


def _remote_api_token() -> str:
    """Return the configured token without making startup/config errors fatal."""
    try:
        from astronverse.scheduler.core.svc import get_svc

        config = get_svc().config
    except Exception:
        return ""
    return str(getattr(config, "scheduler_api_token", "") or "") if config else ""


def is_authorized_remote_request(request: Request) -> bool:
    configured = _remote_api_token()
    supplied = request.headers.get("x-scheduler-token", "")
    return bool(configured) and secrets.compare_digest(supplied, configured)


def is_allowed_origin(origin: Optional[str]) -> bool:
    """
    Non-browser callers send no Origin and are allowed through the origin check;
    remote scheduler routes still require their separate token check below.
    Browser callers must come from the desktop client; "null" and other origins are rejected.
    """
    if origin is None:
        return True
    return origin.rstrip("/") in ALLOWED_ORIGINS


def is_allowed_websocket_origin(ws: WebSocket) -> bool:
    origin = ws.headers.get("origin")
    if is_allowed_origin(origin):
        return True
    logger.warning("websocket rejected, origin not allowed: {}".format(origin))
    return False


async def local_access_guard(request: Request, call_next):
    origin = request.headers.get("origin")
    if not is_allowed_origin(origin):
        logger.warning("request rejected, origin not allowed: {} {}".format(origin, request.url.path))
        return JSONResponse(status_code=403, content={"detail": "origin not allowed"})

    if is_local_request(request):
        return await call_next(request)

    if is_remote_allowed_path(request.url.path) and is_authorized_remote_request(request):
        return await call_next(request)

    if is_remote_allowed_path(request.url.path):
        return JSONResponse(status_code=401, content={"detail": "scheduler token required"})

    return JSONResponse(status_code=403, content={"detail": "local access only"})
