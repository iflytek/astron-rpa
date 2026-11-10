import pytest
from astronverse.scheduler.apis import access_control
from astronverse.scheduler.apis.access_control import (
    ALLOWED_ORIGINS,
    is_allowed_origin,
    is_allowed_websocket_origin,
    local_access_guard,
)
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


def _client():
    app = FastAPI()
    app.middleware("http")(local_access_guard)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/pip/install")
    def pip_install():
        return {"ok": True}

    @app.post("/executor/run")
    def executor_run():
        return {"ok": True}

    @app.websocket("/ws/ws")
    async def ws_endpoint(ws: WebSocket):
        if not is_allowed_websocket_origin(ws):
            await ws.close(code=1008)
            return
        await ws.accept()
        await ws.send_text("ok")
        await ws.close()

    # TestClient reports the client host as "testclient"; treat it as loopback
    return TestClient(app, client=("127.0.0.1", 50000))


@pytest.mark.parametrize("origin", [None, "rpa://localhost", "rpa://localhost/", "http://localhost:1420"])
def test_is_allowed_origin_accepts_desktop_and_non_browser(origin):
    assert is_allowed_origin(origin)


@pytest.mark.parametrize("origin", ["null", "https://evil.example", "http://localhost:8080", "rpa://evil"])
def test_is_allowed_origin_rejects_other_origins(origin):
    assert not is_allowed_origin(origin)


def test_request_without_origin_is_allowed():
    with _client() as client:
        assert client.post("/pip/install").status_code == 200


def test_request_from_desktop_origin_is_allowed():
    with _client() as client:
        response = client.post("/pip/install", headers={"Origin": "rpa://localhost"})
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "rpa://localhost"


@pytest.mark.parametrize("origin", ["https://evil.example", "null"])
def test_request_from_foreign_origin_is_rejected(origin):
    with _client() as client:
        response = client.post("/pip/install", headers={"Origin": origin})
        assert response.status_code == 403


def test_remote_allowed_prefix_still_checks_origin():
    with _client() as client:
        response = client.post("/executor/run", headers={"Origin": "https://evil.example"})
        assert response.status_code == 403


def test_remote_allowed_prefix_requires_scheduler_token(monkeypatch):
    monkeypatch.setattr(access_control, "_remote_api_token", lambda: "test-token")
    app = FastAPI()
    app.middleware("http")(local_access_guard)

    @app.post("/executor/run")
    def executor_run():
        return {"ok": True}

    client = TestClient(app, client=("192.0.2.10", 50000))
    assert client.post("/executor/run").status_code == 401
    assert client.post("/executor/run", headers={"X-Scheduler-Token": "wrong"}).status_code == 401
    assert client.post("/executor/run", headers={"X-Scheduler-Token": "test-token"}).status_code == 200


def test_websocket_from_foreign_origin_is_closed():
    with _client() as client:
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect("/ws/ws", headers={"Origin": "https://evil.example"}) as ws:
                ws.receive_text()
        assert exc.value.code == 1008


def test_websocket_without_origin_is_accepted():
    with _client() as client:
        with client.websocket_connect("/ws/ws") as ws:
            assert ws.receive_text() == "ok"
