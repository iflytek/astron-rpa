import sys
from typing import Any

from astronverse.actionlib.error import PARAM_VERIFY_ERROR_FORMAT
from astronverse.actionlib.types import typesMg
from astronverse.excel.error import *


class ExcelObj:
    """Excel对象"""

    def __init__(self, obj: Any, path: str = ""):
        self.obj = obj
        self.path = path

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, ExcelObj):
            return value
        raise BaseException(PARAM_VERIFY_ERROR_FORMAT.format(name, value), "{}参数验证失败{}".format(name, value))

    def get_name(self):
        if sys.platform == "win32":
            return self.obj.Name
        else:
            return ""

    @typesMg.shortcut("ExcelObj", res_type="Str")
    def get_full_name(self) -> str:
        return self.path or self.get_name()
