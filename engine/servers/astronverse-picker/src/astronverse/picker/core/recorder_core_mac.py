# macOS implementation - mirrors recorder_core_win.py
# Windows-specific changes:
#   UIAOperate  → AXUIOperate  (axui_picker)
#   win32api.GetCursorPos() → AXUIOperate.get_cursor_pos()
#   pythoncom.CoInitialize() → removed (not needed on macOS)
import asyncio
import json
import threading
import time
from collections.abc import Callable
from enum import Enum
from typing import Any, Optional

from astronverse.picker import (
    RECORDING_BLACKLIST,
    DrawResult,
    MKSign,
    OperationResult,
    PickerType,
    Point,
    RecordAction,
    Rect,
)
from astronverse.picker.core.picker_core_mac import PickerCore
from astronverse.picker.engines.axui_picker import AXUIOperate
from astronverse.picker.error import (
    BizException,
    PICKER_CONVERTER_ERROR,
    PICKER_CONVERTER_MISSING_ERROR,
    CUR_RECT_NOT_INITIALIZED_ERROR,
    MOUSE_POSITION_OUT_OF_RANGE_ERROR,
)
from astronverse.picker.logger import logger
from astronverse.picker.utils.process import find_real_application_process


class RecordingState(Enum):
    """录制状态枚举"""

    IDLE = "idle"
    LISTENING = "listening"
    RECORDING = "recording"
    PAUSED = "paused"


class RecordPickerAdapter:
    """录制功能的拾取适配器"""

    def __init__(self, picker_core: PickerCore):
        self.picker_core = picker_core
        self.enable_blacklist = True

    def set_blacklist_enabled(self, enabled: bool):
        self.enable_blacklist = enabled

    def draw_for_record(self, svc, highlight_client, data: dict) -> DrawResult:
        """为录制模式定制的拾取绘制"""
        try:
            if self.enable_blacklist and self._should_use_blacklist(data):
                blacklist_result = self._handle_blacklist(highlight_client)
                if blacklist_result:
                    return blacklist_result
            return self.picker_core.draw(svc, highlight_client, data)
        except Exception as e:
            logger.error(f"录制模式拾取失败: {e}")
            return DrawResult(success=False, error_message=str(e))

    def _should_use_blacklist(self, data: dict) -> bool:
        pick_type = data.get("pick_type")
        return pick_type in [PickerType.ELEMENT, PickerType.SIMILAR, PickerType.BATCH]

    def _handle_blacklist(self, highlight_client) -> Optional[DrawResult]:
        try:
            # macOS: AXUIOperate 替代 UIAOperate
            current_x, current_y = AXUIOperate.get_cursor_pos()
            current_point = Point(current_x, current_y)
            start_control = AXUIOperate.get_windows_by_point(current_point)
            if not start_control:
                raise BizException(PICKER_CONVERTER_ERROR, f"获取点位所在ax-control出错{self.picker_core.last_point}")

            process_id = AXUIOperate.get_process_id(start_control)
            process_info = find_real_application_process(process_id)
            process_name = process_info["name"]

            if process_name in RECORDING_BLACKLIST:
                logger.debug("当前应用在录制黑名单中，使用上一次的拾取结果")
                return self._use_cached_result(highlight_client, process_name)
            return None
        except Exception as e:
            logger.error(f"黑名单处理失败: {e}")
            return None

    def _use_cached_result(self, highlight_client, process_name: str) -> DrawResult:
        if self.picker_core.last_valid_rect:
            logger.info(f"当前落点是{process_name} 缓存结果是 {self.picker_core.last_valid_rect.to_json()}")
            highlight_client.draw_wnd(self.picker_core.last_valid_rect, msgs=self.picker_core.last_valid_tag)
            return DrawResult(
                success=True,
                rect=self.picker_core.last_valid_rect,
                app=process_name,
                domain=self.picker_core.last_valid_domain,
            )
        else:
            logger.info(f"缓存结果是{process_name} {-1, -1, -1, -1}")
            placeholder_rect = Rect(-1, -1, -1, -1)
            return DrawResult(
                success=True,
                rect=placeholder_rect,
                app=process_name,
                domain=None,
            )


class RecordManager:
    """录制管理器 - 统一管理录制状态、事件监控和回调"""

    def __init__(self):
        self.svc = None
        self.highlight_client = None
        self.state = RecordingState.IDLE
        self.ws_connection = None

        self.record_adapter: Optional[RecordPickerAdapter] = None

        self.drawing_thread: Optional[threading.Thread] = None
        self.stop_drawing = False

        self.event_monitor_task = None
        self.last_element = None

        self.cur_rect = None
        self.cur_app = None
        self.cur_domain = None

        self.push_callbacks = {
            "on_f4": None,
            "on_esc": None,
            "on_hover": None,
            "on_mouse_out": None,
        }

        self.hover_triggered = False
        self.hover_threshold = 0.2
        self.hover_start_time = None
        self.is_hover_paused = False
        self.last_hover_rect = None

        self.enable_record_blacklist = True

    def initialize(self, svc):
        self.svc = svc
        from astronverse.picker.core.highlight_client import highlight_client

        self.highlight_client = highlight_client
        while True:
            if not self.svc.event_core:
                logger.info("svc.event_core初始化中....")
                time.sleep(0.1)
                continue
            if not self.svc.picker_core:
                logger.info("svc.picker_core初始化中....")
                time.sleep(0.1)
                continue
            break

        if svc.picker_core and not self.record_adapter:
            self.record_adapter = RecordPickerAdapter(svc.picker_core)
            self.record_adapter.set_blacklist_enabled(self.enable_record_blacklist)

    def set_push_callbacks(
        self,
        on_f4: Callable = None,
        on_esc: Callable = None,
        on_hover: Callable = None,
        on_mouse_out: Callable = None,
    ):
        self.push_callbacks["on_f4"] = on_f4
        self.push_callbacks["on_esc"] = on_esc
        self.push_callbacks["on_hover"] = on_hover
        self.push_callbacks["on_mouse_out"] = on_mouse_out
        logger.info("录制管理器：设置推送回调函数，f4...esc...on_hover")

    async def handle_record_action(self, action: RecordAction, ws, svc, input_data) -> dict[str, Any]:
        self.initialize(svc)
        try:
            if action == RecordAction.LISTENING:
                return await self._handle_listening(ws)
            elif action == RecordAction.START:
                return await self._handle_start()
            elif action == RecordAction.PAUSE:
                return await self._handle_pause()
            elif action == RecordAction.HOVER_START:
                return await self._handle_hover_start()
            elif action == RecordAction.HOVER_END:
                return await self._handle_hover_end()
            elif action == RecordAction.AUTOMIC_END:
                return await self._handle_atomic_end(input_data)
            elif action == RecordAction.END:
                return await self._handle_end()
            else:
                return OperationResult.error(f"未知的录制动作: {action}").to_dict()
        except Exception as e:
            import traceback

            logger.error(f"处理录制动作失败: {e}\n完整堆栈信息:\n{traceback.format_exc()}")
            return OperationResult.error(str(e)).to_dict()

    async def _handle_listening(self, ws) -> dict[str, Any]:
        if self.state != RecordingState.IDLE:
            return OperationResult.error(f"无法开始监听，当前状态: {self.state.value}").to_dict()
        is_start = self.svc.event_core.start(domain=MKSign.RECORD)
        if is_start:
            logger.info("录制键鼠监听开启成功")
        self.state = RecordingState.LISTENING
        self.ws_connection = ws
        self.highlight_client.start_wnd("record")
        self.event_monitor_task = asyncio.create_task(self._monitor_events())
        logger.info("录制管理器：开始监听模式")
        return OperationResult.success().to_dict()

    async def _handle_start(self) -> dict[str, Any]:
        if self.state not in [RecordingState.LISTENING, RecordingState.PAUSED]:
            return OperationResult.error(f"无法开始录制，当前状态: {self.state.value}").to_dict()
        try:
            self.state = RecordingState.RECORDING
            self._start_continuous_drawing()
            logger.info("录制管理器：开始录制")
            return OperationResult.success().to_dict()
        except Exception as e:
            logger.info(f' "error": f"无法开始录制，当前状态: {self.state.value} {e}"')
            return OperationResult.error("无法开始录制，出现异常").to_dict()

    async def _handle_pause(self) -> dict[str, Any]:
        if self.state != RecordingState.RECORDING:
            return OperationResult.error(f"无法暂停录制，当前状态: {self.state.value}").to_dict()
        self.state = RecordingState.PAUSED
        self._stop_continuous_drawing()
        logger.info("录制管理器：暂停录制")
        return OperationResult.success().to_dict()

    async def _handle_hover_start(self) -> dict[str, Any]:
        if self.state != RecordingState.RECORDING:
            return OperationResult.error(f"无法暂停录制过程的拾取，当前状态: {self.state.value}").to_dict()
        self.is_hover_paused = True
        self.state = RecordingState.PAUSED
        self._stop_continuous_drawing()
        logger.info("录制管理器：前端hover暂停录制")
        return OperationResult.success().to_dict()

    async def _handle_hover_end(self) -> dict[str, Any]:
        if self.state != RecordingState.PAUSED and not self.is_hover_paused:
            return OperationResult.error(f"无法开始录制，当前状态: {self.state.value}").to_dict()
        self.state = RecordingState.RECORDING
        self._start_continuous_drawing()
        self.is_hover_paused = False
        logger.info("录制管理器：继续录制")
        return OperationResult.success().to_dict()

    async def _handle_atomic_end(self, input_data) -> dict[str, Any]:
        logger.info("走入_handle_atomic_end了")
        was_recording = self.state == RecordingState.RECORDING
        if was_recording:
            self._stop_continuous_drawing()
        try:
            res = self.last_element
            if isinstance(res, dict):
                res["picker_type"] = input_data.pick_type.name
                result = OperationResult.success(data=res).to_dict()
            else:
                result = OperationResult.error(res).to_dict()
            return result
        finally:
            if was_recording:
                self.state = RecordingState.RECORDING
                self._start_continuous_drawing()

    async def _handle_end(self) -> dict[str, Any]:
        if self.event_monitor_task:
            self.event_monitor_task.cancel()
            self.event_monitor_task = None
        self._stop_continuous_drawing()
        self.highlight_client.hide_wnd()
        self.svc.event_core.close()
        self.state = RecordingState.IDLE
        self.ws_connection = None
        logger.info("录制管理器：结束录制")
        return OperationResult.success().to_dict()

    def _start_continuous_drawing(self):
        if self.drawing_thread and self.drawing_thread.is_alive():
            return
        self.stop_drawing = False
        self.hover_start_time = None
        if self.record_adapter and self.record_adapter.picker_core:
            self.record_adapter.picker_core.last_valid_rect = None
            self.record_adapter.picker_core.last_valid_tag = ""
            logger.debug("已清理绘框缓存，将从当前鼠标位置重新开始")
        self.drawing_thread = threading.Thread(target=self._continuous_drawing_loop, daemon=True)
        self.drawing_thread.start()
        logger.info("启动持续绘框线程")

    def _stop_continuous_drawing(self):
        self.stop_drawing = True
        if self.drawing_thread and self.drawing_thread.is_alive():
            self.drawing_thread.join(timeout=0.5)

    def _continuous_drawing_loop(self):
        # macOS: 不需要 pythoncom.CoInitialize()
        self.highlight_client.start_wnd("record")
        while not self.stop_drawing and self.state == RecordingState.RECORDING:
            try:
                draw_data = {"pick_type": PickerType.ELEMENT}
                if self.record_adapter:
                    result: DrawResult = self.record_adapter.draw_for_record(self.svc, self.highlight_client, draw_data)
                else:
                    raise BizException(PICKER_CONVERTER_MISSING_ERROR, "缺少拾取转换器")
                if result.success and result.rect:
                    self.cur_rect = result.rect
                    self.cur_app = result.app
                    self.cur_domain = result.domain
            except Exception as e:
                import traceback

                logger.error(f"持续绘框出错: {e}\n完整堆栈信息:\n{traceback.format_exc()}")
        if not self.is_hover_paused:
            self.highlight_client.hide_wnd()

    async def _monitor_events(self):
        logger.info("开始事件监控")
        try:
            await asyncio.sleep(1)
            while self.state != RecordingState.IDLE and self.ws_connection:
                if self.svc.event_core.is_f4_pressed():
                    logger.info("检测到F4按键")
                    self.svc.event_core.reset_f4_flag()
                    if self.push_callbacks["on_f4"] and self.state in [
                        RecordingState.LISTENING,
                        RecordingState.PAUSED,
                    ]:
                        self.state = RecordingState.RECORDING
                        self._start_continuous_drawing()
                        await self.push_callbacks["on_f4"](self.ws_connection)

                if self.svc.event_core.is_cancel():
                    logger.info("检测到ESC按键")
                    if hasattr(self.svc.event_core, "reset_cancel_flag"):
                        self.svc.event_core.reset_cancel_flag()
                    if self.push_callbacks["on_esc"] and self.state in [
                        RecordingState.RECORDING,
                        RecordingState.PAUSED,
                    ]:
                        self.state = RecordingState.PAUSED
                        if self.is_hover_paused:
                            self.highlight_client.hide_wnd()
                        if not self.stop_drawing:
                            self._stop_continuous_drawing()
                        await self.push_callbacks["on_esc"](self.ws_connection)

                if self.state == RecordingState.RECORDING:
                    await self._check_mouse_hover()

                await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            logger.info("事件监控被取消")
        except Exception as e:
            logger.error(f"事件监控出错: {e}")
        finally:
            logger.info("事件监控结束")

    def _get_current_element_rect(self) -> str:
        try:
            # macOS: AXUIOperate 替代 win32api.GetCursorPos()
            x, y = AXUIOperate.get_cursor_pos()
            if not hasattr(self, "cur_rect") or self.cur_rect is None:
                raise BizException(CUR_RECT_NOT_INITIALIZED_ERROR, "cur_rect 未初始化")
            if not (self.cur_rect.left <= x <= self.cur_rect.right and self.cur_rect.top <= y <= self.cur_rect.bottom):
                raise BizException(MOUSE_POSITION_OUT_OF_RANGE_ERROR, "鼠标点位不在当前元素范围内")
            final_record_rect = {
                "left": self.cur_rect.left,
                "top": self.cur_rect.top,
                "right": self.cur_rect.right,
                "bottom": self.cur_rect.bottom,
                "mouse_x": x,
                "mouse_y": y,
                "domain": self.cur_domain,
            }
            return json.dumps(final_record_rect, ensure_ascii=False)
        except Exception as e:
            logger.error(f"获取元素矩形信息失败: {e}")
            return "{}"

    def _is_rect_changed(self, current_rect, last_rect):
        if (current_rect is None) != (last_rect is None):
            return True
        if current_rect is None and last_rect is None:
            return False
        return current_rect != last_rect

    async def _check_mouse_hover(self):
        try:
            # macOS: AXUIOperate 替代 win32api.GetCursorPos()
            current_pos = AXUIOperate.get_cursor_pos()
            current_time = time.time()

            current_rect = self.cur_rect
            if self._is_rect_changed(current_rect, self.last_hover_rect):
                if self.hover_start_time is not None:
                    logger.debug(
                        f"检测到元素矩形变化，重置悬停状态。旧矩形: {self.last_hover_rect}, 新矩形: {current_rect}"
                    )
                self.last_hover_rect = current_rect
                self.hover_start_time = None
                self.hover_triggered = False

            is_in_draw_area = (
                current_rect
                and current_rect.left <= current_pos[0] <= current_rect.right
                and current_rect.top <= current_pos[1] <= current_rect.bottom
            )
            if is_in_draw_area:
                if self.hover_start_time is None:
                    self.hover_start_time = current_time
                    self.hover_triggered = False
                    logger.debug("鼠标进入draw区域，开始悬停计时")
                elif not self.hover_triggered:
                    hover_duration = current_time - self.hover_start_time
                    if hover_duration >= self.hover_threshold:
                        logger.info(f"检测到鼠标悬停{hover_duration:.1f}秒，触发automic_start信号")
                        self.hover_triggered = True
                        rect_data = self._get_current_element_rect()
                        if self.push_callbacks["on_hover"] and (
                            not self.enable_record_blacklist or self.cur_app not in RECORDING_BLACKLIST
                        ):
                            await self.push_callbacks["on_hover"](self.ws_connection, rect_data)
                        self.last_element = self.svc.picker_core.element(self.svc, {"pick_type": PickerType.ELEMENT})
            else:
                if self.hover_start_time is not None:
                    logger.debug("鼠标离开draw区域，重置悬停状态")
                if self.hover_triggered and (
                    not self.enable_record_blacklist or self.cur_app not in RECORDING_BLACKLIST
                ):
                    await self.push_callbacks["on_mouse_out"](self.ws_connection)
                    logger.debug(f"鼠标悬停后离开draw区域，通知前端收敛红框 当前红框是{self.cur_app}")
                self.hover_start_time = None
                self.hover_triggered = False

        except Exception as e:
            import traceback

            logger.error("堆栈信息:\n{}".format(traceback.format_exc()))
            logger.error(f"悬停检测出错: {e}")

    def get_state(self) -> RecordingState:
        return self.state

    def is_recording(self) -> bool:
        return self.state == RecordingState.RECORDING

    def is_listening(self) -> bool:
        return self.state == RecordingState.LISTENING


# 全局单例
record_manager = RecordManager()
