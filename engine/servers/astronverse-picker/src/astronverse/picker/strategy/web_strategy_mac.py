# macOS implementation - replaces web_strategy.py
# start_control is an AXUIElementRef (not a UIA Control).
from typing import TYPE_CHECKING, Optional

from astronverse.picker import IElement, PickerSign, Point, SmartComponentAction
from astronverse.picker.engines.web_picker import web_picker
from astronverse.picker.engines.smart_component.web_picker_smart_component import web_picker_smart_component
from astronverse.picker.logger import logger
from astronverse.picker.strategy.types import StrategySvc
from astronverse.picker.error import BizException, PARAM_ERROR_FORMAT

if TYPE_CHECKING:
    from astronverse.picker.svc import ServiceContext


def web_default_strategy_mac(service: "ServiceContext", strategy_svc: StrategySvc, cache=None) -> Optional[IElement]:
    """macOS web 策略，替代 web_strategy.py

    cache 由 auto_strategy_web_mac 传入（is_document 已由 AXUIOperate.get_web_control 判断）：
        (is_document, menu_top, menu_left, window_ref)

    cache=None 时（智能拾取路径）：直接从 start_control 的 AXFrame 读取坐标。
    根据提示内容，此时 start_control 就是 DOMClassList==View 的节点 A，
    其 AXPosition 即为浏览器内容区域的左上角坐标。
    """
    if cache:
        is_document, menu_top, menu_left, window_ref = cache
        menu_right, menu_bottom = None, None
    else:
        # 从 AXUIElement 读取 AXFrame 替代 BoundingRectangle
        from astronverse.picker.engines.axui_picker import _ax_attr, _ax_unpack_rect, _ax_unpack_point, _ax_unpack_size

        el = strategy_svc.start_control
        frame_v = _ax_attr(el, "AXFrame")
        if frame_v is not None:
            r = _ax_unpack_rect(frame_v)
            if r:
                menu_left, menu_top, w, h = r
                menu_right = menu_left + w
                menu_bottom = menu_top + h
            else:
                return None
        else:
            pv = _ax_attr(el, "AXPosition")
            sv = _ax_attr(el, "AXSize")
            if pv is None or sv is None:
                return None
            pt = _ax_unpack_point(pv)
            sz = _ax_unpack_size(sv)
            if not pt or not sz:
                return None
            menu_left, menu_top = pt
            menu_right = menu_left + sz[0]
            menu_bottom = menu_top + sz[1]
        is_document = True
        window_ref = _ax_attr(el, "AXWindow")

    if not is_document:
        return None

    logger.info(f"测试data数据 {strategy_svc}")
    if strategy_svc.data.get("pick_sign", "") != PickerSign.SMART_COMPONENT:
        ele = web_picker.get_element(
            root_control=strategy_svc.start_control,
            route_port=service.route_port,
            strategy_svc=strategy_svc,
            left_top_point=Point(menu_left, menu_top),
            right_bottom_point=Point(menu_right, menu_bottom),
        )
    else:
        smart_component_action = strategy_svc.data.get("smart_component_action", "")
        if smart_component_action == SmartComponentAction.START:
            ele = web_picker_smart_component.get_element(
                root_control=strategy_svc.start_control,
                route_port=service.route_port,
                strategy_svc=strategy_svc,
                left_top_point=Point(menu_left, menu_top),
                right_bottom_point=Point(menu_right, menu_bottom),
            )
        elif smart_component_action == SmartComponentAction.PREVIOUS:
            ele = web_picker_smart_component.getParentElement(
                root_control=strategy_svc.start_control,
                route_port=service.route_port,
                strategy_svc=strategy_svc,
                left_top_point=Point(menu_left, menu_top),
                right_bottom_point=Point(menu_right, menu_bottom),
            )
        elif smart_component_action == SmartComponentAction.NEXT:
            ele = web_picker_smart_component.getChildElement(
                root_control=strategy_svc.start_control,
                route_port=service.route_port,
                strategy_svc=strategy_svc,
                left_top_point=Point(menu_left, menu_top),
            )
        else:
            error_msg = f"拾取接口参数传递异常,不存在SmartComponentAction {smart_component_action}"
            raise BizException(PARAM_ERROR_FORMAT.format(error_msg), error_msg)
    return ele
