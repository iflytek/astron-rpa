"""Opt-in, isolated real-broker regression (CI supplies its own Redis service)."""

import asyncio
import multiprocessing
import os
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import ConnectionPool, Redis
from starlette.responses import JSONResponse

from app.services.execution_routing import ExecutionRouter, route_key


def peer_process(url, owner, pipe):
    async def run():
        calls = 0

        async def local_request(user, data, timeout, *, expected):
            nonlocal calls
            calls += 1
            return {"owner": user, "action": data["action"], "calls": calls}

        router = ExecutionRouter.from_url(SimpleNamespace(local_execution_request=local_request), url)
        await router.start()
        await router.register(owner, SimpleNamespace(ws=SimpleNamespace(close=lambda: None)))
        pipe.send({"ready": True, "instance": router.instance})
        try:
            while not pipe.poll():
                await asyncio.sleep(0.02)
            pipe.recv()
        finally:
            await router.stop()
            pipe.close()

    asyncio.run(run())


@pytest.mark.asyncio
async def test_real_redis_routes_between_processes_without_start_replay():
    url = os.environ["ASTRON_TEST_REDIS_URL"]  # Explicit opt-in; never use deployment REDIS_URL.
    owner = "synthetic-production-" + uuid.uuid4().hex
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe()
    process = context.Process(target=peer_process, args=(url, owner, child))
    process.start()

    async def forbidden(*args, **kwargs):
        pytest.fail("request must reach the other process")

    router = ExecutionRouter.from_url(SimpleNamespace(local_execution_request=forbidden), url)
    inspector = Redis.from_url(url, decode_responses=True)
    try:
        assert await asyncio.to_thread(parent.poll, 10), "isolated peer did not become ready"
        ready = parent.recv()
        assert ready["ready"]
        await router.start()
        assert router.instance != ready["instance"]
        replies = await asyncio.gather(*(router.request(owner, {"action": "get"}, 2) for _ in range(8)))
        assert {reply["calls"] for reply in replies} == set(range(1, 9))
        assert all(reply["owner"] == owner for reply in replies)
        assert 0 < await inspector.ttl(route_key(owner)) <= 30
        response = await router.request(owner, {"action": "start"}, 2)
        assert response["calls"] == 9
        parent.send("stop")
        await asyncio.to_thread(process.join, 5)
        assert not process.is_alive()
        assert await inspector.get(route_key(owner)) is None
        with pytest.raises(ConnectionError, match="CLIENT_OFFLINE"):
            await router.request(owner, {"action": "start"}, 0.2)
        assert not router.pending
    finally:
        if process.is_alive():
            parent.send("stop")
            await asyncio.to_thread(process.join, 5)
        if process.is_alive():
            process.terminate()
            await asyncio.to_thread(process.join, 3)
        parent.close()
        child.close()
        await router.stop()
        # This test owns only one random owner key. Never FLUSHDB.
        await inspector.delete(route_key(owner))
        await inspector.aclose()


@pytest.mark.asyncio
async def test_real_redis_rate_window_is_shared_by_transport_and_has_expiry(monkeypatch):
    import hashlib

    from app import redis as redis_module
    from app.security import integration_rate_limit as limiter
    from app.security.mcp_auth import MCPAPIKeyAuthMiddleware

    url = os.environ["ASTRON_TEST_REDIS_URL"]
    owner = "synthetic-limit-" + uuid.uuid4().hex
    pool = ConnectionPool.from_url(url, decode_responses=True)
    monkeypatch.setattr(redis_module, "redis_pool", pool)
    monkeypatch.setattr(limiter, "get_settings", lambda: SimpleNamespace(INTEGRATION_RATE_PER_MINUTE=2))
    key = "astron:rate:v1:" + hashlib.sha256(owner.encode()).hexdigest()
    redis = Redis(connection_pool=pool)
    endpoint = MCPAPIKeyAuthMiddleware(
        JSONResponse({"ok": True}), AsyncMock(return_value=owner), limiter=limiter.enforce_rate_limit
    )
    try:
        async with AsyncClient(transport=ASGITransport(endpoint), base_url="https://test") as client:
            headers = {"Authorization": "Bearer synthetic-test-key"}
            assert (await client.post("/mcp/", headers=headers)).status_code == 200
            await limiter.enforce_rate_limit(owner)  # Same hook as REST identity dependency.
            denied = await client.post("/mcp/", headers=headers)
            assert denied.status_code == 429
            assert denied.json() == {"detail": {"code": "RATE_LIMITED"}}
            assert 0 < int(denied.headers["Retry-After"]) <= 60
            assert 0 < await redis.ttl(key) <= 60
    finally:
        await redis.delete(key)
        await redis.aclose()
        await pool.disconnect()


@pytest.mark.asyncio
async def test_real_broker_connection_loss_does_not_replay_start():
    url = os.environ["ASTRON_TEST_REDIS_URL"]
    owner = "synthetic-reconnect-" + uuid.uuid4().hex
    name = "synthetic-router-" + uuid.uuid4().hex
    started, release = asyncio.Event(), asyncio.Event()
    calls = []

    async def local_request(user, data, timeout, *, expected):
        calls.append(data["action"])
        if data["action"] == "start":
            started.set()
            await release.wait()
        return {"action": data["action"]}

    manager = SimpleNamespace(local_execution_request=local_request)
    target = ExecutionRouter.from_url(manager, url)
    caller = ExecutionRouter(manager, Redis.from_url(url, decode_responses=True, client_name=name))
    inspector = Redis.from_url(url, decode_responses=True)
    try:
        await target.start()
        await caller.start()
        await target.register(owner, SimpleNamespace(ws=SimpleNamespace(close=AsyncMock())))
        pending = asyncio.create_task(caller.request(owner, {"action": "start"}, 10))
        await asyncio.wait_for(started.wait(), 3)
        subscriptions = [row for row in await inspector.client_list() if row["name"] == name and "P" in row["flags"]]
        assert len(subscriptions) == 1
        # Disconnect only this test's subscription, never the broker or another client.
        await inspector.client_kill_filter(_id=subscriptions[0]["id"])
        with pytest.raises(TimeoutError, match="ROUTING_UNCONFIRMED"):
            await pending
        assert not caller.ready
        release.set()
        async with asyncio.timeout(12):
            while not caller.ready:
                await asyncio.sleep(0.05)
        assert await caller.request(owner, {"action": "get"}, 3) == {"action": "get"}
        assert calls == ["start", "get"]
        assert not caller.pending
    finally:
        release.set()
        await caller.stop()
        await target.stop()
        await inspector.delete(route_key(owner))
        await inspector.aclose()
