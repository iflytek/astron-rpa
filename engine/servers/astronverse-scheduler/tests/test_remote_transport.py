import asyncio
import gzip
import hashlib
import json
import logging
import socket
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
import uvicorn
from astronverse.scheduler.core.route.remote_transport import RemoteTransport, create_app
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse, Response, StreamingResponse
from starlette.routing import Route, WebSocketRoute
from starlette.testclient import TestClient, WebSocketDenialResponse
from starlette.websockets import WebSocketDisconnect
from websockets.sync.client import connect


@contextmanager
def serve(app, cert=None, key=None):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            log_level="warning",
            access_log=False,
            ssl_certfile=cert,
            ssl_keyfile=key,
            timeout_graceful_shutdown=1,
        )
    )
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert server.started
        yield port
    finally:
        server.should_exit = True
        thread.join(4)
        sock.close()


@pytest.fixture
def certificates(tmp_path, monkeypatch):
    now = datetime.now(UTC)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Transport test CA")])
    ca = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
        .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    ca_path = tmp_path / "ca.pem"
    ca_path.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    monkeypatch.setenv("SSL_CERT_FILE", str(ca_path))
    pairs = {}
    for name in ["trusted", "wrong-host", "expired", "untrusted"]:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        issuer_key = key if name == "untrusted" else ca_key
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject if name == "untrusted" else ca_name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=2))
            .not_valid_after(now + timedelta(days=-1 if name == "expired" else 1))
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_key.public_key()), critical=False)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName("wrong.invalid" if name == "wrong-host" else "localhost")]),
                critical=False,
            )
            .sign(issuer_key, hashes.SHA256())
        )
        cert_path, key_path = tmp_path / (name + ".pem"), tmp_path / (name + ".key")
        cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
            )
        )
        pairs[name] = str(cert_path), str(key_path)
    return pairs


def upstream_app(events, secure=True):
    async def echo(request):
        events.append(request.url.path)
        return JSONResponse(
            {
                "cookie": request.headers.get("cookie", ""),
                "path": request.url.path,
                "query": request.url.query,
                "body": (await request.body()).decode(),
                "auth": request.headers.get("authorization"),
            }
        )

    async def login(request):
        response = JSONResponse({"logged_in": True})
        response.set_cookie("SESSION", "session-secret", secure=secure, httponly=True)
        return response

    async def logout(request):
        response = Response()
        response.delete_cookie("SESSION", secure=secure)
        return response

    async def stream(request):
        async def chunks():
            yield b"first\n"
            await asyncio.sleep(0.01)
            yield b"second\n"

        return StreamingResponse(chunks())

    async def compressed(request):
        return Response(gzip.compress(b"compressed response"), headers={"Content-Encoding": "gzip"})

    async def redirect(request):
        return RedirectResponse("http://untrusted.invalid/", status_code=307)

    async def ws(websocket):
        events.append("websocket")
        await websocket.accept()
        await websocket.send_text(websocket.headers.get("cookie", ""))
        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if message.get("bytes") is not None:
                    await websocket.send_bytes(message["bytes"])
                else:
                    await websocket.send_text(message["text"])
        except WebSocketDisconnect:
            pass

    return Starlette(
        routes=[
            Route("/api/login", login, methods=["POST"]),
            Route("/api/logout", logout, methods=["POST"]),
            Route("/api/echo", echo, methods=["GET", "POST"]),
            Route("/api/stream", stream),
            Route("/api/compressed", compressed),
            Route("/api/redirect", redirect),
            WebSocketRoute("/api/ws", ws),
        ]
    )


def test_https_session_streaming_and_wss(certificates, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    events = []
    with serve(upstream_app(events), *certificates["trusted"]) as port:
        base = f"https://localhost:{port}"
        directory = tmp_path / "cookies"
        with TestClient(create_app(base, directory)) as client:
            login = client.post("/api/login")
            assert login.status_code == 200
            assert "set-cookie" not in login.headers
            response = client.post(
                "/api/echo?key=query-secret",
                content="payload",
                headers={"Cookie": "SESSION=wrong-origin", "Authorization": "Bearer header-secret"},
            )
            assert response.json() == {
                "cookie": "SESSION=session-secret",
                "path": "/api/echo",
                "query": "key=query-secret",
                "body": "payload",
                "auth": "Bearer header-secret",
            }
            assert client.get("/api/stream").content == b"first\nsecond\n"
            assert client.get("/api/compressed").content == b"compressed response"
            assert client.get("/api/redirect", follow_redirects=False).status_code == 307
            with client.websocket_connect("/api/ws") as ws:
                assert ws.receive_text() == "SESSION=session-secret"
                ws.send_text("text")
                assert ws.receive_text() == "text"
                ws.send_bytes(b"\x00\xff")
                assert ws.receive_bytes() == b"\x00\xff"
        with TestClient(create_app(base, directory)) as client:
            assert client.get("/api/echo").json()["cookie"] == "SESSION=session-secret"
            assert client.post("/api/logout").status_code == 200
        with TestClient(create_app(base, directory)) as client:
            assert client.get("/api/echo").json()["cookie"] == ""
    assert all(secret not in caplog.text for secret in ["query-secret", "header-secret", "session-secret"])


@pytest.mark.parametrize("certificate", ["wrong-host", "expired", "untrusted"])
def test_rejects_bad_certificates_on_http_and_websocket(certificates, certificate, tmp_path):
    events = []
    with serve(upstream_app(events), *certificates[certificate]) as port:
        with TestClient(create_app(f"https://localhost:{port}", tmp_path / "cookies")) as client:
            response = client.get("/api/echo?token=must-not-echo")
            assert response.status_code == 502
            assert "must-not-echo" not in response.text
            with pytest.raises(WebSocketDisconnect):
                with client.websocket_connect("/api/ws"):
                    pytest.fail("Unverified upstream WebSocket was accepted")
    assert events == []


def test_explicit_http_and_origin_isolation(tmp_path):
    with serve(upstream_app([], secure=False)) as first, serve(upstream_app([], secure=False)) as second:
        directory = tmp_path / "cookies"
        with TestClient(create_app(f"http://localhost:{first}", directory)) as client:
            assert client.post("/api/login").status_code == 200
            assert client.get("/api/echo").json()["cookie"] == "SESSION=session-secret"
            with client.websocket_connect("/api/ws") as ws:
                assert ws.receive_text() == "SESSION=session-secret"
        with TestClient(create_app(f"http://localhost:{second}", directory)) as client:
            assert client.get("/api/echo").json()["cookie"] == ""
            assert client.get("/not-an-api").status_code == 404


def test_migrates_only_configured_origins_session(certificates, tmp_path):
    with serve(upstream_app([]), *certificates["trusted"]) as port:
        base = f"https://localhost:{port}"
        (tmp_path / ".cookie.json").write_text(
            json.dumps(
                {
                    f"localhost:{port}": {"SESSION": {"key_value": "SESSION=old-session", "path": "/"}},
                    "elsewhere.invalid": {"SESSION": {"key_value": "SESSION=foreign-session", "path": "/"}},
                }
            )
        )
        directory = tmp_path / "cookies"
        with TestClient(create_app(base, directory)) as client:
            assert client.get("/api/echo").json()["cookie"] == "SESSION=old-session"
            client.post("/api/logout")
        with TestClient(create_app(base, directory)) as client:
            assert client.get("/api/echo").json()["cookie"] == ""


@pytest.mark.parametrize(
    "case", ["invalid-json", "invalid-root", "invalid-origin", "invalid-entry", "no-value", "bad-value"]
)
def test_malformed_legacy_session_allows_fresh_login(tmp_path, case):
    with serve(upstream_app([], secure=False)) as port:
        entries = {
            "invalid-json": "{broken-json",
            "invalid-root": "[]",
            "invalid-origin": json.dumps({f"localhost:{port}": []}),
            "invalid-entry": json.dumps({f"localhost:{port}": {"SESSION": []}}),
            "no-value": json.dumps({f"localhost:{port}": {"SESSION": {}}}),
            "bad-value": json.dumps({f"localhost:{port}": {"SESSION": {"key_value": 123}}}),
        }
        (tmp_path / ".cookie.json").write_text(entries[case], encoding="utf-8")
        with TestClient(create_app(f"http://localhost:{port}", tmp_path / "cookies")) as client:
            assert client.get("/api/echo").json()["cookie"] == ""
            assert client.post("/api/login").status_code == 200
            assert client.get("/api/echo").json()["cookie"] == "SESSION=session-secret"


def test_damaged_session_does_not_restore_legacy_or_log_values(tmp_path, caplog, recwarn):
    with serve(upstream_app([], secure=False)) as port:
        base = f"http://localhost:{port}"
        directory = tmp_path / "cookies"
        directory.mkdir()
        (tmp_path / ".cookie.json").write_text(
            json.dumps({f"localhost:{port}": {"SESSION": {"key_value": "legacy-private-value"}}})
        )
        cookie_file = directory / (hashlib.sha256(base.encode()).hexdigest() + ".cookies")
        cookie_file.write_text(
            "#LWP-Cookies-2.0\nSet-Cookie3: SESSION=damaged-private-value; domain=localhost.local; "
            'path="/"; version=private-invalid-version\n'
        )
        for _ in range(2):
            with TestClient(create_app(base, directory)) as client:
                assert client.get("/api/echo").json()["cookie"] == ""
        diagnostic = caplog.text + " ".join(str(w.message) for w in recwarn)
        assert "private" not in diagnostic


def test_websocket_redirect_does_not_forward_credentials(certificates, tmp_path):
    events = []
    with serve(upstream_app(events), *certificates["trusted"]) as other_port:

        async def redirect(websocket):
            await websocket.send_denial_response(RedirectResponse(f"wss://localhost:{other_port}/api/ws"))

        async def denied(websocket):
            await websocket.send_denial_response(Response(status_code=401))

        app = upstream_app([])
        app.routes.extend([WebSocketRoute("/redirect", redirect), WebSocketRoute("/denied", denied)])
        with serve(app, *certificates["trusted"]) as port:
            with TestClient(create_app(f"https://localhost:{port}", tmp_path / "cookies")) as client:
                assert client.post("/api/login").status_code == 200
                for path, status in [("/redirect", 502), ("/denied", 401)]:
                    with pytest.raises(WebSocketDenialResponse) as error:
                        with client.websocket_connect(path, headers={"Authorization": "Bearer private"}):
                            pytest.fail("Rejected handshake was accepted")
                    assert error.value.status_code == status
    assert events == []


@pytest.mark.skipif(sys.platform != "win32", reason="Bundled Windows router compatibility")
@pytest.mark.parametrize(("certificate", "expected"), [("trusted", 200), ("wrong-host", 502)])
def test_bundled_router_uses_verified_transport_and_preserves_local_routes(
    certificates, certificate, expected, tmp_path, monkeypatch
):
    executable = Path(__file__).parents[1] / "src/astronverse/scheduler/core/route/win/route.exe"
    monkeypatch.chdir(tmp_path)
    with serve(upstream_app([]), *certificates[certificate]) as upstream, serve(upstream_app([], False)) as local:
        relay = RemoteTransport(f"https://localhost:{upstream}")
        relay_port = relay.start()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            router_port = sock.getsockname()[1]
        process = subprocess.Popen(
            [
                str(executable),
                f"--port={router_port}",
                "--httpProtocol=http",
                "--wsProtocol=ws",
                f"--remoteHost=127.0.0.1:{relay_port}",
            ],
            cwd=tmp_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            base = f"http://127.0.0.1:{router_port}"
            for _ in range(100):
                try:
                    if httpx.get(base + "/rpa-local-route/health").status_code == 200:
                        break
                except httpx.ConnectError:
                    pass
                time.sleep(0.02)
            assert httpx.get(base + "/api/echo").status_code == expected
            registered = httpx.post(
                base + "/rpa-local-route/registry", json={"module_name": "scheduler", "port": str(local)}
            )
            assert "OK" in registered.text
            assert httpx.get(base + "/scheduler/api/echo").json()["path"] == "/api/echo"
            if expected == 200:
                with connect(f"ws://127.0.0.1:{router_port}/api/ws", proxy=None) as ws:
                    assert ws.recv() == ""
                    ws.send("through router")
                    assert ws.recv() == "through router"
                    # Consecutive result messages must retain their boundaries.
                    messages = [json.dumps({"id": i, "msg": "运行结果"}) for i in range(30)]
                    for message in messages:
                        ws.send(message)
                    assert [ws.recv(timeout=5) for _ in messages] == messages
        finally:
            process.terminate()
            process.wait(5)
            relay.close()
