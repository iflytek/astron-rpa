import asyncio
import json
import time
from enum import Enum
from typing import Optional

import pyautogui

from astronverse.picker import RecordAction, RECORDING_BLACKLIST, PickerType
from astronverse.picker.logger import logger
from astronverse.picker.server import RequestMessage, ResponseMessage, ResponseKey, PushKey, RequestPush


class RecordState(Enum):
    IDLE = "idle"                  # 未录制
    RECORDING = "recording"        # 录制中（绘框循环运行）
    HOVER_PENDING = "hover_pending"  # monitor 已推送悬停，等待前端 HOVER_START 确认
    HOVER = "hover"                # 前端已确认 HOVER_START，完全静默


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
            while h.ws_server:
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
            current_time = time.time()
            h = self._handler

            rs = h.record_server
            cur_rect = rs.last_valid_rect if rs else None

            if self._is_rect_changed(cur_rect, self._last_hover_rect):
                self._last_hover_rect = cur_rect
                self._hover_start_time = None
                self._hover_triggered = False

            if cur_rect is None:
                return

            in_rect = (
                    cur_rect.left <= cur_x <= cur_rect.right
                    and cur_rect.top <= cur_y <= cur_rect.bottom
            )

            if in_rect:
                if self._hover_start_time is None:
                    self._hover_start_time = current_time
                    self._hover_triggered = False
                elif not self._hover_triggered:
                    if current_time - self._hover_start_time >= self.HOVER_THRESHOLD:
                        self._hover_triggered = True
                        rect_data = self._build_rect_data(rs, cur_x, cur_y)
                        await h.on_mouse_hover(rect_data)
            else:
                if self._hover_triggered:
                    await h.on_mouse_out()
                self._hover_start_time = None
                self._hover_triggered = False
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
    def _build_rect_data(rs, cur_x: int, cur_y: int) -> str:
        try:
            if rs and rs.last_valid_rect:
                rect = rs.last_valid_rect
                return json.dumps({
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "mouse_x": cur_x,
                    "mouse_y": cur_y,
                    "domain": rs.last_valid_domain,
                }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[EventMonitor] 构造 rect_data 失败: {e}")
        return "{}"


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

    @property
    def record_server(self):
        try:
            return self.svc.pick_server._record  # noqa 不太规范但是这样做有效
        except AttributeError:
            return None

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
        if self.svc.event_core:
            self.svc.event_core.start()

        self.event_monitor = RecordEventMonitor(self)
        self.event_monitor.start()

        await self._send_response(ResponseKey.SUCCESS, data="监听已启动")

    async def _handle_end(self, request: RequestMessage):
        if self.event_monitor:
            self.event_monitor.stop()
            self.event_monitor = None

        await self._stop_recording()
        await self.ws_server.hl.hide()
        self._state = RecordState.IDLE

        if self.svc.event_core:
            self.svc.event_core.close()

        await self._send_response(ResponseKey.SUCCESS, data="录制已结束")

    # ------------------------------------------------------------------
    # 录制控制
    # ------------------------------------------------------------------

    async def _handle_start(self, request: RequestMessage):
        if self._state == RecordState.RECORDING:
            await self._send_response(ResponseKey.SUCCESS, data="录制已在进行中")
            return
        await self._start_recording(request)
        await self._send_response(ResponseKey.SUCCESS, data="录制已开始")

    async def _handle_pause(self, request: RequestMessage):
        await self._stop_recording()
        await self.ws_server.hl.hide()
        await self._send_response(ResponseKey.SUCCESS, data="已暂停")

    async def _start_recording(self, request: RequestMessage = None) -> bool:
        if self._state == RecordState.RECORDING:
            return False
        await self.ws_server.hl.start("normal")
        self._cached_element = None
        self._continue_event = None
        self.record_task = asyncio.create_task(self._record_loop(request))
        self._state = RecordState.RECORDING
        return True

    async def _stop_recording(self) -> bool:
        if self._state == RecordState.IDLE:
            return False
        if self.record_task and not self.record_task.done():
            self.record_task.cancel()
            try:
                await self.record_task
            except asyncio.CancelledError:
                pass
        self.record_task = None
        self._state = RecordState.IDLE
        await self.svc.send_sign(RecordAction.END.value, {})
        return True

    # ------------------------------------------------------------------
    # 悬停交互
    # ------------------------------------------------------------------

    async def _handle_hover_start(self, request: RequestMessage):
        # 前端确认悬停，_continue_event 已在 on_mouse_hover 中 clear，无需重复操作
        result = await self.svc.send_sign(RecordAction.END.value, {})
        self._cached_element = result
        self._state = RecordState.HOVER  # 前端已确认，完全静默
        await self._send_response(ResponseKey.SUCCESS, data="悬停检测已启动")

    async def _handle_hover_end(self, request: RequestMessage):
        self._cached_element = None
        if self._continue_event:
            self._continue_event.set()
        self._state = RecordState.RECORDING
        await self._send_response(ResponseKey.SUCCESS, data="已恢复拾取")

    async def _handle_automic_end(self, request: RequestMessage):
        if isinstance(self._cached_element, dict):
            await self._send_response(ResponseKey.SUCCESS, data=self._cached_element)
        else:
            await self._send_response(ResponseKey.ERROR, error="未找到元素")

        self._cached_element = None
        if self._continue_event:
            self._continue_event.set()
        self._state = RecordState.RECORDING

    # ------------------------------------------------------------------
    # 推送回调（由 RecordEventMonitor 调用）
    # ------------------------------------------------------------------

    async def on_f4_pressed(self):
        if self._state != RecordState.IDLE:
            return
        started = await self._start_recording(RequestMessage(
            pick_type=PickerType.RECORD,
            record_action=RecordAction.START,
            data="",
        ))
        if started:
            await self._push(PushKey.RECORD_START)

    async def on_esc_pressed(self):
        if self._state == RecordState.IDLE:
            return
        stopped = await self._stop_recording()
        if stopped:
            await self.ws_server.hl.hide()
            await self._push(PushKey.RECORD_PAUSE)

    async def on_mouse_hover(self, rect_data: str):
        if self._state != RecordState.RECORDING:
            return
        if self._continue_event:
            self._continue_event.clear()  # 悬停触发后立即暂停绘框
        self._state = RecordState.HOVER_PENDING  # 等待前端 HOVER_START 确认
        await self._push(PushKey.RECORD_AUTOMIC_CHOICE, data=rect_data)

    async def on_mouse_out(self):
        if self._state != RecordState.HOVER_PENDING:
            return  # HOVER（前端已确认）状态下完全静默
        if self._continue_event:
            self._continue_event.set()  # 前端未确认前移出，恢复绘框
        self._state = RecordState.RECORDING
        await self._push(PushKey.RECORD_AUTOMIC_DRAW_END)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    async def _record_loop(self, request: RequestMessage):
        self._continue_event = asyncio.Event()
        self._continue_event.set()

        try:
            while True:
                await self._continue_event.wait()

                # event set 之后再检查状态，防止 hover 触发期间继续 draw
                if self._state != RecordState.RECORDING:
                    await asyncio.sleep(0.05)
                    continue

                payload = request.model_dump() if request else {}
                result = await self.svc.send_sign(RecordAction.START.value, payload)

                if isinstance(result, str) and result:
                    logger.warning(f"拾取失败: {result}")

                await asyncio.sleep(0.05)

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
