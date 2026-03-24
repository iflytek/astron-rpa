# macOS stub - implementation pending
# Replaces auto_strategy_desk.py on macOS.
# Desktop-only auto strategy: no browser detection, no MSAA, fallback to AXUIElement.
import traceback
from typing import TYPE_CHECKING, Optional

from astronverse.picker import IElement
from astronverse.picker.logger import logger

if TYPE_CHECKING:
    from astronverse.picker.strategy.types import Strategy, StrategySvc
    from astronverse.picker.svc import ServiceContext


def auto_default_strategy_desk_mac(
    service: "ServiceContext", strategy: "Strategy", strategy_svc: "StrategySvc"
) -> Optional[IElement]:
    """macOS 桌面自动选择策略 - 替代 auto_strategy_desk.py

    macOS 上无 MSAA / JAB / SAP，桌面应用统一走 AXUIElement。
    TODO: 如果后续需要支持 JAB (Java Accessibility Bridge on macOS)，在此添加分支。
    """
    from astronverse.picker.strategy.axui_strategy import axui_default_strategy

    try:
        return axui_default_strategy(service, strategy, strategy_svc)
    except Exception as e:
        logger.error(f"auto_default_strategy_desk_mac error: {e} {traceback.format_exc()}")
        return None
