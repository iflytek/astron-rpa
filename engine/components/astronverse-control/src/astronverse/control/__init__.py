"""控制流相关枚举类型。

提供控制流组件所需的枚举定义。
"""

from enum import Enum

__all__ = []


class ConditionType(Enum):
    """条件类型枚举"""

    EQ = "=="  # 等于
    NE = "!="  # 不等于
    GT = ">"  # 大于
    GE = ">="  # 大于等于
    LT = "<"  # 小于
    LE = "<="  # 小于等于
    IN = "in"  # 包含
    NOT_IN = "notin"  # 不包含
    TRUE = "true"  # 为真
    FALSE = "false"  # 为假
    EMPTY = "empty"  # 为空
    NOT_EMPTY = "notempty"  # 不为空
