import os
from typing import Any
from astronverse.actionlib.error import PARAM_VERIFY_ERROR_FORMAT
from astronverse.actionlib.types import typesMg
from astronverse.excel import ApplicationType
from astronverse.excel.error import BizException


class ExcelObj:
    def __init__(self, obj: Any, path: str = "", app_type: ApplicationType = ApplicationType.DEFAULT):
        self.obj = obj
        self.path = path
        self.app_type = app_type

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, ExcelObj):
            return value
        raise BizException(PARAM_VERIFY_ERROR_FORMAT.format(name, value), "{}参数验证失败{}".format(name, value))

    @property
    def is_openpyxl(self) -> bool:
        return self.app_type == ApplicationType.OPENPYXL

    def get_name(self) -> str:
        if self.path:
            return os.path.basename(self.path)
        if self.is_openpyxl:
            title = getattr(getattr(self.obj, "properties", None), "title", None)
            return title or ""
        return self.obj.Name

    @typesMg.shortcut("ExcelObj", res_type="Str")
    def get_full_name(self) -> str:
        return self.path or self.get_name()

    @typesMg.shortcut("ExcelObj", res_type="Int")
    def get_first_free_row(self) -> int:
        if self.is_openpyxl:
            from astronverse.excel.core_openpyxl.range import Range
            from astronverse.excel.core_openpyxl.worksheet import Worksheet
        else:
            from astronverse.excel.core_com.range import Range
            from astronverse.excel.core_com.worksheet import Worksheet

        worksheet = Worksheet.get_worksheet(self, "", default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        r_start_row, r_start_col, r_end_row, r_end_col, _ = used_range

        if r_end_row == 0 or r_end_col == 0:
            return 1

        for row in range(r_start_row, r_end_row + 1):
            for col in range(r_start_col, r_end_col + 1):
                val = Range.get_range_data(Worksheet.get_cell(worksheet, row, col), False)
                if val not in (None, ""):
                    break
            else:
                return row
        return r_end_row + 1
