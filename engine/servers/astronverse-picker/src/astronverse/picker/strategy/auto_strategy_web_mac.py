# macOS stub - implementation pending
# Replaces auto_strategy_web.py on macOS.
# Browser Document detection uses AXUIElement (AXWebArea) instead of UIA + COMError.
import traceback
from typing import TYPE_CHECKING, Optional

from astronverse.picker import APP, IElement
from astronverse.picker.logger import logger

if TYPE_CHECKING:
    from astronverse.picker.strategy.types import Strategy, StrategySvc
    from astronverse.picker.svc import ServiceContext


def auto_default_strategy_web_mac(
    service: "ServiceContext", strategy: "Strategy", strategy_svc: "StrategySvc"
) -> Optional[IElement]:
    """macOS web 自动选择策略 - 替代 auto_strategy_web.py

    TODO: 用 AXUIOperate.get_web_control() 判断是否在浏览器 Document 区域内。
    AXUIElement 判断逻辑：
      - 遍历 AXUIElement 树，查找 AXRole == "AXWebArea" 的节点
      - 从 AXFrame 获取 (top, left, width, height)
      - 从 AXWindow 获取窗口引用（替代 HWND）
    """
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
            return web_default_strategy_mac(service, strategy_svc, web_cache)

    return None
