"""Broker transport unit regressions; deployment smoke also uses real Redis."""

import asyncio
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.execution_routing import MAX_PENDING, PREFIX, ExecutionRouter, route_key


class Broker:
    def __init__(self):
        self.values = {}
        self.subscribers = {}
        self.publications = []

    def client(self):
        broker = self

        class Subscription:
            subscribed = False

            def __init__(self):
                self.queue = asyncio.Queue()

            async def subscribe(self, channel):
                self.channel = channel
                broker.subscribers[channel] = self
                self.subscribed = True
                await self.queue.put({"type": "subscribe"})

            async def get_message(self, **kwargs):
                try:
                    return await asyncio.wait_for(self.queue.get(), kwargs.get("timeout", 1))
                except TimeoutError:
                    return None

            async def aclose(self):
                broker.subscribers.pop(self.channel, None)
                self.subscribed = False

        async def get(key):
            return broker.values.get(key)

        async def put(key, value, **kwargs):
            assert kwargs.get("ex") == 30
            broker.values[key] = value

        async def publish(channel, payload):
            broker.publications.append((channel, json.loads(payload)))
            subscriber = broker.subscribers.get(channel)
            if subscriber:
                await subscriber.queue.put({"type": "message", "data": payload})
            return int(subscriber is not None)

        async def evaluate(script, count, key, generation, *args):
            if broker.values.get(key) != generation:
                return 0
            if "'del'" in script:
                broker.values.pop(key)
            return 1

        return SimpleNamespace(
            ping=AsyncMock(return_value=True),
            get=get,
            set=put,
            publish=publish,
            eval=evaluate,
            pubsub=Subscription,
            aclose=AsyncMock(),
        )


@pytest.fixture
def broker():
    return Broker()


async def start(broker, result=None):
    manager = SimpleNamespace(local_execution_request=AsyncMock(return_value=result or {"protocol": 1}))
    router = ExecutionRouter(manager, broker.client())
    await router.start()
    return router


@pytest.mark.asyncio
async def test_cross_worker_request_and_receipt_have_exact_owner_connection(broker):
    first, second = await start(broker), await start(broker, {"executionId": "exec", "status": "running"})
    conn = object()
    try:
        await second.register("owner", conn)
        result = await first.request("owner", {"action": "start", "executionId": "exec"}, 1)
        assert result["executionId"] == "exec"
        assert first.manager.local_execution_request.await_count == 0
        call = second.manager.local_execution_request.call_args
        assert call.args[:2] == ("owner", {"action": "start", "executionId": "exec"})
        assert call.kwargs == {"expected": conn}
        assert len(broker.publications) == 2
        assert not first.pending
        assert not second.pending
    finally:
        await first.stop()
        await second.stop()


@pytest.mark.asyncio
async def test_new_connection_fences_old_disconnect_and_stale_messages(broker):
    first, second = await start(broker), await start(broker)
    try:
        old = await first.register("owner", object())
        new = await second.register("owner", object())
        await first.unregister("owner", old)
        assert broker.values[route_key("owner")] == new
        await first._handle(
            {
                "kind": "request",
                "id": "old",
                "owner": "owner",
                "generation": old,
                "deadline": time.time() + 1,
                "data": {"action": "start"},
                "source": second.instance,
            }
        )
        assert first.manager.local_execution_request.await_count == 0
        await first.request("owner", {"action": "capabilities"}, 1)
        assert second.manager.local_execution_request.await_count == 1
    finally:
        await first.stop()
        await second.stop()


@pytest.mark.asyncio
async def test_same_worker_replacement_closes_old_socket_without_losing_new_route(broker):
    router = await start(broker)
    old_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    new_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    try:
        old = await router.register("owner", old_conn)
        new = await router.register("owner", new_conn)
        old_conn.ws.close.assert_awaited_once()
        new_conn.ws.close.assert_not_awaited()
        await router.unregister("owner", old)
        assert broker.values[route_key("owner")] == new
        assert router.local["owner"] == (new, new_conn)
        await router._handle(
            {"owner": "owner", "generation": old, "deadline": time.time() + 1, "data": {"action": "start"}}
        )
        router.manager.local_execution_request.assert_not_awaited()
        await router.request("owner", {"action": "capabilities"}, 1)
        assert router.manager.local_execution_request.call_args.kwargs == {"expected": new_conn}
        await router.unregister("owner", new)
        assert not router.local
        assert route_key("owner") not in broker.values
    finally:
        await router.stop()


@pytest.mark.asyncio
async def test_same_owner_registration_serializes_broker_replies_without_blocking_other_owners(broker):
    router = await start(broker)
    entered, release = asyncio.Event(), asyncio.Event()
    original_set = router.redis.set
    calls = []

    async def delayed_set(key, generation, **kwargs):
        calls.append(key)
        await original_set(key, generation, **kwargs)
        if key == route_key("owner") and calls.count(key) == 1:
            entered.set()
            await release.wait()

    router.redis.set = delayed_set
    old_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    new_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    tasks = [asyncio.create_task(router.register("owner", old_conn))]
    try:
        await asyncio.wait_for(entered.wait(), 1)
        tasks.append(asyncio.create_task(router.register("owner", new_conn)))
        await asyncio.sleep(0)
        assert calls.count(route_key("owner")) == 1
        await asyncio.wait_for(router.register("other", object()), 1)
        release.set()
        old, new = await asyncio.gather(*tasks)
        await router.unregister("owner", old)
        assert broker.values[route_key("owner")] == new
        assert router.local["owner"] == (new, new_conn)
        assert not router.registration_locks
        old_conn.ws.close.assert_awaited_once()
        new_conn.ws.close.assert_not_awaited()
    finally:
        release.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        await router.stop()


@pytest.mark.asyncio
async def test_failed_replacement_keeps_existing_socket_and_route(broker):
    router = await start(broker)
    conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    try:
        old = await router.register("owner", conn)
        router.redis.set = AsyncMock(side_effect=ConnectionError("broker unavailable"))
        with pytest.raises(ConnectionError):
            await router.register("owner", object())
        assert router.local["owner"] == (old, conn)
        assert broker.values[route_key("owner")] == old
        conn.ws.close.assert_not_awaited()
        assert not router.registration_locks
    finally:
        await router.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("close_fails", [False, True])
async def test_old_socket_cleanup_cannot_unregister_newer_reconnect(broker, close_fails):
    router = await start(broker)
    entered, release = asyncio.Event(), asyncio.Event()
    old_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    middle = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    latest = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    task = None
    try:
        old = await router.register("owner", old_conn)

        async def close():
            entered.set()
            await release.wait()
            await router.unregister("owner", old)
            if close_fails:
                raise OSError("already disconnected")

        old_conn.ws.close.side_effect = close
        task = asyncio.create_task(router.register("owner", middle))
        await asyncio.wait_for(entered.wait(), 1)
        new = await router.register("owner", latest)
        release.set()
        superseded = await task
        await router.unregister("owner", superseded)
        assert router.local["owner"] == (new, latest)
        assert broker.values[route_key("owner")] == new
        middle.ws.close.assert_awaited_once()
        latest.ws.close.assert_not_awaited()
    finally:
        release.set()
        if task:
            await asyncio.gather(task, return_exceptions=True)
        await router.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("reconnect_again", [False, True])
async def test_cancelled_replacement_releases_only_its_own_route(broker, reconnect_again):
    router = await start(broker)
    entered = asyncio.Event()

    async def blocked_close():
        entered.set()
        await asyncio.Event().wait()

    old_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock(side_effect=blocked_close)))
    new_conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock()))
    task = None
    try:
        await router.register("owner", old_conn)
        task = asyncio.create_task(router.register("owner", new_conn))
        await asyncio.wait_for(entered.wait(), 1)
        if reconnect_again:
            latest_conn = object()
            latest = await router.register("owner", latest_conn)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not router.registration_locks
        if reconnect_again:
            assert router.local["owner"] == (latest, latest_conn)
            assert broker.values[route_key("owner")] == latest
        else:
            assert not router.local
            assert route_key("owner") not in broker.values
    finally:
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await router.stop()


@pytest.mark.asyncio
async def test_replacement_close_is_bounded(broker):
    router = await start(broker)
    conn = SimpleNamespace(ws=SimpleNamespace(close=AsyncMock(side_effect=asyncio.Event().wait)))
    try:
        await router.register("owner", conn)
        latest = object()
        new = await asyncio.wait_for(router.register("owner", latest), 3)
        assert router.local["owner"] == (new, latest)
        assert broker.values[route_key("owner")] == new
        conn.ws.close.assert_awaited_once()
    finally:
        await router.stop()


@pytest.mark.asyncio
async def test_missing_route_and_lost_worker_never_fall_back_or_replay(broker):
    router = await start(broker)
    try:
        with pytest.raises(ConnectionError, match="CLIENT_OFFLINE"):
            await router.request("absent", {"action": "start"}, 0.1)
        broker.values[route_key("lost")] = "dead:connection"
        with pytest.raises(TimeoutError):
            await router.request("lost", {"action": "start"}, 0.1)
        assert len(broker.publications) == 1
        assert router.manager.local_execution_request.await_count == 0
        assert not router.pending
    finally:
        await router.stop()


@pytest.mark.asyncio
async def test_lost_reply_leaves_exactly_one_start(broker):
    first, second = await start(broker), await start(broker)
    try:
        await second.register("owner", object())
        second._publish = AsyncMock(side_effect=OSError("lost reply"))
        with pytest.raises(TimeoutError):
            await first.request("owner", {"action": "start"}, 0.1)
        assert second.manager.local_execution_request.await_count == 1
        assert len(broker.publications) == 1
        assert not first.pending
    finally:
        await first.stop()
        await second.stop()


@pytest.mark.asyncio
async def test_expired_request_never_reaches_client_and_pending_is_bounded(broker):
    router = await start(broker)
    try:
        generation = await router.register("owner", object())
        await router._handle(
            {"owner": "owner", "generation": generation, "deadline": time.time() - 1, "data": {"action": "start"}}
        )
        assert router.manager.local_execution_request.await_count == 0
        router.pending = {
            str(i): ("generation", asyncio.get_running_loop().create_future()) for i in range(MAX_PENDING)
        }
        with pytest.raises(TimeoutError, match="ROUTING_UNAVAILABLE"):
            await router.request("owner", {"action": "start"}, 1)
        for _, future in router.pending.values():
            future.cancel()
        router.pending.clear()
    finally:
        await router.stop()


@pytest.mark.asyncio
async def test_wrong_generation_reply_cannot_complete_pending_request(broker):
    router = await start(broker)
    try:
        future = asyncio.get_running_loop().create_future()
        router.pending["request"] = ("expected", future)
        await router.redis.publish(
            PREFIX + "worker:" + router.instance,
            json.dumps({"kind": "reply", "id": "request", "generation": "other", "ok": True}),
        )
        await asyncio.sleep(0.01)
        assert not future.done()
        future.cancel()
        router.pending.clear()
    finally:
        await router.stop()


@pytest.mark.asyncio
async def test_simultaneous_lookups_cannot_bypass_pending_limit(broker):
    router = await start(broker)
    gate = asyncio.Event()
    original_get = router.redis.get

    async def blocked_get(key):
        await gate.wait()
        return await original_get(key)

    router.redis.get = blocked_get
    tasks = [asyncio.create_task(router.request("absent", {"action": "start"}, 2)) for _ in range(100)]
    try:
        await asyncio.sleep(0.01)
        assert len(router.pending) == MAX_PENDING
        assert sum(task.done() for task in tasks) == 100 - MAX_PENDING
        gate.set()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        assert all(isinstance(result, (TimeoutError, ConnectionError)) for result in results)
        assert not router.pending
        assert router.manager.local_execution_request.await_count == 0
    finally:
        gate.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        await router.stop()
