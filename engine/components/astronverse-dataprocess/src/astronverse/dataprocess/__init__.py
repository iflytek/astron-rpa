from enum import Enum


class VariableType(Enum):
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
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    URL = "url"
    DIGIT = "digit"
    ID_NUMBER = "id_number"
    REGEX = "regex"


class ReplaceType(Enum):
    STRING = "string"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    URL = "url"
    DIGIT = "digit"
    ID_NUMBER = "id_number"
    REGEX = "regex"


class NumberType(Enum):
    INTEGER = "integer"
    FLOAT = "float"


class ListType(Enum):
    EMPTY = "empty"
    SAME_DATA = "same_data"
    USER_DEFINED = "user_defined"


class InsertMethodType(Enum):
    APPEND = "append"
    INDEX = "index"


class DeleteMethodType(Enum):
    INDEX = "index"
    VALUE = "value"


class SortMethodType(Enum):
    ASC = "asc"
    DESC = "desc"


class ConcatStringType(Enum):
    NONE = "none"
    LINEBREAK = "linebreak"
    SPACE = "space"
    HYPHEN = "hyphen"
    UNDERLINE = "underline"
    OTHER = "other"


class FillStringType(Enum):
    RIGHT = "right"
    LEFT = "left"


class StripStringType(Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class CutStringType(Enum):
    FIRST = "first"
    INDEX = "index"
    STRING = "string"


class CaseChangeType(Enum):
    UPPER = "upper"
    LOWER = "lower"
    CAPS = "caps"


class NoKeyOptionType(Enum):
    RAISE_ERROR = "raise_error"
    RETURN_DEFAULT = "return_default"


class JSONConvertType(Enum):
    JSON_TO_STR = "json_to_str"
    STR_TO_JSON = "str_to_json"


class StringConvertType(Enum):
    STR_TO_LIST = "str_to_list"
    STR_TO_DICT = "str_to_dict"
    STR_TO_TUPLE = "str_to_tuple"
    STR_TO_BOOL = "str_to_bool"
    STR_TO_INT = "str_to_int"
    STR_TO_FLOAT = "str_to_float"


class AddSubType(Enum):
    ADD = "add"
    SUB = "sub"


class MathOperatorType(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


class MathRoundType(Enum):
    ROUND = "round"
    CEIL = "ceil"
    FLOOR = "floor"
    NONE = "none"


class TimeChangeType(Enum):
    MAINTAIN = "maintain"
    ADD = "add"
    SUB = "sub"


class TimestampUnitType(Enum):
    SECOND = "second"
    MILLISECOND = "millisecond"
    MICROSECOND = "microsecond"


class TimeZoneType(Enum):
    UTC = "UTC"
    LOCAL = "local"


class TimeUnitType(Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
