"""策略管理器模块"""

from astronverse.picker.strategy.types import StrategyEnv, StrategySvc
from astronverse.picker.utils.process import get_process_name
from astronverse.picker import APP, PickerDomain


class Strategy:
    """策略管理类"""

    def __init__(self, service_context):
        self.service_context = service_context
        self.strategy_env = StrategyEnv()

    def gen_svc(self, process_id, last_point, data, start_control=None) -> StrategySvc:
        process_name = get_process_name(process_id)
        app = APP.init(process_name)

        # 默认自动选择AUTO模式
        domain = PickerDomain.AUTO

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
        from astronverse.picker import IElement, PickerDomain
        from astronverse.picker.logger import logger
        import traceback

        # 根据domain动态导入对应的策略函数
        strategy_func = None
        error = None

        if strategy_svc.domain == PickerDomain.UIA:
            from astronverse.picker.strategy.uia_strategy import uia_default_strategy

            strategy_func = uia_default_strategy
        elif strategy_svc.domain == PickerDomain.WEB:
            from astronverse.picker.strategy.web_strategy import web_default_strategy

            strategy_func = web_default_strategy
        elif strategy_svc.domain == PickerDomain.MSAA:
            from astronverse.picker.strategy.msaa_strategy import msaa_default_strategy

            strategy_func = msaa_default_strategy
        elif strategy_svc.domain == PickerDomain.AUTO:
            from astronverse.picker.strategy.auto_strategy import auto_default_strategy

            strategy_func = auto_default_strategy

        if strategy_func:
            try:
                result = strategy_func(self.service_context, self, strategy_svc)
                if result is not None:
                    return result
            except Exception as e:
                error = e
                logger.info("Strategy run error: %s %s", e, traceback.format_exc())

        if error:
            raise error
