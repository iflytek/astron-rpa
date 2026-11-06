"""Ephemeral Redis routing to the process holding a Client WebSocket.

Pub/sub deliberately has no replay. Lost publication/reply remains unconfirmed;
the durable execution service alone owns NEW -> SENT and never resends start.
Redis must be private, authenticated, and shared by the participating replicas.
"""

import asyncio
import contextlib
import hashlib
import json
import time
import uuid

from redis.asyncio import Redis

from app.middlewares.tracing import correlation_ctx, get_request_id, request_id_ctx_var, safe_id

PREFIX = "astron:execution:v1:"
LEASE_SECONDS = 30
MAX_PENDING = 64
MAX_MESSAGE_BYTES = 4 * 1024 * 1024
_RENEW = "if redis.call('get',KEYS[1]) == ARGV[1] then return redis.call('expire',KEYS[1],ARGV[2]) else return 0 end"
_REMOVE = "if redis.call('get',KEYS[1]) == ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end"


def route_key(owner):
    return PREFIX + "owner:" + hashlib.sha256(str(owner).encode()).hexdigest()


class ExecutionRouter:
    def __init__(self, manager, redis):
        self.manager = manager
        self.redis = redis
        self.instance = uuid.uuid4().hex
        self.channel = PREFIX + "worker:" + self.instance
        self.local = {}  # owner -> (connection generation, connection)
        self.registration_locks = {}  # owner -> (lock, active/waiting registrations)
        self.pending = {}
        self.tasks = set()
        self.ready = False
        self.subscribed = False
        self.listener = None
        self.heartbeat = None
        self.pubsub = None

    @classmethod
    def from_url(cls, manager, url):
        return cls(manager, Redis.from_url(url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2))

    async def start(self):
        await self.redis.ping()
        await self._subscribe()
        self.listener = asyncio.create_task(self._listen(), name="execution-routing")
        self.heartbeat = asyncio.create_task(self._renew(), name="execution-route-leases")

    async def _subscribe(self):
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(self.channel)
        # Await the subscription ACK before advertising routes or sending RPCs.
        async with asyncio.timeout(3):
            while True:
                message = await self.pubsub.get_message(ignore_subscribe_messages=False, timeout=1)
                if message and message["type"] == "subscribe":
                    break
        self.ready = True
        self.subscribed = True

    async def stop(self):
        self.ready = False
        self.subscribed = False
        for task in (self.listener, self.heartbeat, *self.tasks):
            if task:
                task.cancel()
        await asyncio.gather(*(t for t in (self.listener, self.heartbeat, *self.tasks) if t), return_exceptions=True)
        for owner, (generation, _) in list(self.local.items()):
            with contextlib.suppress(Exception):
                await self.redis.eval(_REMOVE, 1, route_key(owner), generation)
        for _, future in self.pending.values():
            if not future.done():
                future.set_exception(TimeoutError("ROUTING_UNCONFIRMED"))
        if self.pubsub:
            await self.pubsub.aclose()
        await self.redis.aclose()

    async def register(self, owner, conn):
        owner = str(owner)
        lock, users = self.registration_locks.get(owner, (asyncio.Lock(), 0))
        self.registration_locks[owner] = (lock, users + 1)
        try:
            # Concurrent Redis replies can arrive out of order. Serialize each
            # owner's publication and local update, but never another owner's
            # registration or the old socket's potentially slow close.
            async with lock:
                if not self.ready:
                    raise ConnectionError("ROUTING_UNAVAILABLE")
                generation = self.instance + ":" + uuid.uuid4().hex
                await self.redis.set(route_key(owner), generation, ex=LEASE_SECONDS)
                previous = self.local.get(owner)
                self.local[owner] = (generation, conn)
        finally:
            _, users = self.registration_locks[owner]
            if users == 1:
                self.registration_locks.pop(owner)
            else:
                self.registration_locks[owner] = (lock, users - 1)
        try:
            if previous is not None and previous[1] is not conn:
                # Publish the new generation first: closing the old socket can run
                # its unregister callback, which must not remove the new route.
                # The old socket is no longer in local and will not be lease-swept.
                with contextlib.suppress(Exception):
                    async with asyncio.timeout(2):
                        await previous[1].ws.close()
        except asyncio.CancelledError:
            # listen() has not received this generation yet and cannot release
            # it itself if registration is cancelled during old-peer cleanup.
            await self.unregister(owner, generation)
            raise
        return generation

    async def unregister(self, owner, generation):
        if self.local.get(str(owner), (None,))[0] == generation:
            self.local.pop(str(owner), None)
        with contextlib.suppress(Exception):
            await self.redis.eval(_REMOVE, 1, route_key(owner), generation)

    async def online(self, owner):
        if not self.ready:
            return False
        return bool(await self.redis.get(route_key(owner)))

    async def request(self, owner, data, timeout):
        if not self.ready or len(self.pending) >= MAX_PENDING:
            raise TimeoutError("ROUTING_UNAVAILABLE")
        timeout = min(max(float(timeout), 0.1), 120)
        request_id = uuid.uuid4().hex
        future = asyncio.get_running_loop().create_future()
        # Reserve before the first await so simultaneous Redis lookups cannot
        # bypass the capacity bound.
        self.pending[request_id] = (None, future)
        try:
            async with asyncio.timeout(timeout):
                generation = await self.redis.get(route_key(owner))
                if not self.ready:
                    raise TimeoutError("ROUTING_UNAVAILABLE")
                if not generation:
                    raise ConnectionError("CLIENT_OFFLINE")
                self.pending[request_id] = (generation, future)
                try:
                    await self._publish(
                        generation.split(":")[0],
                        {
                            "kind": "request",
                            "id": request_id,
                            "source": self.instance,
                            "generation": generation,
                            "owner": str(owner),
                            "data": data,
                            "deadline": time.time() + timeout,
                            "trace": get_request_id(),
                            "correlation": correlation_ctx.get(),
                        },
                    )
                    return await future
                finally:
                    self.pending.pop(request_id, None)
        except ConnectionError:
            raise
        except Exception:
            raise TimeoutError("ROUTING_UNCONFIRMED") from None
        finally:
            self.pending.pop(request_id, None)
            if not future.done():
                future.cancel()
            elif not future.cancelled():
                future.exception()

    async def _publish(self, instance, message):
        payload = json.dumps(message, allow_nan=False, separators=(",", ":"))
        if len(payload.encode()) > MAX_MESSAGE_BYTES:
            raise ValueError("ROUTING_MESSAGE_TOO_LARGE")
        if not await self.redis.publish(PREFIX + "worker:" + instance, payload):
            raise TimeoutError("ROUTING_UNCONFIRMED")

    async def _listen(self):
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
                if not message:
                    continue
                raw = message["data"]
                if not isinstance(raw, str) or len(raw.encode()) > MAX_MESSAGE_BYTES:
                    continue
                data = json.loads(raw)
                if data.get("kind") == "reply":
                    waiting = self.pending.get(data.get("id"))
                    if waiting and waiting[0] == data.get("generation") and not waiting[1].done():
                        if data.get("ok") is True:
                            waiting[1].set_result(data.get("data"))
                        else:
                            waiting[1].set_exception(TimeoutError("ROUTING_UNCONFIRMED"))
                elif data.get("kind") == "request" and len(self.tasks) < MAX_PENDING:
                    task = asyncio.create_task(self._handle(data))
                    self.tasks.add(task)
                    task.add_done_callback(self.tasks.discard)
            except (ValueError, TypeError, KeyError, AttributeError):
                continue
            except Exception:
                self.ready = False
                self.subscribed = False
                # Never replay pending messages after a broker outage. Client
                # connections with expired ownership must reconnect and register.
                for _, future in self.pending.values():
                    if not future.done():
                        future.set_exception(TimeoutError("ROUTING_UNCONFIRMED"))
                await asyncio.sleep(5)
                with contextlib.suppress(Exception):
                    await self.pubsub.aclose()
                    await self._subscribe()

    async def _handle(self, message):
        trace = request_id_ctx_var.set(safe_id(message.get("trace")))
        supplied = message.get("correlation")
        supplied = supplied if isinstance(supplied, dict) else {}
        context = correlation_ctx.set(
            {key: safe_id(supplied.get(key)) for key in ("n8n_execution_id", "n8n_item_index")}
        )
        try:
            owner = message["owner"]
            generation = message["generation"]
            remaining = min(float(message["deadline"]) - time.time(), 120)
            local = self.local.get(owner)
            if (
                not self.ready
                or remaining <= 0
                or not local
                or local[0] != generation
                or await self.redis.get(route_key(owner)) != generation
            ):
                return
            reply = {"kind": "reply", "id": message["id"], "generation": generation, "ok": False}
            try:
                reply["data"] = await self.manager.local_execution_request(
                    owner, message["data"], remaining, expected=local[1]
                )
                reply["ok"] = True
            except Exception:
                pass
            await self._publish(message["source"], reply)
        except Exception:
            # Unconfirmed caller recovers via durable query, never a start replay.
            pass
        finally:
            correlation_ctx.reset(context)
            request_id_ctx_var.reset(trace)

    async def _renew(self):
        while True:
            await asyncio.sleep(5)
            try:
                await self.redis.ping()
                self.ready = self.subscribed
            except Exception:
                self.ready = False
                continue
            for owner, (generation, conn) in list(self.local.items()):
                try:
                    renewed = await self.redis.eval(_RENEW, 1, route_key(owner), generation, LEASE_SECONDS)
                    if not renewed:
                        # A newer connection or expired lease fences this peer.
                        if self.local.get(owner) == (generation, conn):
                            self.local.pop(owner, None)
                        await conn.ws.close()
                except Exception:
                    self.ready = False
