# macOS stub - implementation pending
# Replaces auto_strategy.py on macOS.
# Browser detection uses AXUIElement instead of UIA + COMError.
import traceback
from typing import TYPE_CHECKING, Optional

from astronverse.picker import APP, MSAA_APPLICATIONS, IElement
from astronverse.picker.logger import logger

if TYPE_CHECKING:
    from astronverse.picker.strategy.types import Strategy, StrategySvc
    from astronverse.picker.svc import ServiceContext


def auto_default_strategy_mac(
    service: "ServiceContext", strategy: "Strategy", strategy_svc: "StrategySvc"
) -> Optional[IElement]:
    """macOS 自动选择策略 - 替代 auto_strategy.py

    分发逻辑与 Windows 版相同，但：
    - 浏览器 Document 判断用 AXUIOperate.get_web_control() (AXWebArea)
    - 桌面元素用 axui_default_strategy
    - 无 MSAA / COMError / IE
    """
    from astronverse.picker.strategy.axui_strategy import axui_default_strategy
    from astronverse.picker.strategy.web_strategy_mac import web_default_strategy_mac

    chrome_like_apps = [
        APP.Chrome,
        APP.Firefox,
        APP.Chrome360X,
        APP.Chrome360se,
        APP.Chrome360,
        APP.Edge,
        APP.Chromium,
    ]

    preliminary_element = None

    if strategy_svc.app in chrome_like_apps:
        try:
            # TODO: 用 AXUIOperate.get_web_control() 替代 UIAOperate.get_web_control()
            from astronverse.picker.engines.axui_picker import AXUIOperate

            web_control_result = AXUIOperate.get_web_control(
                strategy_svc.start_control,
                strategy_svc.app,
                strategy_svc.last_point,
            )
            is_document, menu_top, menu_left, window_ref = web_control_result
        except Exception as e:
            logger.error("堆栈信息:\n{}".format(traceback.format_exc()))
            return None

        if is_document:
            web_cache = (is_document, menu_top, menu_left, window_ref)
            preliminary_element = web_default_strategy_mac(service, strategy_svc, web_cache)
            return preliminary_element
    else:
        # macOS 上无 MSAA，桌面应用统一走 AXUIElement
        try:
            preliminary_element = axui_default_strategy(service, strategy, strategy_svc)
        except Exception as e:
            logger.error(f"auto_default_strategy_mac axui error: {e} {traceback.extract_stack()}")

    # 兜底
    axui_element = None
    try:
        axui_element = axui_default_strategy(service, strategy, strategy_svc)
    except Exception as e:
        logger.error(f"auto_default_strategy_mac axui fallback error: {e} {traceback.extract_stack()}")

    if axui_element is None and preliminary_element is not None:
        return preliminary_element
    if preliminary_element is None and axui_element is not None:
        return axui_element
    if axui_element is None and preliminary_element is None:
        return None
    if preliminary_element.rect().area() <= axui_element.rect().area():
        return preliminary_element
    return axui_element
