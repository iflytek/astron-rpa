from enum import Enum
import ast
from astronverse.pdf.error import *


def _handle_files_input(files_path):
    if isinstance(files_path, str):
        if files_path.startswith("[") and files_path.endswith("]"):
            files_path = ast.literal_eval(files_path)
        else:
            files_path = files_path.split(".pdf,")
            for i in range(len(files_path)):
                if i != len(files_path) - 1:
                    # 最后一项是正常路径
                    files_path[i] = files_path[i].strip() + ".pdf"
    elif not isinstance(files_path, list):
        raise BaseException(FILE_PATH_ERROR_FORMAT.format(str(files_path)), "PDF文件路径有误，请输入正确的路径")


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


class ImageLayoutType(Enum):
    SINGLE_PAGE = "single_page"
    MULTIPLE_PAGES = "multiple_pages"
