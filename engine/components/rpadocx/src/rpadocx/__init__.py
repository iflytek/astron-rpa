from enum import Enum

from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


class EncodingType(Enum):
    UTF = "utf-8"
    GBK = "gbk"


class SelectRangeType(Enum):
    ALL = "all"
    SELECTED = "selected"


class SaveType(Enum):
    SAVE = "save"
    SAVE_AS = "save_as"
    ABORT = "abort"


class ApplicationType(Enum):
    WORD = "Word"
    WPS = "WPS"
    DEFAULT = "Default"


class FileExistenceType(Enum):
    OVERWRITE = "overwrite"
    RENAME = "rename"
    CANCEL = "cancel"


class CloseRangeType(Enum):
    ONE = "one"
    ALL = "all"


class ReplaceType(Enum):
    IMG = "img"
    STR = "str"


class ReplaceMethodType(Enum):
    FIRST = "first"
    ALL = "all"


class SelectTextType(Enum):
    ALL = "all"
    PARAGRAPH = "paragraph"
    ROW = "row"


class CursorPointerType(Enum):
    ALL = "all"
    PARAGRAPH = "paragraph"
    ROW = "row"
    CONTENT = "content"


class CursorPositionType(Enum):
    HEAD = "head"
    TAIL = "tail"


class MoveDirectionType(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class MoveUpDownType(Enum):
    PARAGRAPH = "paragraph"
    ROW = "row"


class MoveLeftRightType(Enum):
    CHARACTER = "character"
    WORD = "word"


class InsertionType(Enum):
    PAGE = "page"
    PARAGRAPH = "paragraph"


class InsertImgType(Enum):
    FILE = "file"
    CLIPBOARD = "clipboard"


class SearchTableType(Enum):
    TEXT = "text"
    IDX = "idx"


class TableBehavior(Enum):
    DEFAULT = 0
    AUTO = 1


# class TableFitBehavior(Enum):
#     FIXED = 0
#     CONTENT = 1
#     WINDOW = 2


class RowAlignment(Enum):
    LEFT = WD_PARAGRAPH_ALIGNMENT.LEFT
    CENTER = WD_PARAGRAPH_ALIGNMENT.CENTER
    RIGHT = WD_PARAGRAPH_ALIGNMENT.RIGHT


class VerticalAlignment(Enum):
    TOP = WD_CELL_VERTICAL_ALIGNMENT.TOP
    CENTER = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    BOTTOM = WD_CELL_VERTICAL_ALIGNMENT.BOTTOM


class DeleteMode(Enum):
    ALL = "all"
    CONTENT = "content"
    RANGE = "range"


class CommentType(Enum):
    POSITION = "position"
    CONTENT = "content"


class FileType(Enum):
    PDF = "pdf"
    TXT = "txt"


class ConvertPageType(Enum):
    ALL = 0
    CURRENT = 2
    RANGE = 3
    SELECTION = 1


class SaveFileType(Enum):
    WARN = "warn"  # 提示
    GENERATE = "generate"  # 自动重命名
    OVERWRITE = "overwrite"  # 覆写


class UnderLineStyle(Enum):
    DEFAULT = 0
    LINE = 1


# class LineStyle(Enum):
#     SINGLE = 1
#     NONE = 0
#     DOUBLE = 2
