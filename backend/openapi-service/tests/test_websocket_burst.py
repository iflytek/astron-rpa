import asyncio
import json
from contextlib import suppress

import pytest
from rpawebsocket.ws import BaseMsg, Conn

from app.services.websocket import WsManagerService


class BufferedSocket:
    def __init__(self):
        self.messages = asyncio.Queue()
        self.sent = []
        self.closed = False

    async def receive_text(self):
        return await self.messages.get()

    async def send(self, message):
        self.sent.append(message)

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_execution_control_pins_one_connection_and_ignores_foreign_stale_replies():
    manager = WsManagerService().ws_manager
    old, current, foreign = [Conn(ws=BufferedSocket()) for _ in range(3)]
    manager._add_conn("owner", old)
    manager._add_conn("owner", current)
    manager._add_conn("other", foreign)
    task = asyncio.create_task(manager.execution_request("owner", {"action": "get"}, timeout=0.5))
    await asyncio.sleep(0)
    assert len(current.ws.sent) == 1
    assert old.ws.sent == []
    assert foreign.ws.sent == []
    request = BaseMsg(**json.loads(current.ws.sent[0]))
    reply = request.to_reply()
    reply.data = {"status": "succeeded"}
    await manager._handle_message(reply, old, None)
    await manager._handle_message(reply, foreign, None)
    assert not task.done()
    await manager._handle_message(reply, current, None)
    assert await task == reply.data
    assert not manager.execution_waiters
    with pytest.raises(TimeoutError):
        await manager.execution_request("owner", {"action": "get"}, timeout=0.01)
    assert len(current.ws.sent) == 2  # Exactly one send per request, including timeout.
    assert not manager.execution_waiters


@pytest.mark.asyncio
async def test_buffered_execution_replies_keep_their_own_callback():
    manager = WsManagerService().ws_manager
    socket = BufferedSocket()
    listener = asyncio.create_task(manager.listen("owner", Conn(ws=socket)))
    observed = []
    try:
        await asyncio.sleep(0)
        requests = []
        for i in range(3):
            request = BaseMsg(channel="remote", key="run", uuid="$root$", send_uuid="owner").init()

            async def callback(reply, error, expected=i):
                assert error is None
                observed.append((expected, reply.data["value"]))

            await manager.send_reply(request, 30, callback)
            requests.append(request)

        # All frames are buffered before the listener runs again. This models
        # busy and successful results arriving in the same network read.
        for i, request in enumerate(requests):
            reply = request.to_reply()
            reply.data = {"value": i}
            socket.messages.put_nowait(reply.tojson())
        async with asyncio.timeout(1):
            while len(observed) < 3:
                await asyncio.sleep(0.01)
        assert observed == [(0, 0), (1, 1), (2, 2)]
        assert not manager.watch_msg
    finally:
        listener.cancel()
        with suppress(asyncio.CancelledError):
            await listener
    assert socket.closed
    assert "owner" not in manager.conns


@pytest.mark.asyncio
async def test_buffered_ping_and_duplicate_reply_do_not_drop_or_repeat_result():
    manager = WsManagerService().ws_manager
    socket = BufferedSocket()
    listener = asyncio.create_task(manager.listen("owner", Conn(ws=socket)))
    observed = []
    try:
        await asyncio.sleep(0)
        request = BaseMsg(channel="remote", key="run", uuid="$root$", send_uuid="owner").init()

        async def callback(reply, error):
            await asyncio.sleep(0.01)
            observed.append(reply.data)

        await manager.send_reply(request, 30, callback)
        reply = request.to_reply()
        reply.data = {"code": "5001", "msg": "busy"}
        for message in [reply.tojson(), '{"channel":"ping"}', reply.tojson()]:
            socket.messages.put_nowait(message)
        await asyncio.sleep(0.05)
        assert observed == [reply.data]
        assert any('"pong"' in message for message in socket.sent)
    finally:
        listener.cancel()
        with suppress(asyncio.CancelledError):
            await listener
