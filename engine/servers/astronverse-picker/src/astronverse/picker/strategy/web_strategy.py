from typing import TYPE_CHECKING, Optional

from astronverse.picker import WEB_CLASS_NAMES, IElement, Point, PickerSign, SmartComponentAction
from astronverse.picker.engines.smart_component.web_picker_smart_component import web_picker_smart_component
from astronverse.picker.engines.uia_picker import UIAOperate
from astronverse.picker.engines.web_picker import web_picker
from astronverse.picker.strategy.types import StrategySvc
from astronverse.picker.logger import logger


# 使用TYPE_CHECKING避免循环导入
if TYPE_CHECKING:
    from astronverse.picker.svc import ServiceContext


def web_default_strategy(service: "ServiceContext", strategy_svc: StrategySvc, cache=None) -> Optional[IElement]:
    """默认策略"""
    if cache:
        is_document, menu_top, menu_left, hwnd = cache
        menu_right, menu_bottom = None, None
    else:
        bound = strategy_svc.start_control.BoundingRectangle  ##专为智能拾取定制
        is_document, menu_top, menu_left, menu_right, menu_bottom, hwnd = (
            True,
            bound.top,
            bound.left,
            bound.right,
            bound.bottom,
            strategy_svc.start_control.NativeWindowHandle,
        )
    if not is_document:
        return None

    logger.info(f"测试data数据 {strategy_svc}")
    if (
        strategy_svc.data.get("pick_sign", "") != PickerSign.SMART_COMPONENT
    ):  ##对于不是使用各类基础拾取的业务，需要走定制
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
            raise Exception(f"拾取接口参数传递异常,不存在SmartComponentAction {smart_component_action}")
    return ele
