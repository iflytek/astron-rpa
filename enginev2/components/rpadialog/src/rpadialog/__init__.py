from enum import Enum


class MessageType(Enum):
    MESSAGE = "message"
    WARNING = "warning"
    QUESTION = "question"
    ERROR = "error"


class ButtonType(Enum):
    CONFIRM = "confirm"
    CONFIRM_CANCEL = "confirm_cancel"
    YES_NO = "yes_no"
    YES_NO_CANCEL = "yes_no_cancel"


class InputType(Enum):
    TEXT = "text"
    PASSWORD = "password"


class SelectType(Enum):
    SINGLE = "single"
    MULTI = "multi"


class TimeType(Enum):
    TIME = "time"
    TIME_RANGE = "time_range"


class TimeFormat(Enum):
    YEAR_MONTH_DAY = "YYYY-MM-DD"
    YEAR_MONTH_DAY_HOUR_MINUTE = "YYYY-MM-DD HH:mm"
    YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = "YYYY-MM-DD HH:mm:ss"
    YEAR__MONTH__DAY = "YYYY/MM/DD"
    YEAR__MONTH_DAY__HOUR_MINUTE = "YYYY/MM/DD HH:mm"
    YEAR__MONTH_DAY__HOUR_MINUTE__SECOND = "YYYY/MM/DD HH:mm:ss"


class OpenType(Enum):
    FILE = "file"
    FOLDER = "folder"


class FileType(Enum):
    ALL = "*"
    EXCEL = ".xls,.xlsx"
    WORD = ".doc,.docx"
    TXT = ".txt"
    IMG = ".png,.jpg,.jpeg,.bmp,.gif"
    PPT = ".ppt,.pptx"
    RAR = ".zip,.rar"


class DefaultButtonC(Enum):
    CONFIRM = "confirm"


class DefaultButtonCN(Enum):
    CONFIRM = "confirm"
    CANCEL = "cancel"


class DefaultButtonY(Enum):
    YES = "yes"
    NO = "no"


class DefaultButtonYN(Enum):
    YES = "yes"
    NO = "no"
    CANCEL = "cancel"
