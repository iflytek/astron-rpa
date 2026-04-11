import asyncio
import json
from typing import Union

from astronverse.baseline.i18n.i18n import i18n
from astronverse.picker import Rect
from astronverse.picker.logger import logger


def _run_sync(coro) -> None:
    """将协程调度到 WsServer 事件循环并阻塞等待完成"""
    from astronverse.picker.server.ws_server import WsServer
    asyncio.run_coroutine_threadsafe(coro, WsServer.loop).result()


class HlHandler:
    """
    高亮通道消息处理器
    通过 WebSocket 向高亮进程（hl 连接）发送控制指令

    async 方法供 WebSocket handler（异步上下文）直接 await 调用；
    _sync 方法供同步线程（picker_server 等）调用，内部桥接到 WsServer 事件循环。
    """

    def __init__(self, connections: dict):
        self._connections = connections

    async def _broadcast(self, message: dict) -> None:
        """向所有已连接的 hl 客户端广播消息，单个连接失败不影响其他连接"""
        try:
            conns = list(self._connections.get("hl", []))
            if not conns:
                return
            payload = json.dumps(message)
            for ws in conns:
                try:
                    await ws.send(payload)
                except Exception as e:
                    logger.warning(f"发送高亮消息失败: {e}")
        except Exception as e:
            logger.error("广播高亮消息失败: %s", e)

    async def start(self, draw_type: str = "normal") -> None:
        await self._broadcast({"Operation": "start", "Type": draw_type, "Language": i18n.language})

    async def hide(self) -> None:
        await self._broadcast({"Operation": "hide"})

    async def draw(
        self,
        rects: Union[Rect, list[Rect]],
        msgs: Union[str, list[str]] = "",
        draw_type: str = "picking",
    ) -> None:
        msg = {"Operation": "draw", "Type": draw_type, "Boxes": []}
        if isinstance(rects, list):
            if msgs == "":
                msgs = [""] * len(rects)
            if len(msgs) < len(rects):
                msgs = msgs + [""] * (len(rects) - len(msgs))
            for i, rect in enumerate(rects):
                msg["Boxes"].append({
                    "Left": rect.left, "Top": rect.top,
                    "Right": rect.right, "Bottom": rect.bottom,
                    "Msg": msgs[i],
                })
        else:
            msg["Boxes"].append({
                "Left": rects.left, "Top": rects.top,
                "Right": rects.right, "Bottom": rects.bottom,
                "Msg": msgs,
            })
        await self._broadcast(msg)

    def start_sync(self, draw_type: str = "normal") -> None:
        _run_sync(self.start(draw_type))

    def hide_sync(self) -> None:
        _run_sync(self.hide())

    def draw_sync(
        self,
        rects: Union[Rect, list[Rect]],
        msgs: Union[str, list[str]] = "",
        draw_type: str = "picking",
    ) -> None:
        _run_sync(self.draw(rects, msgs, draw_type))


