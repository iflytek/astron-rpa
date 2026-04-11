import json
from typing import Union

from astronverse.baseline.i18n.i18n import i18n
from astronverse.picker import Rect
from astronverse.picker.logger import logger


class HlHandler:
    """
    高亮通道消息处理器
    通过 WebSocket 向高亮进程（hl 连接）发送控制指令
    """

    def __init__(self, connections: dict):
        self._connections = connections

    async def _broadcast(self, message: dict) -> None:
        """向所有已连接的 hl 客户端广播消息，单个连接失败不影响其他连接"""
        conns = list(self._connections.get("hl", []))
        if not conns:
            return
        payload = json.dumps(message)
        for ws in conns:
            try:
                await ws.send(payload)
            except Exception as e:
                logger.warning(f"发送高亮消息失败: {e}")

    async def start(self, draw_type: str = "normal") -> None:
        """
        启动高亮窗口
        """
        await self._broadcast({"Operation": "start", "Type": draw_type, "Language": i18n.language})

    async def hide(self) -> None:
        """
        隐藏高亮窗口
        """
        await self._broadcast({"Operation": "hide"})

    async def draw(
        self,
        rects: Union[Rect, list[Rect]],
        msgs: Union[str, list[str]] = "",
        draw_type: str = "picking",
    ) -> None:
        """
        绘制高亮框
        """
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


