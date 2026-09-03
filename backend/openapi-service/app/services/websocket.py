from typing import Any

from fastapi import WebSocket
from rpawebsocket.ws import IWebSocket
from rpawebsocket.ws_service import WsManager

from app.logger import get_logger

logger = get_logger(__name__)


class WsService(IWebSocket):
    """这个是为了兼容 websocket和fastapi的差异的封装类"""

    def __init__(self, ws: WebSocket):
        self.ws = ws

    async def receive_text(self) -> str:
        return await self.ws.receive_text()

    async def send(self, message: Any) -> None:
        return await self.ws.send({"type": "websocket.send", "text": message})

    async def close(self) -> None:
        return await self.ws.close()


def ws_log(msg):
    message = str(msg)
    if message.startswith(">>>"):
        logger.debug("WebSocket message sent")
    elif message.startswith("<<<"):
        logger.debug("WebSocket message received")
    elif message.startswith("_add_conn "):
        logger.info("WebSocket connection added")
    elif message.startswith("_del_conn "):
        logger.info("WebSocket connection removed")
    elif message.startswith(("error", "listen error", "uuid empty")):
        logger.warning("WebSocket manager reported an error")
    else:
        logger.debug("WebSocket manager event")


class WsManagerService:
    def __init__(self):
        self.ws_manager = WsManager(log=ws_log)
