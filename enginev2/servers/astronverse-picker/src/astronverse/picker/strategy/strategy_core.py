"""策略核心模块 - 兼容性导入"""

# 为了保持向后兼容性，重新导出类型和管理器
from astronverse.picker.strategy.types import StrategySvc, StrategyEnv
from astronverse.picker.strategy.manager import Strategy

# 导出所有类型供其他模块使用
__all__ = ["Strategy", "StrategySvc", "StrategyEnv"]
