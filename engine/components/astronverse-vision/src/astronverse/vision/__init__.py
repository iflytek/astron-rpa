from enum import Enum


class ReportLevelType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class BtnModel(Enum):  # 按键模式
    CLICK = "click"
    DOUBLE_CLICK = "double_click"


class BtnType(Enum):  # 按键类型
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


class PositionType(Enum):  # 位置类型
    CENTER = "center"
    RANDOM = "random"
    SPECIFIC = "specific"


class ExistType(Enum):  # 存在类型
    EXIST = "exist"
    NOT_EXIST = "not_exist"


class WaitType(Enum):  # 等待类型
    APPEAR = "appear"
    DISAPPEAR = "disappear"


class InputType(Enum):  # 输入类型
    TEXT = "text"
    CLIP = "clip"
