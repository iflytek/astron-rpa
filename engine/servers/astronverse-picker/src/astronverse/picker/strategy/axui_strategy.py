# macOS stub - implementation pending
# Handles both UIA and MSAA domains on macOS (both route here via manager.py).
from typing import TYPE_CHECKING, Optional

from astronverse.picker import IElement
from astronverse.picker.strategy.types import StrategySvc

if TYPE_CHECKING:
    from astronverse.picker.strategy.types import Strategy
    from astronverse.picker.svc import ServiceContext


def axui_default_strategy(
    service: "ServiceContext", strategy: "Strategy", strategy_svc: StrategySvc
) -> Optional[IElement]:
    """macOS AXUIElement 策略 - 替代 uia_default_strategy 和 msaa_default_strategy

    TODO: 实现后导入 axui_picker 并调用 AXUIPicker.get_element()
    """
    from astronverse.picker.engines.axui_picker import AXUIElement, axui_picker

    ele = axui_picker.get_element(
        root=AXUIElement(element=strategy_svc.start_control),
        point=strategy_svc.last_point,
    )
    return ele
