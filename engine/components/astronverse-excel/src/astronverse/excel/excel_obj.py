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

    @typesMg.shortcut("ExcelObj", res_type="Int")
    def get_first_free_row(self) -> int:
        """同get_excel_first_available_row"""

        if sys.platform == "win32":
            from astronverse.excel.core_win.worksheet import Worksheet
            from astronverse.excel.core_win.range import Range
        else:
            return 0
        worksheet = Worksheet.get_worksheet(self, "", default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        r_start_row, r_start_col, r_end_row, r_end_col, r_address = used_range

        for row in range(r_start_row, r_end_row + 1):
            for col in range(r_start_col, r_end_col + 1):
                val = Range.get_range_data(Worksheet.get_cell(worksheet, row, col), False)
                if val not in (None, ""):
                    break
            else:
                return row
        return r_end_row + 1
