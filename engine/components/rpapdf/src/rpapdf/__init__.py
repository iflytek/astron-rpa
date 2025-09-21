from enum import Enum


class FileExistenceType(Enum):
    OVERWRITE = "overwrite"
    RENAME = "rename"
    CANCEL = "cancel"


class PictureType(Enum):
    PNG = "png"
    JPEG = "jpeg"


class MergeType(Enum):
    FOLDER = "folder"
    FILE = "file"


class SelectRangeType(Enum):
    ALL = "all"
    PART = "part"


class TextSaveType(Enum):
    NONE = "none"
    WORD = "word"
    TXT = "txt"
    WORD_AND_TXT = "word_and_txt"
