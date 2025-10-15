"""
对话相关的枚举类型定义。
"""

from enum import Enum


class MessageType(Enum):
    """消息类型枚举。"""

    MESSAGE = "message"
    WARNING = "warning"
    QUESTION = "question"
    ERROR = "error"


class ButtonType(Enum):
    """按钮类型枚举。"""

    CONFIRM = "confirm"
    CONFIRM_CANCEL = "confirm_cancel"
    YES_NO = "yes_no"
    YES_NO_CANCEL = "yes_no_cancel"


class InputType(Enum):
    """输入类型枚举。"""

    TEXT = "text"
    PASSWORD = "password"


class SelectType(Enum):
    """选择类型枚举。"""

    SINGLE = "single"
    MULTI = "multi"


class TimeType(Enum):
    """时间类型枚举。"""

    TIME = "time"
    TIME_RANGE = "time_range"


class TimeFormat(Enum):
    """时间格式枚举。"""

    YEAR_MONTH_DAY = "YYYY-MM-DD"
    YEAR_MONTH_DAY_HOUR_MINUTE = "YYYY-MM-DD HH:mm"
    YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = "YYYY-MM-DD HH:mm:ss"
    YEAR_MONTH_DAY_SLASH = "YYYY/MM/DD"
    YEAR_MONTH_DAY_HOUR_MINUTE_SLASH = "YYYY/MM/DD HH:mm"
    YEAR_MONTH_DAY_HOUR_MINUTE_SECOND_SLASH = "YYYY/MM/DD HH:mm:ss"


class OpenType(Enum):
    """打开类型枚举。"""

    FILE = "file"
    FOLDER = "folder"


class FileType(Enum):
    """文件类型枚举。"""

    ALL = "*"
    EXCEL = ".xls,.xlsx"
    WORD = ".doc,.docx"
    TXT = ".txt"
    IMG = ".png,.jpg,.jpeg,.bmp,.gif"
    PPT = ".ppt,.pptx"
    RAR = ".zip,.rar"


class DefaultButtonC(Enum):
    """仅确认按钮枚举。"""

    CONFIRM = "confirm"


class DefaultButtonCN(Enum):
    """确认和取消按钮枚举。"""

    CONFIRM = "confirm"
    CANCEL = "cancel"


class DefaultButtonY(Enum):
    """是和否按钮枚举。"""

    YES = "yes"
    NO = "no"


class DefaultButtonYN(Enum):
    """是、否和取消按钮枚举。"""

    YES = "yes"
    NO = "no"
    CANCEL = "cancel"
