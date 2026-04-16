import asyncio
import json
import time
from enum import Enum
from typing import Optional

import pyautogui

from astronverse.picker import RecordAction, RECORDING_BLACKLIST, PickerType, Rect
from astronverse.picker.logger import logger
from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey, PushKey, RequestPush


class RecordState(Enum):
    """录制状态枚举"""

    IDLE = "idle"
    LISTENING = "listening"
    RECORDING = "recording"
    HOVERING = "hovering"
    PAUSED = "paused"


class RecordEventMonitor:
    """录制事件监控器：检测 F4/ESC 按键和鼠标悬停，触发 RecordHandler 上的回调。
    只负责事件感知，不做任何业务状态判断。
    """

    POLL_INTERVAL = 0.05  # 主循环轮询间隔（秒）
    HOVER_THRESHOLD = 0.2  # 悬停触发阈值（秒）
    STARTUP_DELAY = 1.0  # 首次启动延迟，等待前端就绪

    def __init__(self, record_handler):
        self._handler = record_handler
        self._task: Optional[asyncio.Task] = None

        self._hover_start_time: Optional[float] = None
        self._hover_triggered: bool = False
        self._last_hover_rect = None

    def start(self):
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run())
        logger.info("[EventMonitor] 启动")

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        logger.info("[EventMonitor] 停止")

    async def _run(self):
        try:
            await asyncio.sleep(self.STARTUP_DELAY)
            h = self._handler
            while True:
                event_core = h.svc.event_core

                if event_core.is_f4_pressed():
                    event_core.reset_f4_flag()
                    logger.info("[EventMonitor] F4")
                    await h.on_f4_pressed()

                if event_core.is_cancel():
                    if hasattr(event_core, "reset_cancel_flag"):
                        event_core.reset_cancel_flag()
                    logger.info("[EventMonitor] ESC")
                    await h.on_esc_pressed()

                await self._check_hover()
                await asyncio.sleep(self.POLL_INTERVAL)

        except asyncio.CancelledError:
            logger.info("[EventMonitor] 被取消")
        except Exception as e:
            import traceback
            logger.error(f"[EventMonitor] 异常: {e}\n{traceback.format_exc()}")
        finally:
            logger.info("[EventMonitor] 结束")

    async def _check_hover(self):
        try:
            cur_x, cur_y = pyautogui.position()
            rs = self._handler.svc.pick_server._record # noqa
            cur_rect = rs.last_valid_rect if rs else None

            if self._is_rect_changed(cur_rect, self._last_hover_rect):
                self._last_hover_rect = cur_rect
                self._hover_start_time = None
                self._hover_triggered = False

            if cur_rect is None:
                return

            in_rect = cur_rect.left <= cur_x <= cur_rect.right and cur_rect.top <= cur_y <= cur_rect.bottom

            if not in_rect:
                if self._hover_triggered:
                    await self._handler.on_mouse_out()
                self._hover_start_time = None
                self._hover_triggered = False
                return

            if self._hover_start_time is None:
                self._hover_start_time = time.time()
            if not self._hover_triggered and time.time() - self._hover_start_time >= self.HOVER_THRESHOLD:
                self._hover_triggered = True
                await self._handler.on_mouse_hover(self._build_rect_data(cur_rect, rs.last_valid_domain, cur_x, cur_y))

        except Exception as e:
            import traceback
            logger.error(f"[EventMonitor] 悬停检测异常: {e}\n{traceback.format_exc()}")

    @staticmethod
    def _is_rect_changed(a, b) -> bool:
        if (a is None) != (b is None):
            return True
        if a is None:
            return False
        return a != b

    @staticmethod
    def _build_rect_data(rect, domain: Optional[str], cur_x: int, cur_y: int) -> str:
        data = {
            "left": rect.left,
            "top": rect.top,
            "right": rect.right,
            "bottom": rect.bottom,
            "mouse_x": cur_x,
            "mouse_y": cur_y,
            "domain": domain,
        }
        return json.dumps(data, ensure_ascii=False)


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

        self._state = RecordState.IDLE
        self.record_task: asyncio.Task = None
        self._continue_event: asyncio.Event = None
        self._cached_element = None

        self.event_monitor: RecordEventMonitor = None

    # ------------------------------------------------------------------
    # 分发
    # ------------------------------------------------------------------

    async def dispatch(self, ws_server, data: dict):
        self.ws_server = ws_server
        request = RequestMessage(**data)

        try:
            match request.record_action:
                case RecordAction.LISTENING:
                    await self._handle_listening(request)
                case RecordAction.END:
                    await self._handle_end(request)
                case RecordAction.START:
                    await self._handle_start(request)
                case RecordAction.PAUSE:
                    await self._handle_pause(request)
                case RecordAction.HOVER_START:
                    await self._handle_hover_start(request)
                case RecordAction.HOVER_END:
                    await self._handle_hover_end(request)
                case RecordAction.AUTOMIC_END:
                    await self._handle_automic_end(request)
        except Exception as e:
            logger.error(f"录制动作处理失败: {e}")
            await self._send_response(ResponseKey.ERROR, error=str(e))

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    async def _handle_listening(self, request: RequestMessage):
        if self._state == RecordState.IDLE:
            if self.svc.event_core:
                self.svc.event_core.start()

            self.event_monitor = RecordEventMonitor(self)
            self.event_monitor.start()
            self._state = RecordState.LISTENING
            await self._send_response(ResponseKey.SUCCESS, data="监听已启动")
        elif self._state == RecordState.LISTENING:
            await self._send_response(ResponseKey.SUCCESS, data="监听已启动")
        else:
            await self._send_response(ResponseKey.ERROR, error="当前状态不允许监听")

    async def _handle_end(self, request: RequestMessage):
        if self._state == RecordState.IDLE:
            await self._send_response(ResponseKey.SUCCESS, data="录制已结束")
        else:
            if self.event_monitor:
                self.event_monitor.stop()
                self.event_monitor = None

            if self.svc.event_core:
                self.svc.event_core.close()

            await self._stop_recording()

            self._state = RecordState.IDLE
            await self._send_response(ResponseKey.SUCCESS, data="录制已结束")

    # ------------------------------------------------------------------
    # 录制控制
    # ------------------------------------------------------------------

    async def _handle_start(self, request: RequestMessage):
        if await self._start_recording(request):
            await self._send_response(ResponseKey.SUCCESS, data="录制已开始")

    async def _handle_pause(self, request: RequestMessage):
        if await self._stop_recording():
            await self._send_response(ResponseKey.SUCCESS, data="已暂停")

    async def _start_recording(self, request: RequestMessage = None) -> bool:
        if self._state == RecordState.LISTENING:
            await self.ws_server.hl.start("normal")

            self._cached_element = None
            self._continue_event = None
            self.record_task = asyncio.create_task(self._record_loop(request))
            self._state = RecordState.RECORDING
            return True
        elif self._state == RecordState.RECORDING:
            return True
        else:
            return False

    async def _stop_recording(self) -> bool:
        if self._state == RecordState.IDLE:
            return False
        elif self._state == RecordState.LISTENING:
            return True
        else:
            await self.ws_server.hl.hide()

            if self.record_task and not self.record_task.done():
                self.record_task.cancel()
                try:
                    await self.record_task
                except asyncio.CancelledError:
                    pass
                self.record_task = None

            await self.svc.send_sign(RecordAction.END.value, {})
            self._state = RecordState.LISTENING
            return True

    # ------------------------------------------------------------------
    # 悬停交互
    # ------------------------------------------------------------------

    async def _handle_hover_start(self, request: RequestMessage):
        if self._state == RecordState.HOVERING:
            self._state = RecordState.PAUSED
            await self._send_response(ResponseKey.SUCCESS, data="悬停检测已启动")

    async def _handle_hover_end(self, request: RequestMessage):
        if self._state == RecordState.PAUSED:
            self._state = RecordState.HOVERING
            await self._send_response(ResponseKey.SUCCESS, data="已恢复拾取")

    async def _handle_automic_end(self, request: RequestMessage):
        if self._state == RecordState.PAUSED:
            self._state = RecordState.RECORDING
            if isinstance(self._cached_element, dict):
                await self._send_response(ResponseKey.SUCCESS, data=self._cached_element)
            else:
                await self._send_response(ResponseKey.ERROR, error="未找到元素")

    # ------------------------------------------------------------------
    # 推送回调（由 RecordEventMonitor 调用）
    # ------------------------------------------------------------------

    async def on_f4_pressed(self):
        started = await self._start_recording(RequestMessage(
            pick_type=PickerType.RECORD,
            record_action=RecordAction.START
        ))
        if started:
            await self._push(PushKey.RECORD_START)

    async def on_esc_pressed(self):
        stopped = await self._stop_recording()
        if stopped:
            await self._push(PushKey.RECORD_PAUSE)

    async def on_mouse_hover(self, rect_data: str):
        if self._state == RecordState.RECORDING:
            self._state = RecordState.HOVERING
            await self._push(PushKey.RECORD_AUTOMIC_CHOICE, data=rect_data)
            self._cached_element = await self.svc.send_sign(RecordAction.END.value, {})

    async def on_mouse_out(self):
        if self._state == RecordState.HOVERING:
            self._state = RecordState.RECORDING
            await self._push(PushKey.RECORD_AUTOMIC_DRAW_END)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    async def _record_loop(self, request: RequestMessage):
        payload = request.model_dump() if request else {}
        try:
            while True:
                if self._state in [RecordState.RECORDING, RecordState.HOVERING]:
                    result = await self.svc.send_sign(RecordAction.START.value, payload)
                    if result:
                        logger.warning(f"拾取错误: {result}")
        except asyncio.CancelledError:
            logger.info("录制循环已取消")

    async def _push(self, key: PushKey, data: str = ""):
        if not self.ws_server:
            return
        conns = self.ws_server.connections.get("record", [])
        if not conns:
            return
        logger.info(f"[RecordHandler] 推送: {key.value}")
        await conns[-1].send(RequestPush.create_push(key, data=data).model_dump_json())

    async def _send_response(self, key: ResponseKey, data=None, error: str = ""):
        logger.info(f"[RecordHandler] 返回值: {key.value}")
        if data is None:
            data = ""
        if key == ResponseKey.SUCCESS:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            elif not isinstance(data, str):
                data = str(data)
        if not self.ws_server:
            return
        conns = self.ws_server.connections.get("record", [])
        if not conns:
            return
        await conns[-1].send(ResponseMessage.create_response(key, data=data, err_msg=error).model_dump_json())
