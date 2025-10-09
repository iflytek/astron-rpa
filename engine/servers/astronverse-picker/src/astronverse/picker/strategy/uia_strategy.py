from astronverse.picker import IElement
from astronverse.picker.engines.uia_picker import UIAElement, uia_picker
from astronverse.picker.strategy.types import StrategySvc


def uia_default_strategy(strategy_svc: StrategySvc) -> IElement:
    """
    默认策略
    strategy_svc 策略上下文
    """

    ele = uia_picker.get_element(
        root=UIAElement(control=strategy_svc.start_control),
        point=strategy_svc.last_point,
        # 下面就是配置
        used_cache=False,
        root_need_init=True,
        ignore_parent_zero=True,
    )
    return ele
