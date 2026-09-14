"""Verified remote transport for the desktop client's local router.

The bundled router is kept for local module routing. Its remote TLS transport
does not verify certificates, so it connects only to this loopback service.
This module owns upstream TLS and origin-scoped session cookies.
"""

import asyncio
import hashlib
import json
import logging
import os
import socket
import ssl
import threading
import time
import warnings
from contextlib import asynccontextmanager
from http.cookiejar import Cookie, LoadError, LWPCookieJar
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidStatus

_HOP_HEADERS = {
    b"connection",
    b"keep-alive",
    b"proxy-authenticate",
    b"proxy-authorization",
    b"te",
    b"trailer",
    b"transfer-encoding",
    b"upgrade",
}
_WS_HEADERS = {b"sec-websocket-key", b"sec-websocket-version", b"sec-websocket-extensions", b"sec-websocket-protocol"}


class _OriginConnect(connect):
    def process_redirect(self, exc):
        # Session headers must never follow a handshake redirect to another
        # origin. Match the HTTP transport's explicit no-redirect policy.
        return exc


def _headers(raw_headers, *, request=False, websocket=False):
    excluded = set(_HOP_HEADERS)
    for name, value in raw_headers:
        if name.lower() == b"connection":
            excluded.update(part.strip().lower() for part in value.split(b","))
    if request:
        # Session cookies belong to the configured origin, not the router's
        # temporary loopback authority. Never reuse cookies supplied to it.
        excluded.update({b"host", b"cookie"})
    else:
        excluded.add(b"set-cookie")
    if websocket:
        excluded.update(_WS_HEADERS)
    return [(name, value) for name, value in raw_headers if name.lower() not in excluded]


class SessionCookies:
    def __init__(self, remote_addr: str, directory: Path):
        self.directory = directory
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.path = directory / (hashlib.sha256(remote_addr.encode()).hexdigest() + ".cookies")
        self.jar = LWPCookieJar(str(self.path))
        if self.path.exists():
            try:
                # CookieJar warns with parser tracebacks before raising
                # LoadError; malformed values may contain session material.
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning, module=r"http\.cookiejar")
                    self.jar.load(ignore_discard=True)
            except (LoadError, UnicodeError, ValueError):
                # A damaged local session must allow a fresh login, without
                # resurrecting an older session from the legacy store.
                self.jar.clear()
                self.save()
        else:
            self._migrate(remote_addr)

    def _migrate(self, remote_addr):
        legacy = self.directory.parent / ".cookie.json"
        if not legacy.exists():
            return
        origin = urlsplit(remote_addr)
        cookie_host = origin.hostname
        if "." not in cookie_host and ":" not in cookie_host:
            cookie_host += ".local"  # CookieJar's effective host for localhost.
        try:
            stored = json.loads(legacy.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            stored = {}
        entries = stored.get(origin.netloc, {}) if isinstance(stored, dict) else {}
        if not isinstance(entries, dict):
            entries = {}
        for name, entry in entries.items():
            if name not in {"SESSION", "JSESSIONID", "casdoor_session_id"} or not isinstance(entry, dict):
                continue
            raw = entry.get("key_value")
            if not isinstance(raw, str) or not raw:
                continue
            parsed = SimpleCookie()
            try:
                parsed.load(raw if raw.startswith(name + "=") else name + "=" + raw)
            except CookieError:
                continue
            if name not in parsed:
                continue
            self.jar.set_cookie(
                Cookie(
                    version=0,
                    name=name,
                    value=parsed[name].value,
                    port=None,
                    port_specified=False,
                    domain=cookie_host,
                    domain_specified=False,
                    domain_initial_dot=False,
                    path=entry.get("path") if isinstance(entry.get("path"), str) and entry["path"] else "/",
                    path_specified=True,
                    secure=origin.scheme == "https",
                    expires=None,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rest={"HttpOnly": None},
                )
            )
        self.save()

    def save(self):
        temporary = self.path.with_suffix(".tmp")
        try:
            self.jar.save(str(temporary), ignore_discard=True)
            temporary.chmod(0o600)
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)


def create_app(remote_addr: str, cookie_directory: Path) -> Starlette:
    origin = urlsplit(remote_addr)
    if origin.scheme not in {"http", "https"} or not origin.hostname or origin.username or origin.password:
        raise ValueError("remote_addr must be an HTTP or HTTPS server address without credentials")
    if origin.query or origin.fragment:
        raise ValueError("remote_addr must not contain query parameters or fragments")
    # Match the router's existing remote_addr semantics: scheme and authority.
    base_url = f"{origin.scheme}://{origin.netloc}"
    # HTTP/WebSocket debug logs include session headers and login query tokens.
    for name in ("httpx", "httpcore", "websockets.client"):
        logging.getLogger(name).setLevel(logging.WARNING)
    cookies = SessionCookies(base_url, cookie_directory)
    context = ssl.create_default_context()

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(
            verify=context,
            trust_env=False,
            follow_redirects=False,
            timeout=httpx.Timeout(600, connect=10),
            cookies=cookies.jar,
        ) as client:
            app.state.client = client
            yield

    def target(scope):
        path = scope.get("raw_path", scope["path"].encode()).decode("ascii")
        query = scope.get("query_string", b"").decode("ascii")
        return base_url + path + ("?" + query if query else "")

    async def http_forward(request: Request):
        client = request.app.state.client
        upstream = None
        try:
            forwarded = client.build_request(
                request.method,
                target(request.scope),
                headers=_headers(request.headers.raw, request=True),
                content=request.stream(),
            )
            upstream = await client.send(forwarded, stream=True)
            if upstream.headers.get_list("set-cookie"):
                cookies.save()
        except (httpx.HTTPError, OSError, ValueError):
            if upstream is not None:
                await upstream.aclose()
            # Never echo URLs, credentials, cookies or upstream exception text.
            return JSONResponse(
                {"code": "REMOTE_CONNECTION_FAILED", "message": "Remote connection failed"}, status_code=502
            )

        async def chunks():
            try:
                async for chunk in upstream.aiter_raw():
                    yield chunk
            except httpx.HTTPError:
                raise RuntimeError("Remote response stream interrupted") from None
            finally:
                await upstream.aclose()

        response = StreamingResponse(chunks(), status_code=upstream.status_code)
        response.raw_headers = _headers(upstream.headers.raw)
        return response

    async def websocket_forward(websocket: WebSocket):
        client = websocket.app.state.client
        http_url = target(websocket.scope)
        ws_url = ("wss" if origin.scheme == "https" else "ws") + http_url[http_url.index(":") :]
        forwarded = client.build_request(
            "GET", http_url, headers=_headers(websocket.headers.raw, request=True, websocket=True)
        )
        headers = [
            (k, v)
            for k, v in forwarded.headers.multi_items()
            if k.lower() != "host" and k.lower().encode() not in _HOP_HEADERS
        ]
        try:
            async with _OriginConnect(
                ws_url,
                additional_headers=headers,
                subprotocols=websocket.scope.get("subprotocols") or None,
                ssl=context if origin.scheme == "https" else None,
                proxy=None,
                open_timeout=10,
                close_timeout=5,
                max_size=None,
            ) as upstream:
                if upstream.response.headers.get_all("Set-Cookie"):
                    client.cookies.extract_cookies(
                        httpx.Response(
                            101,
                            headers=list(upstream.response.headers.raw_items()),
                            request=forwarded,
                        )
                    )
                    cookies.save()
                await websocket.accept(subprotocol=upstream.subprotocol)

                async def outbound():
                    while True:
                        message = await websocket.receive()
                        if message["type"] == "websocket.disconnect":
                            return
                        await upstream.send(
                            message.get("bytes") if message.get("bytes") is not None else message["text"]
                        )

                async def inbound():
                    async for message in upstream:
                        if isinstance(message, bytes):
                            await websocket.send_bytes(message)
                        else:
                            await websocket.send_text(message)

                tasks = [asyncio.create_task(outbound()), asyncio.create_task(inbound())]
                try:
                    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                finally:
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
        except InvalidStatus as exc:
            status = exc.response.status_code
            await websocket.send_denial_response(Response(status_code=502 if 300 <= status < 400 else status))
            return
        except (OSError, InvalidHandshake, TimeoutError, WebSocketDisconnect, ConnectionClosed):
            pass
        finally:
            if websocket.application_state.name != "DISCONNECTED":
                await websocket.close(code=1001)

    return Starlette(
        lifespan=lifespan,
        routes=[
            Route("/{path:path}", http_forward, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]),
            WebSocketRoute("/{path:path}", websocket_forward),
        ],
    )


class RemoteTransport:
    """A loopback-only relay whose lifetime follows the local router."""

    def __init__(self, remote_addr: str):
        self.app = create_app(remote_addr, Path.cwd() / ".remote-cookies")
        self.server = None
        self.thread = None
        self.socket = None

    def start(self) -> int:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 0))
        self.server = uvicorn.Server(
            uvicorn.Config(
                self.app,
                access_log=False,
                log_level="warning",
                timeout_graceful_shutdown=3,
            )
        )
        self.thread = threading.Thread(target=self.server.run, kwargs={"sockets": [self.socket]}, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + 10
        while self.thread.is_alive() and not self.server.started and time.monotonic() < deadline:
            time.sleep(0.05)
        if not self.server.started:
            self.close()
            raise RuntimeError("Remote transport did not start")
        return self.socket.getsockname()[1]

    def is_alive(self) -> bool:
        return self.thread is not None and self.thread.is_alive() and self.server.started

    def close(self):
        if self.server is not None:
            self.server.should_exit = True
        if self.thread is not None:
            self.thread.join(timeout=12)
            if self.thread.is_alive():
                raise RuntimeError("Remote transport did not stop")
        if self.socket is not None:
            self.socket.close()
