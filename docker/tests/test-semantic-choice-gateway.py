#!/usr/bin/env python3
"""Exercise production gateway routes against the real semantic-choice API.

Run with backend/ai-service's Python environment; Docker must already have the
OPENRESTY_IMAGE (default: openresty/openresty:1.27.1.1-alpine). No paid API calls.
"""

import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import uvicorn
from fastapi import FastAPI, Request

ROOT = Path(__file__).resolve().parents[2]
IMAGE = os.environ.get("OPENRESTY_IMAGE", "openresty/openresty:1.27.1.1-alpine")
PAYLOAD = {
    "instruction": "Select the matching ticket category.",
    "text": "Please refund the duplicate payment.",
    "options": [{"id": "refund", "label": "Refund"}],
}


def docker(*args, check=True):
    result = subprocess.run(
        ["docker", *args], check=False, text=True, capture_output=True, timeout=60
    )
    if check and result.returncode:
        raise RuntimeError(f"docker {' '.join(args)} failed: {result.stderr}")
    return (result.stdout + (result.stderr if args[0] == "logs" else "")).strip()


def build_app(log_dir):
    # Override, rather than inherit, local deployment credentials.
    os.environ.update(
        DATABASE_URL="mysql+aiomysql://smoke:smoke@127.0.0.1:1/smoke",
        DATABASE_USERNAME="smoke",
        DATABASE_PASSWORD="smoke",
        REDIS_URL="redis://127.0.0.1:1/0",
        AICHAT_BASE_URL="https://chat.invalid/v1/",
        AICHAT_API_KEY="smoke",
        CUA_BASE_URL="https://cua.invalid/v1/",
        CUA_API_KEY="smoke",
        XFYUN_APP_ID="smoke",
        XFYUN_API_SECRET="smoke",
        XFYUN_API_KEY="smoke",
        JFBYM_API_TOKEN="smoke",
        JEV_API_KEY="smoke-never-sent-to-network",
        JEV_MODEL="jev-latest",
        JEV_TIMEOUT_SECONDS="10",
        JEV_POINTS_COST="100",
        LOG_DIR=str(log_dir),
    )
    sys.path.insert(0, str(ROOT / "backend/ai-service"))
    from app.dependencies import get_user_point_service
    from app.routers.v1.decision import router

    state = SimpleNamespace(
        choice="candidate_0",
        provider_status=200,
        provider_calls=[],
        arrivals=[],
        points=SimpleNamespace(
            grant_monthly_points=AsyncMock(),
            get_cached_points=AsyncMock(return_value=10000),
            deduct_points=AsyncMock(),
        ),
    )

    def provider(request):
        state.provider_calls.append(request)
        return httpx.Response(
            state.provider_status,
            json={
                "answers": {
                    "selection": {
                        "type": "choice",
                        "choice": state.choice,
                        "confidence": 0.9,
                    }
                }
            },
        )

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            app.state.jev_http_client = client
            yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(router, prefix="/v1")
    # Keep the production PointChecker and get_user_id_from_header dependencies.
    app.dependency_overrides[get_user_point_service] = lambda: state.points

    @app.middleware("http")
    async def capture_identity(request: Request, call_next):
        state.arrivals.append((request.url.path, dict(request.headers)))
        return await call_next(request)

    @app.get("/v1/smoke-sibling")
    def sibling():
        return {"route": "generic-ai-sibling"}

    return app, state


def gateway_config(port):
    upstreams = "\n".join(
        f"upstream {name} {{ server host.docker.internal:{port}; }}"
        for name in (
            "resource-service",
            "ai-service",
            "openapi-service",
            "rpa-auth-service",
            "casdoor",
        )
    )
    return f"""worker_processes 1;
events {{ worker_connections 64; }}
http {{
    resolver 127.0.0.11 ipv6=off;
    lua_package_path "/usr/local/openresty/nginx/lua/?.lua;;";
    upstream robot-service {{ server robot-service:8040; }}
    {upstreams}
    server {{
        listen 8080;
        set $context_type "HTTP";
        include /etc/smoke/gateway-routes.conf;
    }}
}}
"""


MOCK_AUTH = """worker_processes 1;
events { worker_connections 32; }
http {
    server {
        listen 8040;
        location = /api/robot/user/info {
            default_type application/json;
            content_by_lua_block {
                local c = ngx.var.http_cookie or ""
                if c == "SESSION=valid-token" or c == "JSESSIONID=valid-token" then
                    ngx.say('{"code":"000000","data":{"id":"real-user"}}')
                else
                    ngx.say('{"code":"000000","data":null}')
                end
            }
        }
    }
}
"""


def check_requests(base_url, state):
    spoofed = {
        "user_id": "attacker",
        "X-User-Id": "attacker",
        "user-info": '{"id":"attacker"}',
    }
    with httpx.Client(base_url=base_url, timeout=10, trust_env=False) as client:

        def choice(headers, query=""):
            return client.post(
                "/api/rpa-ai-service/v1/decision/choice" + query,
                headers={**spoofed, **headers},
                json=PAYLOAD,
            )

        for headers in (
            {"Token": "valid-token"},
            {"Cookie": "SESSION=valid-token"},
            {"Cookie": "JSESSIONID=valid-token"},
        ):
            before = state.points.deduct_points.await_count
            response = choice(headers)
            assert response.status_code == 200, response.text
            assert response.json() == {
                "status": "matched",
                "selected_id": "refund",
                "confidence": 0.9,
            }
            assert state.points.deduct_points.await_count == before + 1
            assert (
                state.points.deduct_points.await_args.kwargs["user_id"] == "real-user"
            )
            assert state.points.deduct_points.await_args.kwargs["amount"] == 100
            assert state.points.grant_monthly_points.await_args.args == ("real-user",)
            path, forwarded = state.arrivals[-1]
            assert path == "/v1/decision/choice"
            assert forwarded["user_id"] == "real-user"
            assert "x-user-id" not in forwarded
            assert '"real-user"' in forwarded["user-info"]
        print(
            "PASS token, SESSION and JSESSIONID: real identity, rewrite, match and single deduction"
        )

        for headers, query in (
            ({}, ""),
            ({"Token": "expired-token"}, ""),
            ({"Authorization": "Bearer arbitrary"}, ""),
            ({"X-API-Key": "arbitrary"}, ""),
            ({}, "?key=arbitrary"),
            (
                {"Cookie": "SESSION=valid-token", "Authorization": "Bearer arbitrary"},
                "",
            ),
        ):
            before = (
                len(state.arrivals),
                len(state.provider_calls),
                state.points.deduct_points.await_count,
            )
            response = choice(headers, query=query)
            assert response.status_code == 401, response.text
            assert before == (
                len(state.arrivals),
                len(state.provider_calls),
                state.points.deduct_points.await_count,
            )
        print(
            "PASS six rejected credential cases: no backend entry, inference or deduction"
        )

        state.choice = "__abstain__"
        before = state.points.deduct_points.await_count
        response = choice({"Token": "valid-token"})
        assert response.status_code == 200, response.text
        assert response.json() == {
            "status": "abstain",
            "selected_id": None,
            "confidence": 0.9,
        }
        assert state.points.deduct_points.await_count == before + 1
        print("PASS abstention: valid result charged once")

        state.provider_status = 529
        before = state.points.deduct_points.await_count
        calls = len(state.provider_calls)
        response = choice({"Token": "valid-token"})
        assert response.status_code == 502, response.text
        assert response.json()["detail"] == "Semantic choice provider request failed"
        assert len(state.provider_calls) == calls + 1
        assert state.points.deduct_points.await_count == before
        print("PASS provider failure: one attempt, sanitized error, no deduction")

        # The existing sibling route accepts Bearer; only the longer decision
        # location should reject it. This detects accidental broad route changes.
        response = client.get(
            "/api/rpa-ai-service/v1/smoke-sibling",
            headers={"Authorization": "Bearer arbitrary"},
        )
        assert response.status_code == 200, response.text
        assert response.json() == {"route": "generic-ai-sibling"}
        print("PASS generic AI sibling selects its existing production location")


def main():
    # Never implicitly pull: keep this check deterministic and usable offline.
    docker("image", "inspect", IMAGE)
    name = "astron-choice-smoke-" + uuid4().hex[:10]
    network, auth, gateway = name, name + "-auth", name + "-gateway"
    server = thread = None
    with tempfile.TemporaryDirectory(prefix=name) as directory:
        work = Path(directory)
        sock = socket.socket()
        try:
            # Only synthetic fixtures are served; Docker needs a host-reachable listener.
            sock.bind(("0.0.0.0", 0))
            port = sock.getsockname()[1]
            app, state = build_app(work)
            server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
            thread = threading.Thread(
                target=server.run, kwargs={"sockets": [sock]}, daemon=True
            )
            thread.start()
            deadline = time.monotonic() + 10
            while not server.started:
                if not thread.is_alive() or time.monotonic() > deadline:
                    raise RuntimeError("Fixture backend failed to start")
                time.sleep(0.05)
            (work / "gateway.conf").write_text(gateway_config(port))
            (work / "auth.conf").write_text(MOCK_AUTH)
            docker("network", "create", network)
            docker(
                "run",
                "-d",
                "--pull=never",
                "--name",
                auth,
                "--network",
                network,
                "--network-alias",
                "robot-service",
                "-v",
                f"{work}/auth.conf:/usr/local/openresty/nginx/conf/nginx.conf:ro",
                IMAGE,
            )
            docker(
                "run",
                "-d",
                "--pull=never",
                "--name",
                gateway,
                "--network",
                network,
                "--add-host",
                "host.docker.internal:host-gateway",
                "-p",
                "127.0.0.1::8080",
                "-v",
                f"{work}/gateway.conf:/usr/local/openresty/nginx/conf/nginx.conf:ro",
                "-v",
                f"{ROOT}/docker/volumes/nginx/lua:/usr/local/openresty/nginx/lua:ro",
                "-v",
                f"{ROOT}/docker/volumes/nginx/includes/gateway-routes.conf:/etc/smoke/gateway-routes.conf:ro",
                IMAGE,
            )
            docker("exec", gateway, "nginx", "-t")
            published = docker("port", gateway, "8080/tcp").rsplit(":", 1)[1]
            base = f"http://127.0.0.1:{published}"
            for _ in range(40):
                try:
                    if (
                        httpx.get(
                            base + "/health", timeout=1, trust_env=False
                        ).status_code
                        == 200
                    ):
                        break
                except httpx.TransportError:
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("Fixture gateway failed to start")
            check_requests(base, state)
            print(
                "PASS 12 production-route smoke cases (mock auth, provider and points store)"
            )
        except BaseException:
            for container in (gateway, auth):
                print(docker("logs", container, check=False), file=sys.stderr)
            raise
        finally:
            docker("rm", "-f", gateway, auth, check=False)
            docker("network", "rm", network, check=False)
            if server:
                server.should_exit = True
            if thread:
                thread.join(timeout=10)
            sock.close()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    main()
