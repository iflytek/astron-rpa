import asyncio
import json

from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey, RequestPush, PushKey
from astronverse.picker import RecordAction
from astronverse.picker.logger import logger


class RecordHandler:
    """录制处理器 - 管理录制状态流转，通过 svc.send_sign 与 RecordServer 通信

    状态分组：
    - 生命周期对：LISTENING ↔ END（初始化/销毁会话）
    - 录制控制对：START ↔ PAUSE（创建/销毁绘框循环，回到 LISTENING 状态）
    - 悬停交互组：HOVER_START → HOVER_END / AUTOMIC_END（前端浮层交互）
    """

    def __init__(self, svc):
        self.svc = svc
        self.ws_server = None

        # 状态管理
        self.record_task: asyncio.Task = None
        self._continue_event: asyncio.Event = None  # 控制循环暂停/恢复
        self._cached_element = None  # HOVER_START 时缓存的元素数据，供 AUTOMIC_END 使用

    async def dispatch(self, ws_server, data: dict):
        """分发录制动作"""
        self.ws_server = ws_server
        request = RequestMessage(**data)
        try:
            match request.record_action:
                # === 生命周期对 ===
                case RecordAction.LISTENING:
                    await self._handle_listening(request)
                case RecordAction.END:
                    await self._handle_end(request)

                # === 录制控制对 ===
                case RecordAction.START:
                    await self._handle_start(request)
                case RecordAction.PAUSE:
                    await self._handle_pause(request)

                # === 悬停交互组 ===
                case RecordAction.HOVER_START:
                    await self._handle_hover_start(request)
                case RecordAction.HOVER_END:
                    await self._handle_hover_end(request)
                case RecordAction.AUTOMIC_END:
                    await self._handle_automic_end(request)

        except Exception as e:
            logger.error(f"录制动作处理失败: {e}")
            await self._send_response(ResponseKey.ERROR, error=str(e))

    async def _handle_listening(self, request: RequestMessage):
        """初始化录制会话：注册推送回调、启动键鼠监听等"""
        # TODO: 初始化后端的键鼠监听、悬停检测
        await self._send_response(ResponseKey.SUCCESS, data="监听已启动")

    async def _handle_end(self, request: RequestMessage):
        """销毁录制会话：清理所有资源"""
        # TODO: 取消初始化后端的键鼠监听、悬停检测
        await self._send_response(ResponseKey.SUCCESS, data="录制已结束")

    async def _handle_start(self, request: RequestMessage):
        """创建绘框循环，确保干净状态"""
        if self.record_task and not self.record_task.done():
            await self._send_response(ResponseKey.SUCCESS, data="录制已在进行中")
            return

        await self.ws_server.hl.start("normal")
        self._cached_element = None
        self._continue_event = None
        self.record_task = asyncio.create_task(self._record_loop(request))
        await self._send_response(ResponseKey.SUCCESS, data="录制已开始")

    async def _handle_pause(self, request: RequestMessage):
        """销毁绘框循环，回到 LISTENING 的干净状态"""
        # 取消循环
        if self.record_task and not self.record_task.done():
            self.record_task.cancel()
            try:
                await self.record_task
            except asyncio.CancelledError:
                pass

        # 通知 RecordServer 清理状态（隐藏高亮、清空缓存）
        await self.svc.send_sign(RecordAction.END.value, {})

        # 清空循环引用
        self.record_task = None

        await self._send_response(ResponseKey.SUCCESS, data="已暂停")

    async def _handle_hover_start(self, request: RequestMessage):
        """前端 UI 浮层出现：停止绘框，缓存元素数据"""
        # 暂停循环
        if self._continue_event:
            self._continue_event.clear()

        # 发送 END 停止绘框，同时获取元素数据
        result = await self.svc.send_sign(RecordAction.END.value, {})
        self._cached_element = result

        await self._send_response(ResponseKey.SUCCESS, data="悬停检测已启动")

    async def _handle_hover_end(self, request: RequestMessage):
        """用户放弃选择：恢复绘框"""
        self._cached_element = None
        if self._continue_event:
            self._continue_event.set()
        await self._send_response(ResponseKey.SUCCESS, data="已恢复拾取")

    async def _handle_automic_end(self, request: RequestMessage):
        """用户确认原子操作：返回缓存的元素数据，恢复绘框"""
        if isinstance(self._cached_element, dict):
            await self._send_response(ResponseKey.SUCCESS, data=self._cached_element)
        else:
            await self._send_response(ResponseKey.ERROR, error="未找到元素")

        self._cached_element = None
        if self._continue_event:
            self._continue_event.set()

    async def _record_loop(self, request: RequestMessage):
        """录制主循环：持续通过 send_sign 触发绘框"""
        self._continue_event = asyncio.Event()
        self._continue_event.set()  # 初始状态为运行

        try:
            while True:
                # 检查是否需要暂停（悬停时）
                if not self._continue_event.is_set():
                    await self._continue_event.wait()

                # 通过 send_sign 触发一次拾取绘框
                payload = request.model_dump()
                result = await self.svc.send_sign(RecordAction.START.value, payload)

                # 只有出错才会返回，记录日志但继续循环
                if isinstance(result, str) and result != "":
                    logger.warning(f"拾取失败: {result}")

                # 短暂让出，避免空转
                await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            logger.info("录制循环已取消")

    async def _send_response(self, key: ResponseKey, data=None, error: str = ""):
        """发送响应给前端"""
        if data is None:
            data = ""
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        ws = self.ws_server.connections["record"][-1]
        await ws.send(ResponseMessage.create_response(key, data=data, err_msg=error).model_dump_json())
