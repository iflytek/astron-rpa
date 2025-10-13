"""Report 组件基础类型与枚举。

暴露 `ReportLevelType` 供外部选择日志级别使用。
"""

from enum import Enum

__all__ = ["ReportLevelType"]


class ReportLevelType(Enum):
    """用户日志级别枚举。

    值使用小写字符串以便统一向下游（例如序列化/前端）输出。
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
