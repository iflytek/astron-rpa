"""策略管理器模块"""

import sys

from astronverse.picker import APP, PickerDomain
from astronverse.picker.strategy.types import StrategyEnv, StrategySvc
from astronverse.picker.utils.process import get_process_name

_IS_MAC = sys.platform == "darwin"


class Strategy:
    """策略管理类"""

    def __init__(self, service_context):
        self.service_context = service_context
        self.strategy_env = StrategyEnv()

    def gen_svc(self, process_id, last_point, data, start_control=None, domain=PickerDomain.AUTO) -> StrategySvc:
        process_name = get_process_name(process_id)
        app = APP.init(process_name)

        return StrategySvc(
            app=app,
            process_id=process_id,
            last_point=last_point,
            data=data,
            domain=domain,
            start_control=start_control,
        )

    def run(self, strategy_svc: StrategySvc):
        """调用策略函数"""
        import traceback

        from astronverse.picker import PickerDomain
        from astronverse.picker.logger import logger

        strategy_func = None
        error = None

        if strategy_svc.domain == PickerDomain.UIA:
            if _IS_MAC:
                from astronverse.picker.strategy.axui_strategy import axui_default_strategy

                strategy_func = axui_default_strategy
            else:
                from astronverse.picker.strategy.uia_strategy import uia_default_strategy

                strategy_func = uia_default_strategy

        elif strategy_svc.domain == PickerDomain.MSAA:
            if _IS_MAC:
                # macOS 没有 MSAA，统一走 AXUIElement
                from astronverse.picker.strategy.axui_strategy import axui_default_strategy

                strategy_func = axui_default_strategy
            else:
                from astronverse.picker.strategy.msaa_strategy import msaa_default_strategy

                strategy_func = msaa_default_strategy

        elif strategy_svc.domain == PickerDomain.WEB:
            if _IS_MAC:
                from astronverse.picker.strategy.web_strategy_mac import web_default_strategy_mac

                strategy_func = web_default_strategy_mac
            else:
                from astronverse.picker.strategy.web_strategy import web_default_strategy

                strategy_func = web_default_strategy

        elif strategy_svc.domain == PickerDomain.AUTO_DESK:
            if _IS_MAC:
                from astronverse.picker.strategy.auto_strategy_desk_mac import auto_default_strategy_desk_mac

                strategy_func = auto_default_strategy_desk_mac
            else:
                from astronverse.picker.strategy.auto_strategy_desk import auto_default_strategy_desk

                strategy_func = auto_default_strategy_desk

        elif strategy_svc.domain == PickerDomain.AUTO_WEB:
            if _IS_MAC:
                from astronverse.picker.strategy.auto_strategy_web_mac import auto_default_strategy_web_mac

                strategy_func = auto_default_strategy_web_mac
            else:
                from astronverse.picker.strategy.auto_strategy_web import auto_default_strategy_web

                strategy_func = auto_default_strategy_web

        elif strategy_svc.domain == PickerDomain.AUTO:
            if _IS_MAC:
                from astronverse.picker.strategy.auto_strategy_mac import auto_default_strategy_mac

                strategy_func = auto_default_strategy_mac
            else:
                from astronverse.picker.strategy.auto_strategy import auto_default_strategy

                strategy_func = auto_default_strategy

        if strategy_func:
            try:
                if strategy_svc.domain == PickerDomain.WEB:
                    result = strategy_func(self.service_context, strategy_svc)
                else:
                    result = strategy_func(self.service_context, self, strategy_svc)
                if result is not None:
                    return result
            except Exception as e:
                error = e
                logger.info("Strategy run error: %s %s", e, traceback.format_exc())

        if error:
            raise error
