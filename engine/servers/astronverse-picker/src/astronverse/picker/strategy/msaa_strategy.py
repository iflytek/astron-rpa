from astronverse.picker import IElement
from astronverse.picker.engines.msaa_picker import MSAAPicker
from astronverse.picker.strategy.types import StrategySvc


def msaa_default_strategy(strategy_svc: StrategySvc) -> IElement:
    """默认策略"""

    ele = MSAAPicker.get_element(point=strategy_svc.last_point, pid=strategy_svc.process_id)
    return ele
