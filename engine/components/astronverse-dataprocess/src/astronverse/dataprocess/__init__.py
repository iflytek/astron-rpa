"""
数据处理相关类型定义模块。
"""

from enum import Enum


class VariableType(Enum):
    """变量类型枚举"""

    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    JSON = "json"
    TUPLE = "tuple"
    OTHER = "other"


class ExtractType(Enum):
    """提取类型枚举。"""

    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    URL = "url"
    DIGIT = "digit"
    ID_NUMBER = "id_number"
    REGEX = "regex"


class ReplaceType(Enum):
    """替换类型枚举。"""

    STRING = "string"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    URL = "url"
    DIGIT = "digit"
    ID_NUMBER = "id_number"
    REGEX = "regex"


class NumberType(Enum):
    """数字类型枚举。"""

    INTEGER = "integer"
    FLOAT = "float"


class ListType(Enum):
    """列表类型枚举。"""

    EMPTY = "empty"
    SAME_DATA = "same_data"
    USER_DEFINED = "user_defined"


class InsertMethodType(Enum):
    """插入方法类型枚举。"""

    APPEND = "append"
    INDEX = "index"


class DeleteMethodType(Enum):
    """删除方法类型枚举。"""

    INDEX = "index"
    VALUE = "value"


class SortMethodType(Enum):
    """排序方法类型枚举。"""

    ASC = "asc"
    DESC = "desc"


class ConcatStringType(Enum):
    """字符串拼接类型枚举。"""

    NONE = "none"
    LINEBREAK = "linebreak"
    SPACE = "space"
    HYPHEN = "hyphen"
    UNDERLINE = "underline"
    OTHER = "other"


class FillStringType(Enum):
    """字符串填充类型枚举。"""

    RIGHT = "right"
    LEFT = "left"


class StripStringType(Enum):
    """字符串去除类型枚举。"""

    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class CutStringType(Enum):
    """字符串裁剪类型枚举。"""

    FIRST = "first"
    INDEX = "index"
    STRING = "string"


class CaseChangeType(Enum):
    """字符串大小写变换类型枚举。"""

    UPPER = "upper"
    LOWER = "lower"
    CAPS = "caps"


class NoKeyOptionType(Enum):
    """无 key 选项类型枚举。"""

    RAISE_ERROR = "raise_error"
    RETURN_DEFAULT = "return_default"


class JSONConvertType(Enum):
    """JSON 转换类型枚举。"""

    JSON_TO_STR = "json_to_str"
    STR_TO_JSON = "str_to_json"


class StringConvertType(Enum):
    """字符串转换类型枚举。"""

    STR_TO_LIST = "str_to_list"
    STR_TO_DICT = "str_to_dict"
    STR_TO_TUPLE = "str_to_tuple"
    STR_TO_BOOL = "str_to_bool"
    STR_TO_INT = "str_to_int"
    STR_TO_FLOAT = "str_to_float"


class AddSubType(Enum):
    """加减类型枚举。"""

    ADD = "add"
    SUB = "sub"


class MathOperatorType(Enum):
    """数学运算符类型枚举。"""

    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


class MathRoundType(Enum):
    """数学取整类型枚举。"""

    ROUND = "round"
    CEIL = "ceil"
    FLOOR = "floor"
    NONE = "none"


class TimeChangeType(Enum):
    """时间变换类型枚举。"""

    MAINTAIN = "maintain"
    ADD = "add"
    SUB = "sub"


class TimestampUnitType(Enum):
    """时间戳单位类型枚举。"""

    SECOND = "second"
    MILLISECOND = "millisecond"
    MICROSECOND = "microsecond"


class TimeZoneType(Enum):
    """时区类型枚举。"""

    UTC = "UTC"
    LOCAL = "local"


class TimeUnitType(Enum):
    """时间单位类型枚举。"""

    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
