import threading
import time
import traceback
from typing import Optional

from astronverse.picker import (
    DrawResult,
    IElement,
    PickerAction,
    PickerDomain,
    PickerType,
    Point,
    Rect,
)
from astronverse.picker.engines.uia_picker import UIAElement, UIAOperate
from astronverse.picker.logger import logger


def _get_element_domain(element: IElement) -> str:
    element_type = type(element).__name__
    if element_type == "UIAElement":
        return PickerDomain.UIA.value
    elif element_type == "WEBElement":
        return PickerDomain.WEB.value
    elif element_type == "MSAAElement":
        return PickerDomain.MSAA.value
    else:
        logger.warning(f"无法确定元素类型 {element_type}，使用默认 UIA domain")
        return PickerDomain.UIA.value


class NormalPickServer:
    """普通拾取服务 - 处理普通拾取信号，包含拾取核心逻辑"""

    def __init__(self, service_context):
        # 核心服务组件
        self.service_context = service_context
        self.event_core = service_context.event_core
        self.hl = service_context.ws_server.hl

        # lock 保护 last_element 的读写
        self.lock = threading.Lock()

        # 缓存上一个拾取信息并对后续处理
        self.last_point = Point(0, 0)
        self.last_element: Optional[IElement] = None
        self.last_strategy_svc = None
        self.last_valid_rect: Optional[Rect] = None
        self.last_valid_tag: str = ""
        self.last_valid_domain: Optional[str] = None

    def handle(self, sign):
        """处理普通拾取信号"""
        if PickerAction.STOP.value in sign:
            self.hl.hide_sync()
            self.event_core.close()

            result = None

            del sign[PickerAction.STOP.value]
            sign["{}_RES".format(PickerAction.STOP.value)] = result
            logger.info("拾取结束，外部退出")
        elif PickerAction.START.value in sign:
            is_start = self.event_core.start()
            if is_start:
                logger.info("拾取开始")
            is_focus = self.event_core.is_focus()
            is_cancel = self.event_core.is_cancel()
            if is_focus or is_cancel:

                self.hl.hide_sync()
                self.event_core.close()

                result = "cancel"

                if is_focus:
                    try:
                        picker_data = sign[PickerAction.START.value]
                        result = self.element(self.service_context, picker_data)
                    except Exception as e:
                        result = "{}".format(e)

                del sign[PickerAction.START.value]
                sign["{}_RES".format(PickerAction.START.value)] = result
                logger.info("拾取结束，主动退出")
            else:
                draw_result: DrawResult = self.draw(
                    self.service_context,
                    sign[PickerAction.START.value],
                )
                if not draw_result.success and draw_result.error_message:

                    self.hl.hide_sync()
                    self.event_core.close()

                    result = "{}".format(draw_result.error_message)

                    del sign[PickerAction.START.value]
                    sign["{}_RES".format(PickerAction.START.value)] = result
                    logger.info("拾取因异常结束")

    def draw(self, svc, data: dict) -> DrawResult:
        try:
            p_x, p_y = UIAOperate.get_cursor_pos()
            self.last_point.x = p_x
            self.last_point.y = p_y
            pick_type = data.get("pick_type")

            if pick_type == PickerType.POINT:
                return DrawResult(success=True)
            elif pick_type == PickerType.WINDOW:
                start_control = UIAOperate.get_windows_by_point(self.last_point)
                result_control = UIAOperate.get_app_windows(start_control)
                if not result_control:
                    return DrawResult(success=False, error_message="")
                with self.lock:
                    self.last_element = UIAElement(control=result_control)
                process_id = UIAOperate.get_process_id(start_control)
                self.last_strategy_svc = svc.strategy.gen_svc(
                    process_id=process_id,
                    last_point=self.last_point,
                    data=data,
                    start_control=start_control,
                    domain=PickerDomain.UIA,
                )
                rect = self.last_element.rect()
                tag = self.last_element.tag()
                self.hl.draw_sync(rect, msgs=tag)
                return DrawResult(
                    success=True,
                    rect=rect,
                    app=self.last_strategy_svc.app.value,
                    domain=PickerDomain.UIA.value,
                )
            elif pick_type in [PickerType.ELEMENT, PickerType.SIMILAR, PickerType.BATCH]:
                start_control = UIAOperate.get_windows_by_point(self.last_point)
                if not start_control:
                    logger.info("拾取预处理 start_control 为空")
                    return DrawResult(success=False, error_message="未找到起始控件")

                process_id = UIAOperate.get_process_id(start_control)

                if not svc.strategy:
                    timeout = 10
                    wait_time = 0
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
                    start_control=start_control,
                    domain=domain,
                )

                res = svc.strategy.run(self.last_strategy_svc)
                if not res:
                    return DrawResult(success=False, error_message="")

                with self.lock:
                    self.last_element = res
                current_rect = self.last_element.rect()
                current_tag = self.last_element.tag()
                actual_domain = _get_element_domain(self.last_element)

                self.last_valid_rect = current_rect
                self.last_valid_tag = current_tag
                self.last_valid_domain = actual_domain

                self.hl.draw_sync(current_rect, msgs=current_tag)
                return DrawResult(
                    success=True,
                    rect=current_rect,
                    app=self.last_strategy_svc.app.value,
                    domain=actual_domain,
                )
            else:
                return DrawResult(success=False, error_message=f"不支持的拾取类型: {pick_type}")
        except Exception as e:
            logger.error(f"拾取绘制失败: {e}")
            return DrawResult(success=False, error_message=str(e))

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
