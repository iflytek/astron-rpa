import ast
import os
from enum import Enum

from astronverse.pdf.error import *


def _handle_files_input(files_path):
    if isinstance(files_path, str):
        files_path = files_path.strip()
        if files_path.startswith("[") and files_path.endswith("]"):
            parsed_files = ast.literal_eval(files_path)
            if not isinstance(parsed_files, list):
                raise BaseException(FILE_PATH_ERROR_FORMAT.format(files_path), "PDF文件路径有误，请输入正确的路径")
            files_path = parsed_files
        elif os.path.exists(files_path):
            files_path = [files_path]
        elif ".pdf," in files_path:
            files_path = files_path.split(".pdf,")
            for i in range(len(files_path) - 1):
                files_path[i] = files_path[i].strip() + ".pdf"
        else:
            files_path = [item.strip() for item in files_path.split(",") if item.strip()]
    elif not isinstance(files_path, list):
        raise BaseException(FILE_PATH_ERROR_FORMAT.format(str(files_path)), "PDF文件路径有误，请输入正确的路径")

    return files_path


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
