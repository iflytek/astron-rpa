import asyncio
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket
from rpawebsocket.ws import Conn, IWebSocket
from rpawebsocket.ws_service import WsManager

from ...core.svc import Svc, get_svc
from ...logger import logger

router = APIRouter()


def ws_log(msg):
    """日志打印"""
    logger.info(msg)


wsmg = WsManager(log=ws_log, ping_close_time=300)


class WsSocket(IWebSocket):
    """websocket连接类, 实现了IWebSocket接口, 抽象的目的主要是为了兼容fastapi接口和websocket的WebSocketServerProtocol接口"""

    def __init__(self, ws: WebSocket):
        self.ws = ws

    async def receive_text(self) -> str:
        res = await self.ws.receive()
        return str(res)

    async def send(self, message: Any) -> None:
        return await self.ws.send(message)

    async def close(self) -> None:
        return await self.ws.close()


@router.websocket("/ws")
async def websocket(ws: WebSocket, svc: Svc = Depends(get_svc)):
    try:
        uuid = "$executor$"
        await asyncio.gather(
            wsmg.listen(uuid, Conn(ws=WsSocket(ws)), svc),
            wsmg.start_ping(),
            wsmg.clear_watch(),
        )
    except Exception as e:
        logger.error("websocket error {}".format(e))


# 下面是事件注册
