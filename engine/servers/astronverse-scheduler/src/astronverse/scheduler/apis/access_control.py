from ipaddress import ip_address

from fastapi import Request
from fastapi.websockets import WebSocket
from starlette.responses import JSONResponse


LOCAL_HOSTS = {"localhost"}
REMOTE_ALLOWED_PREFIXES = ("/terminal/", "/executor/")


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


async def local_access_guard(request: Request, call_next):
    if is_local_request(request) or is_remote_allowed_path(request.url.path):
        return await call_next(request)

    return JSONResponse(status_code=403, content={"detail": "local access only"})
