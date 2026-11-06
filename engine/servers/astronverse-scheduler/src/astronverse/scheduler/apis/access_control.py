import hmac
import os
from ipaddress import ip_address

from fastapi import Request
from fastapi.websockets import WebSocket
from starlette.responses import JSONResponse


LOCAL_HOSTS = {"localhost"}
REMOTE_ALLOWED_PREFIXES = ("/terminal/", "/executor/")

# Remote access to /terminal and /executor (screenshot capture, terminal mode,
# task control) is opt-in and must be secured with a shared token. Unset by
# default, which denies remote callers entirely - these routes carry no
# authentication of their own, only this gate.
REMOTE_CONTROL_TOKEN_HEADER = "x-remote-control-token"
_REMOTE_CONTROL_TOKEN = os.environ.get("ASTRON_SCHEDULER_REMOTE_CONTROL_TOKEN")


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


def _has_valid_remote_control_token(request: Request) -> bool:
    if not _REMOTE_CONTROL_TOKEN:
        return False
    supplied = request.headers.get(REMOTE_CONTROL_TOKEN_HEADER, "")
    return hmac.compare_digest(supplied, _REMOTE_CONTROL_TOKEN)


async def local_access_guard(request: Request, call_next):
    if is_local_request(request):
        return await call_next(request)

    if is_remote_allowed_path(request.url.path) and _has_valid_remote_control_token(request):
        return await call_next(request)

    return JSONResponse(status_code=403, content={"detail": "local access only"})
