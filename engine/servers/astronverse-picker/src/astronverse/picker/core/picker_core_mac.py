import threading
import time
from typing import Optional

from astronverse.picker import (
    DrawResult,
    IElement,
    IPickerCore,
    PickerDomain,
    PickerSign,
    PickerType,
    Point,
    Rect,
    SmartComponentAction,
)
from astronverse.picker.engines.axui_picker import AXUIElement, AXUIOperate
from astronverse.picker.logger import logger
from astronverse.picker.utils.browser import BrowserControlFinder


class PickerCore(IPickerCore):
    """macOS 拾取核心，对应 picker_core_win.py，基于 AXUIElement"""

    def __init__(self):
        self.last_point = Point(0, 0)
        self.last_element: Optional[IElement] = None
        self.last_strategy_svc = None
        self.lock = threading.Lock()

        self.last_valid_rect: Optional[Rect] = None
        self.last_valid_tag: str = ""
        self.last_valid_domain: Optional[str] = None

    def _get_element_domain(self, element: IElement) -> str:
        element_type = type(element).__name__
        if element_type == "AXUIElement":
            return PickerDomain.UIA.value  # macOS 统一用 UIA domain 标识
        elif element_type == "WEBElement":
            return PickerDomain.WEB.value
        else:
            logger.warning(f"无法确定元素类型 {element_type}，使用默认 UIA domain")
            return PickerDomain.UIA.value

    def draw(self, svc, highlight_client, data: dict) -> DrawResult:
        """拾取绘制，逻辑与 picker_core_win.py 一致，底层换成 AXUIOperate"""
        try:
            p_x, p_y = AXUIOperate.get_cursor_pos()
            self.last_point.x = p_x
            self.last_point.y = p_y
            pick_type = data.get("pick_type")

            if pick_type == PickerType.POINT:
                return DrawResult(success=True)
            elif pick_type == PickerType.WINDOW:
                return self._draw_window(svc, highlight_client, data)
            elif pick_type in [PickerType.ELEMENT, PickerType.SIMILAR, PickerType.BATCH]:
                return self._draw_element(svc, highlight_client, data)
            else:
                return DrawResult(success=False, error_message=f"不支持的拾取类型: {pick_type}")

        except Exception as e:
            logger.error(f"拾取绘制失败: {e}")
            return DrawResult(success=False, error_message=str(e))

    def _draw_window(self, svc, highlight_client, data: dict) -> DrawResult:
        start_element = AXUIOperate.get_windows_by_point(self.last_point)
        result_element = AXUIOperate.get_app_windows(start_element)
        if not result_element:
            return DrawResult(success=False, error_message="")
        with self.lock:
            self.last_element = AXUIElement(element=result_element)
        process_id = AXUIOperate.get_process_id(start_element)
        self.last_strategy_svc = svc.strategy.gen_svc(
            process_id=process_id,
            last_point=self.last_point,
            data=data,
            start_control=start_element,
            domain=PickerDomain.UIA,
        )
        rect = self.last_element.rect()
        tag = self.last_element.tag()
        highlight_client.draw_wnd(rect, msgs=tag)
        return DrawResult(
            success=True,
            rect=rect,
            app=self.last_strategy_svc.app.value,
            domain=PickerDomain.UIA.value,
        )

    def _draw_element(self, svc, highlight_client, data: dict) -> DrawResult:
        start_element = AXUIOperate.get_windows_by_point(self.last_point)
        if not start_element:
            logger.info("拾取预处理 start_element 为空")
            return DrawResult(success=False)

        process_id = AXUIOperate.get_process_id(start_element)

        if not svc.strategy:
            timeout, wait_time = 10, 0
            while not svc.strategy and wait_time < timeout:
                time.sleep(0.1)
                wait_time += 0.1
            if not svc.strategy:
                return DrawResult(success=False, error_message="策略加载超时（10s）")
            logger.info("strategy 加载完成")

        domain = PickerDomain.AUTO
        pick_mode = data.get("pick_mode")
        if pick_mode:
            domain = PickerDomain.AUTO_WEB if pick_mode == "WebPick" else PickerDomain.AUTO_DESK

        self.last_strategy_svc = svc.strategy.gen_svc(
            process_id=process_id,
            last_point=self.last_point,
            data=data,
            start_control=start_element,
            domain=domain,
        )

        res = svc.strategy.run(self.last_strategy_svc)
        if not res:
            return DrawResult(success=False, error_message="")

        with self.lock:
            self.last_element = res
        current_rect = self.last_element.rect()
        current_tag = self.last_element.tag()
        actual_domain = self._get_element_domain(self.last_element)

        self.last_valid_rect = current_rect
        self.last_valid_tag = current_tag
        self.last_valid_domain = actual_domain

        highlight_client.draw_wnd(current_rect, msgs=current_tag)
        return DrawResult(
            success=True,
            rect=current_rect,
            app=self.last_strategy_svc.app.value,
            domain=actual_domain,
        )

    def element(self, svc, data: dict) -> dict:
        pick_type = data.get("pick_type")
        if pick_type == PickerType.POINT:
            return {"point": {"x": self.last_point.x, "y": self.last_point.y}, "version": "1"}
        elif pick_type in [PickerType.WINDOW, PickerType.ELEMENT, PickerType.SIMILAR, PickerType.BATCH]:
            with self.lock:
                if self.last_element:
                    return self.last_element.path(svc, self.last_strategy_svc)
                return {}
        else:
            raise NotImplementedError()
