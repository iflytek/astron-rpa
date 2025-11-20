import asyncio
import json
import queue
import traceback
from dataclasses import dataclass
from typing import Any
import websockets
from astronverse.websocket_server.ws import IWebSocket, BaseMsg, Conn
from astronverse.websocket_server.ws_service import WsManager, AsyncOnce
from websockets import ServerConnection

from astronverse.executor import ExecuteStatus
from astronverse.executor.error import *
from astronverse.executor.logger import logger


@dataclass
class CustomResponse:
    """自定义的返回值"""

    code: str
    msg: str
    data: Any


def ws_log(msg):
    """日志打印"""
    logger.info(msg)


def error_format(e=None) -> dict:
    """错误格式化"""

    def error_to_base_error() -> BaseException:
        if isinstance(e, BaseException):
            return e
        return BaseException(GENERAL_ERROR_FORMAT.format(e), "内部错误 error: {}".format(e))

    def gen_error_msg(exc: BaseException):
        return CustomResponse(exc.code.code.value, exc.code.message, {}).__dict__

    return gen_error_msg(error_to_base_error())


wsmg = WsManager(error_format=error_format, log=ws_log, ping_close_time=300)


class WsSocket(IWebSocket):
    """websocket连接类, 实现了IWebSocket接口"""

    def __init__(self, ws: ServerConnection):
        self.ws = ws

    async def receive_text(self) -> str:
        res = await self.ws.recv()
        return str(res)

    async def send(self, message: Any) -> None:
        return await self.ws.send(message)

    async def close(self) -> None:
        return await self.ws.close()


class Ws:
    def __init__(self, svc):
        self.svc = svc

        self.is_open_web_link = False
        self.is_web_link = False
        self.is_open_top_link = False
        self.is_tip_link = False

        self.BASE_MSG = BaseMsg(channel="flow", key="report", uuid="$root$")
        self.report_once = AsyncOnce()

    def check_ws_link(self):
        if self.is_open_web_link and not self.is_web_link:
            return False
        if self.is_open_top_link and not self.is_tip_link:
            return False
        return True

    @staticmethod
    async def send_text(conn: Conn, msg: str):
        await conn.send_text(msg)

    async def send_report(self, q: queue.Queue):
        async def inner_send_report():
            i = 1
            drop_max_size = int(q.maxsize / 10 * 8)
            drop_min_size = int(q.maxsize / 10 * 2)
            drop_num = 0

            while True:
                if not self.check_ws_link():
                    await asyncio.sleep(0.3)
                    continue
                try:
                    msg = q.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0.3)
                    continue

                try:
                    # 如果只是tip链接就有优化的空间
                    if not self.is_open_web_link:
                        # 消息太多直接抛弃, 快速抛弃
                        if q.qsize() > drop_max_size:
                            for i in range(drop_max_size - drop_min_size):
                                msg = q.get()
                                pass

                    # 都需要发送
                    data = json.loads(msg)
                    tag = data.get("tag", None)
                    if tag == "tip":
                        # 只需要发送给tip
                        is_send_web = False
                        is_send_tip = True
                    else:
                        # 都需要发送
                        is_send_web = True
                        is_send_tip = True

                    tasks_1 = []
                    tasks_2 = []
                    if is_send_web and wsmg.conns.get("$executor$"):
                        self.BASE_MSG.send_uuid = "$executor$"
                        self.BASE_MSG.init().data = data
                        tasks_1 = [
                            asyncio.create_task(self.send_text(v1, self.BASE_MSG.tojson()))
                            for v1 in wsmg.conns[self.BASE_MSG.send_uuid]
                        ]
                    if is_send_tip and wsmg.conns.get("$executor_tip$"):
                        # tip达到抛弃的下沿就直接抛弃，并计算抛弃数量30个就吐出1个
                        if q.qsize() > drop_min_size and drop_num < 30:
                            tasks_2 = []
                            drop_num += 1
                        else:
                            drop_num = 0
                            self.BASE_MSG.send_uuid = "$executor_tip$"
                            self.BASE_MSG.init().data = data
                            tasks_2 = [
                                asyncio.create_task(self.send_text(v2, self.BASE_MSG.tojson()))
                                for v2 in wsmg.conns[self.BASE_MSG.send_uuid]
                            ]
                    tasks = tasks_1 + tasks_2
                    if tasks:
                        i += 1
                        if i % 30 == 0:
                            i = 1
                            await asyncio.sleep(0.3)  # 每次发送30条消息就休眠0.3秒
                        await asyncio.gather(*tasks)
                except Exception as e:
                    pass

        await self.report_once.do(inner_send_report)

    async def websocket_endpoint(self, ws: ServerConnection):
        try:
            path = ws.request.path

            uuid = "$executor$"
            if path in ["", "/"]:
                self.is_web_link = True
                uuid = "$executor$"  # 特殊区分一下是web日志
            elif path == "/?tag=tip":
                uuid = "$executor_tip$"  # 特殊区分一下是右下角日志
                self.is_tip_link = True
            else:
                # 其他条件不管
                pass

            await asyncio.gather(
                wsmg.listen(uuid, Conn(ws=WsSocket(ws)), self.svc),
                wsmg.start_ping(),
                wsmg.clear_watch(),
                self.send_report(self.svc.report.queue),
            )
        except Exception as e:
            if isinstance(e, BaseException):
                error_str = e.code.message
            else:
                error_str = str(e)
            self.svc.end(ExecuteStatus.FAIL, reason=error_str)

    async def run_server(self):
        async with websockets.serve(self.websocket_endpoint, "127.0.0.1", self.svc.conf.port):
            logger.info("服务已启动 ws://127.0.0.1:{}".format(self.svc.conf.port))
            await asyncio.Future()

    def server(self):
        from astronverse.executor.debug.apis.apis import route_init

        route_init()
        asyncio.run(self.run_server())
