"""Compatibility fix for buffered messages in the bundled rpawebsocket 1.0.7.

The dependency's listener closes over the mutable receive-loop variable. Keep
its routing/watch/connection contract, but bind each message to its own task.
This override can be removed when that dependency ships the fix.
"""

import asyncio
import json
import time

from rpawebsocket.ws import AckMsg, BaseMsg, Conn, ExitMsg, MsgUnlawfulnessError, PingMsg, PongMsg
from rpawebsocket.ws_service import WsManager


class MessageBoundWsManager(WsManager):
    async def execution_request(self, user_id: str, data: dict, timeout: float = 5):
        """Send once to one connection, accepting a reply only from that peer."""
        connections = self.conns.get(str(user_id), [])
        if not connections:
            raise ConnectionError("CLIENT_OFFLINE")
        conn = connections[-1]
        msg = BaseMsg(
            channel="execution",
            key="control",
            uuid="$root$",
            send_uuid=str(user_id),
            need_reply=True,
            data={"protocol": 1, **data, "owner": str(user_id)},
        ).init()
        if not hasattr(self, "execution_waiters"):
            self.execution_waiters = {}
        future = asyncio.get_running_loop().create_future()
        self.execution_waiters[msg.event_id] = (conn, future)
        try:
            # No payload logs, broadcasts, watch retries or cross-connection replies.
            await conn.send_text(msg.tojson())
            return await asyncio.wait_for(future, timeout)
        finally:
            self.execution_waiters.pop(msg.event_id, None)

    async def _handle_message(self, msg: BaseMsg, conn: Conn, svc):
        if msg.channel == "execution" and msg.reply_event_id:
            waiter = getattr(self, "execution_waiters", {}).get(msg.reply_event_id)
            if waiter is not None:
                expected, future = waiter
                current = self.conns.get(conn.uuid, [])
                if expected is conn and current and current[-1] is conn and not future.done():
                    future.set_result(msg.data)
            return
        if msg.channel == PingMsg.channel:
            conn.last_ping = int(time.time())
            await self._send_text(conn, PongMsg.tojson())
            return
        if msg.channel == ExitMsg.channel:
            self.log("error ExitMsg")
            return
        watch_name = None
        if msg.channel == AckMsg.channel:
            watch_name = f"ack$${msg.event_id}"
        elif msg.reply_event_id:
            watch_name = f"reply$${msg.reply_event_id}"
        if watch_name is not None:
            # Remove before awaiting so duplicate frames cannot invoke the
            # same callback while its first invocation is suspended.
            watch = self.watch_msg.pop(watch_name, None)
            if watch is not None:
                await self._call_wait(watch, msg, None)
            return

        reply = msg.to_reply()
        try:
            result = await self._call_route(msg.channel, msg.key, msg, svc)
            try:
                result = json.loads(result.body.decode("utf-8"))
            except (AttributeError, ValueError, UnicodeError):
                pass
            reply.data = result
        except Exception as exc:
            reply.data = self.error_format(exc)
        if reply.data is not None:
            await self.send(reply)

    async def listen(self, uuid: str, conn: Conn, svc=None):
        tasks = set()

        async def handle(msg):
            try:
                await self._handle_message(msg, conn, svc)
            except Exception:
                self.log("error handling WebSocket message")

        self._add_conn(uuid, conn)
        try:
            while True:
                text = await conn.ws.receive_text()
                try:
                    msg = BaseMsg(**json.loads(text))
                    if not msg.channel:
                        raise ValueError("Missing channel")
                    msg.uuid = msg.uuid or conn.uuid
                    msg.send_uuid = msg.send_uuid or "$root$"
                except (TypeError, ValueError):
                    await self._send_exit(conn, MsgUnlawfulnessError("Invalid WebSocket message"))
                    continue
                task = asyncio.create_task(handle(msg))
                tasks.add(task)
                task.add_done_callback(tasks.discard)
        except Exception as exc:
            self.log("listen error")
            await self._send_exit(conn, exc)
        finally:
            if self._del_conn(conn.uuid, conn):
                try:
                    await conn.ws.close()
                except Exception:
                    pass
            # Finish already received replies even if the peer disconnects.
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
