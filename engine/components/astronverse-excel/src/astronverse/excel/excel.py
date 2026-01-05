import ast
import time
from itertools import zip_longest

import win32clipboard as cv
from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.excel import *
from astronverse.excel.core_win.application import Application
from astronverse.excel.core_win.range import Range
from astronverse.excel.core_win.worksheet import Worksheet
from astronverse.excel.excel_obj import ExcelObj
from astronverse.excel.utils import *


class Excel:
    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [".xlsx", ".xls"], "file_type": "file"},
                ),
            ),
            atomicMg.param("password", level=AtomicLevel.ADVANCED, required=False),
        ],
        outputList=[
            atomicMg.param("open_excel_obj", types="ExcelObj"),
        ],
    )
    def open_excel(
        file_path: PATH = "",
        default_application: ApplicationType = ApplicationType.DEFAULT,
        visible_flag: bool = True,
        password: str = "",
        update_links: bool = True,
    ) -> ExcelObj:
        if not os.path.exists(file_path):
            raise Exception("填写的文件路径有误，请输入正确的路径！")
        else:
            file_path = os.path.abspath(file_path)
        application = Application.init_app(
            default_application=default_application,
            visible_flag=visible_flag,
            retry=2,
            retry_delay=1,
            prefer_existing=False,
        )
        excel = Application.open_workbook(
            application=application, file_path=file_path, password=password, update_links=update_links
        )
        return excel

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[],
        outputList=[
            atomicMg.param("get_excel_obj", types="ExcelObj"),
        ],
    )
    def get_excel(file_name) -> ExcelObj:
        excel_flag, excel_pid, wps_flag, wps_pid = get_excel_processes()
        if not excel_flag and not wps_flag:
            raise Exception("未检测到wps或office打开！")

        keys = []
        if wps_flag:
            keys.append(ApplicationType.WPS)
        if excel_flag:
            keys.append(ApplicationType.EXCEL)

        res = []
        for key in keys:
            try:
                application = Application.init_app(
                    default_application=key, visible_flag=None, retry=0, retry_delay=0, prefer_existing=True
                )
                excel_obj = Application.get_existing_workbook(application, match_name=file_name)
                if excel_obj:
                    res.append(excel_obj)
            except Exception as e:
                pass

        if len(res) == 1:
            return res[0]
        elif len(res) == 2:
            raise Exception("检测到对象：{}在WPS/Office中打开,需关闭其中一个".format(file_name))
        else:
            raise Exception("不存在已打开的Excel文件:{0}".format(file_name))

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value, params={"filters": [], "file_type": "folder"}
                ),
            ),
            atomicMg.param("password", required=False, level=AtomicLevel.ADVANCED),
        ],
        outputList=[
            atomicMg.param("create_excel_obj", types="ExcelObj"),
            atomicMg.param("excel_path", types="Str"),
        ],
    )
    def create_excel(
        file_path: str = "",
        file_name: str = "",
        default_application: ApplicationType = ApplicationType.EXCEL,
        visible_flag: bool = True,
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        password: str = "",
    ) -> tuple[ExcelObj, str]:
        if not os.path.exists(file_path):
            raise Exception("填写的文件路径有误，请输入正确的路径！")
        else:
            file_path = os.path.abspath(file_path)
        if file_name:
            file_name += ".xlsx"
        else:
            file_name = "新建Excel文档.xlsx"

        new_file_path = os.path.join(file_path, file_name)
        new_file_path = resolve_file_path(new_file_path, exist_handle_type)

        application = Application.init_app(
            default_application=default_application,
            visible_flag=visible_flag,
            retry=2,
            retry_delay=1,
            prefer_existing=True,
        )
        excel = Application.create_workbook(application=application, file_path=new_file_path, password=password)
        return excel, new_file_path

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
                required=False,
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value, params={"filters": [], "file_type": "folder"}
                ),
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "exist_handle_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression="return $this.save_type.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def save_excel(
        excel: ExcelObj,
        save_type: SaveType = SaveType.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        close_flag: bool = False,
    ):
        if save_type == SaveType.SAVE_AS and file_path:
            file_suffix = "." + excel.get_name().split(".")[-1]
            if not file_name:
                file_name = excel.get_name().split(".")[0]
            dst_file = os.path.join(file_path, file_name + file_suffix)
            new_file_path = resolve_file_path(dst_file, exist_handle_type)
            Application.save_workbook(excel_obj=excel, file_path=new_file_path)
        elif save_type == SaveType.SAVE:
            Application.save_workbook(excel_obj=excel)
        else:
            # 不做任何处理 SaveType.SAVE_AS 没有 file_path 或者是 SaveType.ABORT
            pass
        if close_flag:
            Application.close_workbook(excel_obj=excel, save_changes=False)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "excel",
                dynamics=[
                    DynamicsItem(
                        key="$this.excel.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
                    )
                ],
            ),
            atomicMg.param(
                "pkill_flag",
                dynamics=[
                    DynamicsItem(
                        key="$this.pkill_flag.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ALL.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_type_one",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_type_one.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
                    )
                ],
            ),
            atomicMg.param(
                "save_type_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.save_type_all.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ALL.value),
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value, params={"filters": [], "file_type": "folder"}
                ),
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.save_type_one.value == '{}' && $this.close_range_flag.value == '{}'".format(
                            SaveType.SAVE_AS.value, CloseRangeType.ONE.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "file_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.save_type_one.value == '{}'".format(SaveType.SAVE_AS.value),
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression="return $this.close_range_flag.value == '{}'".format(CloseRangeType.ONE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def close_excel(
        close_range_flag: CloseRangeType = CloseRangeType.ONE,
        excel: ExcelObj = None,
        save_type_one: SaveType = SaveType.SAVE,
        save_type_all: SaveType_ALL = SaveType_ALL.SAVE,
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
        pkill_flag: bool = False,
    ):
        if close_range_flag == CloseRangeType.ALL:
            save_changes = False
            if save_type_all == SaveType_ALL.SAVE:
                save_changes = True

            excel_flag, excel_pid, wps_flag, wps_pid = get_excel_processes()
            if wps_flag:
                Application.quit_app(default_application=ApplicationType.WPS, save_changes=save_changes)
            if excel_flag:
                Application.quit_app(default_application=ApplicationType.EXCEL, save_changes=save_changes)
            if pkill_flag:
                if excel_pid:
                    psutil.Process(excel_pid).kill()
                if wps_pid:
                    psutil.Process(wps_pid).kill()
        else:
            if not excel:
                raise Exception("文档不存在，请先打开文档！")
            Excel.save_excel(
                excel=excel,
                save_type=save_type_one,
                file_path=file_path,
                file_name=file_name,
                exist_handle_type=exist_handle_type,
                close_flag=True,
            )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("start_row", required=False),
            atomicMg.param("start_col", required=False),
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "edit_type",
                dynamics=[
                    DynamicsItem(
                        key="$this.edit_type.show",
                        expression="return $this.edit_range.value == '{}' || $this.edit_range.value == '{}'".format(
                            ReadRangeType.ROW.value, ReadRangeType.COLUMN.value
                        ),
                    )
                ],
                required=False,
            ),
        ],
        outputList=[],
    )
    def edit_excel(
        excel: ExcelObj,
        edit_range: EditRangeType = EditRangeType.ROW,
        sheet_name: str = "",
        start_col: str = "A",
        start_row: str = "1",
        value: str = "",
        edit_type: EditType = EditType.OVERWRITE,
    ):
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            try:
                value = ast.literal_eval(value)
            except Exception as e:
                raise Exception("填写的列表格式有误")

        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, end_row, end_col, _ = used_range

        start_col_num = handle_column_input(start_col, end_col)
        start_row_num = handle_row_input(start_row, end_row)

        if edit_range == EditRangeType.ROW:
            if not isinstance(value, list):
                raise Exception("填写内容的列表格式有误")
            first_col = end_col + 1 if edit_type == EditType.APPEND else start_col_num
            for offset, val in enumerate(value):
                r_obj = Worksheet.get_cell(worksheet, start_row_num, first_col + offset)
                Range.set_range_data(r_obj, val)
        elif edit_range == EditRangeType.COLUMN:
            if not isinstance(value, list):
                raise Exception("填写内容的列表格式有误")
            first_row = end_row + 1 if edit_type == EditType.APPEND else start_row_num
            for offset, val in enumerate(value):
                r_obj = Worksheet.get_cell(worksheet, first_row + offset, start_col_num)
                Range.set_range_data(r_obj, val)
        elif edit_range == EditRangeType.AREA:
            if not isinstance(value, list):
                raise Exception("填写内容的列表格式有误")
            if not isinstance(value[0], list):
                raise Exception("填写内容的列表格式有误")
            first_col = end_col + 1 if edit_type == EditType.APPEND else start_col_num
            first_row = end_row + 1 if edit_type == EditType.APPEND else start_row_num
            for row in value:
                for offset, val in enumerate(row):
                    r_obj = Worksheet.get_cell(worksheet, first_row, first_col + offset)
                    Range.set_range_data(r_obj, val)
                first_row += 1  # 写完一行，整体下移
        elif edit_range == EditRangeType.CELL:
            r_obj = Worksheet.get_cell(worksheet, start_row_num, start_col_num)
            Range.set_range_data(r_obj, value)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "column",
                dynamics=[
                    DynamicsItem(
                        key="$this.column.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return $this.read_range.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("read_excel_contents", types="Any"),
        ],
    )
    def read_excel(
        excel: ExcelObj,
        sheet_name: str = "",
        read_range: ReadRangeType = ReadRangeType.CELL,
        start_col: str = "",
        end_col: str = "",
        cell: str = "",
        row: str = 1,
        column: str = "",
        start_row: str = 1,
        end_row: str = 1,
        read_display: bool = True,
        trim_spaces: bool = False,
        replace_none: bool = True,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, _ = used_range

        if read_range == ReadRangeType.CELL:
            r_obj = Worksheet.get_range(worksheet, cell)
            content = Range.get_range_data(r_obj, use_text=True if read_display else False)
        elif read_range == ReadRangeType.ROW:
            start_row_num = handle_row_input(row, r_end_row)
            content = []
            for col in range(1, r_end_col + 1):
                r_obj = Worksheet.get_cell(worksheet, start_row_num, col)
                cell_text = Range.get_range_data(r_obj, use_text=True if read_display else False)
                content.append(cell_text)
        elif read_range == ReadRangeType.COLUMN:
            start_col_num = handle_column_input(column, r_end_col)
            content = []
            for row in range(1, r_end_row + 1):
                r_obj = Worksheet.get_cell(worksheet, row, start_col_num)
                cell_text = Range.get_range_data(r_obj, use_text=True if read_display else False)
                content.append(cell_text)
        elif read_range == ReadRangeType.AREA:
            start_col_num = handle_column_input(start_col, r_end_col)
            end_col_num = handle_column_input(end_col, r_end_col)
            start_row_num = handle_row_input(start_row, r_end_row)
            end_row_num = handle_row_input(end_row, r_end_row)
            content = []
            for row in range(start_row_num, end_row_num + 1):
                row_data = []
                for col in range(start_col_num, end_col_num + 1):
                    r_obj = Worksheet.get_cell(worksheet, row, col)
                    cell_text = Range.get_range_data(r_obj, use_text=True if read_display else False)
                    row_data.append(cell_text)
                content.append(row_data)
        elif read_range == ReadRangeType.ALL:
            content = []
            for row in range(1, r_end_row + 1):
                row_data = []
                for col in range(1, r_end_col + 1):
                    r_obj = Worksheet.get_cell(worksheet, row, col)
                    cell_text = Range.get_range_data(r_obj, use_text=True if read_display else False)
                    row_data.append(cell_text)
                content.append(row_data)
        else:
            raise NotImplementedError()

        if trim_spaces:
            content = util_trim(content)
        if replace_none:
            content = util_replace_node(content)
        return content

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_position.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param("col_width", required=False),
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "bg_color", required=False, formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value)
            ),
            atomicMg.param(
                "font_color",
                required=False,
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_VARIABLE_COLOR.value),
            ),
            atomicMg.param("font_size", required=False),
            atomicMg.param(
                "numberformat_other",
                dynamics=[
                    DynamicsItem(
                        key="$this.numberformat_other.show",
                        expression="return $this.numberformat.value == '{}'".format(NumberFormatType.CUSTOM.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param(
                "auto_row_height",
                dynamics=[
                    DynamicsItem(
                        key="$this.auto_row_height.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "auto_column_width",
                dynamics=[
                    DynamicsItem(
                        key="$this.auto_column_width.show",
                        expression="return $this.design_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def design_cell_type(
        excel: ExcelObj,
        sheet_name: str = "",
        design_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        range_position: str = "",
        col: str = "",
        row: str = "",
        col_width: str = "",
        bg_color: str = "",
        font_color: str = "",
        font_type: FontType = FontType.NO_CHANGE,
        font_name: FontNameType = FontNameType.NO_CHANGE,
        font_size: int = 11,
        numberformat: NumberFormatType = NumberFormatType.NO_CHANGE,
        numberformat_other: str = "",
        horizontal_align: HorizontalAlign = HorizontalAlign.NO_CHANGE,
        vertical_align: VerticalAlign = VerticalAlign.NO_CHANGE,
        wrap_text: bool = True,
        auto_row_height: bool = False,
        auto_column_width: bool = False,
    ):
        if bg_color:
            bg_color = check_color(bg_color)
        if font_color:
            font_color = check_color(font_color)

        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        cell_positions = calculate_cell_positions(
            design_type=design_type.value,
            cell_position=cell_position,
            range_position=range_position,
            col=col,
            row=row,
            r_end_row=r_end_row,
            r_end_col=r_end_col,
            r_address=r_address,
        )

        for cell_position in cell_positions:
            r_obj = Worksheet.get_range(worksheet, cell_position)
            Range.set_range_type(
                range_obj=r_obj,
                col_width=col_width,
                bg_color=bg_color,
                font_color=font_color,
                font_type=font_type,
                font_name=font_name,
                font_size=font_size,
                number_format=numberformat,
                number_format_other=numberformat_other,
                horizontal_align=horizontal_align,
                vertical_align=vertical_align,
                wrap_text=wrap_text,
                design_type=design_type,
                auto_row_height=auto_row_height,
                auto_column_width=auto_column_width,
            )

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_position.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.copy_range_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("copy_excel_contents", types="Str"),
        ],
    )
    def copy_excel(
        excel: ExcelObj,
        sheet_name: str = "",
        copy_range_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "A1",
        row: str = "",
        col: str = "",
        range_position: str = "A1:B5",
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        cell_positions = calculate_cell_positions(
            design_type=copy_range_type.value,
            cell_position=cell_position,
            range_position=range_position,
            col=col,
            row=row,
            r_end_row=r_end_row,
            r_end_col=r_end_col,
            r_address=r_address,
        )
        if len(cell_positions) > 0:
            cell = cell_positions[0]
        else:
            return ""

        r_obj = Worksheet.get_range(worksheet, cell)
        Range.copy_range(r_obj)
        try:
            cv.OpenClipboard()
            return cv.GetClipboardData(cv.CF_UNICODETEXT)
        finally:
            try:
                cv.CloseClipboard()
            except Exception as e:
                pass

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[],
    )
    def paste_excel(
        excel: ExcelObj,
        sheet_name: str = "",
        paste_type: PasteType = PasteType.ALL,
        start_location: str = "A1",
        skip_blanks: bool = False,
        transpose: bool = False,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        r_obj = Worksheet.get_range(worksheet, start_location)
        Range.paste_range(r_obj, paste_type=paste_type.value, skip_blanks=skip_blanks, transpose=transpose)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "coordinate",
                dynamics=[
                    DynamicsItem(
                        key="$this.coordinate.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "data_region",
                dynamics=[
                    DynamicsItem(
                        key="$this.data_region.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.delete_range_excel.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "direction",
                dynamics=[
                    DynamicsItem(
                        key="$this.direction.show",
                        expression="return ['{}', '{}'].includes($this.delete_range_excel.value)".format(
                            ReadRangeType.CELL.value, ReadRangeType.AREA.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def delete_excel_cell(
        excel: ExcelObj,
        sheet_name: str = "",
        delete_range_excel: ReadRangeType = ReadRangeType.CELL,
        coordinate: str = "",
        row: str = "",
        col: str = "",
        data_region: str = "",
        direction: DeleteCellDirection = DeleteCellDirection.LOWER_MOVE_UP,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range
        cell_positions = calculate_cell_positions(
            design_type=delete_range_excel.value,
            cell_position=coordinate,
            range_position=data_region,
            col=col,
            row=row,
            r_end_row=r_end_row,
            r_end_col=r_end_col,
            r_address=r_address,
        )
        for cell_position in cell_positions:
            r_obj = Worksheet.get_range(worksheet, cell_position)
            if delete_range_excel in [ReadRangeType.CELL, ReadRangeType.AREA]:
                Range.delete_range(r_obj, direction=direction.value)
            else:
                Range.delete_range(r_obj)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_location",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_location.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "data_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.data_range.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def clear_excel_content(
        excel: ExcelObj,
        sheet_name: str,
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_location: str = "",
        row: str = "",
        col: str = "",
        data_range: str = "A1:B5",
        clear_type: ClearType = ClearType.CONTENT,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range
        cell_positions = calculate_cell_positions(
            design_type=select_type.value,
            cell_position=cell_location,
            range_position=data_range,
            col=col,
            row=row,
            r_end_row=r_end_row,
            r_end_col=r_end_col,
            r_address=r_address,
        )
        for cell_position in cell_positions:
            r_obj = Worksheet.get_range(worksheet, cell_position)
            Range.clear_range(r_obj, clear_type.value)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "row_direction",
                dynamics=[
                    DynamicsItem(
                        key="$this.row_direction.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "col_direction",
                dynamics=[
                    DynamicsItem(
                        key="$this.col_direction.show",
                        expression="return $this.insert_type.value == '{}'".format(EnhancedInsertType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "insert_num",
                dynamics=[
                    DynamicsItem(key="$this.insert_num.show", expression="return $this.blank_rows.value == true")
                ],
            ),
            atomicMg.param(
                "insert_content",
                dynamics=[
                    DynamicsItem(key="$this.insert_content.show", expression="return $this.blank_rows.value == false")
                ],
            ),
        ],
        outputList=[],
    )
    def insert_excel_row_or_column(
        excel: ExcelObj,
        sheet_name: str = "",
        insert_type: EnhancedInsertType = EnhancedInsertType.ROW,
        row: str = 1,
        row_direction: RowDirectionType = RowDirectionType.LOWER,
        col: str = 1,
        col_direction: ColumnDirectionType = ColumnDirectionType.RIGHT,
        blank_rows: bool = False,
        insert_num: int = 1,
        insert_content: str = "",
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        r_end_col_letter = column_number_to_letter(r_end_col)

        value = insert_content
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            try:
                value = ast.literal_eval(value)
            except Exception as e:
                raise Exception("填写的列表格式有误")

        if not blank_rows:
            if not isinstance(value, list):
                raise Exception("插入内容填写的列表格式有误")
            if not isinstance(value[0], list):
                raise Exception("填写内容的列表格式有误")
            insert_num = len(value)

        if insert_type == EnhancedInsertType.ADD_ROWS:
            row_direction = RowDirectionType.LOWER
            row = r_end_row
        elif insert_type == EnhancedInsertType.ADD_COLUMNS:
            col_direction = ColumnDirectionType.RIGHT
            col = r_end_col

        if insert_type in [EnhancedInsertType.ROW, EnhancedInsertType.ADD_ROWS]:
            start_row_num = handle_row_input(row, r_end_row)
            if row_direction == RowDirectionType.UPPER:  # 向上
                for _ in range(insert_num):
                    r_obj = Worksheet.get_range(
                        worksheet, "A{}:{}{}".format(start_row_num, r_end_col_letter, start_row_num)
                    )
                    Range.insert_range(r_obj, "row")
            elif row_direction == RowDirectionType.LOWER:  # 向下
                for _ in range(insert_num):
                    r_obj = Worksheet.get_range(
                        worksheet, "A{}:{}{}".format(start_row_num + 1, r_end_col_letter, start_row_num + 1)
                    )
                    Range.insert_range(r_obj, "row")
                start_row_num = start_row_num + 1

            if not blank_rows:
                # 插入内容
                first_col = 1
                first_row = start_row_num
                for row in value:
                    for offset, val in enumerate(row):
                        r_obj = Worksheet.get_cell(worksheet, first_row, first_col + offset)
                        Range.set_range_data(r_obj, val)
                    first_row += 1  # 写完一行，整体下移
        elif insert_type in [EnhancedInsertType.COLUMN, EnhancedInsertType.ADD_COLUMNS]:
            start_col_num = handle_column_input(str(col), r_end_col)
            if col_direction == ColumnDirectionType.LEFT:  # 向上
                for _ in range(insert_num):
                    r_obj = Worksheet.get_range(
                        worksheet,
                        "{}1:{}{}".format(
                            column_number_to_letter(start_col_num), column_number_to_letter(start_col_num), r_end_row
                        ),
                    )
                    Range.insert_range(r_obj, "column")
            elif col_direction == ColumnDirectionType.RIGHT:  # 向下
                for _ in range(insert_num):
                    r_obj = Worksheet.get_range(
                        worksheet,
                        "{}1:{}{}".format(
                            column_number_to_letter(start_col_num + 1),
                            column_number_to_letter(start_col_num + 1),
                            r_end_row,
                        ),
                    )
                    Range.insert_range(r_obj, "column")
                start_col_num = start_col_num + 1
            if not blank_rows:
                filled_T = list(zip_longest(*value, fillvalue=""))
                value = [list(t_row) for t_row in filled_T]
                # 插入内容
                first_col = start_col_num
                first_row = 1
                for row in value:
                    for offset, val in enumerate(row):
                        r_obj = Worksheet.get_cell(worksheet, first_row, first_col + offset)
                        Range.set_range_data(r_obj, val)
                    first_row += 1  # 写完一行，整体下移

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.get_col_type.value == '{}'".format(ColumnType.ONE_COLUMN.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("excel_row_num", types="Int"),
        ],
    )
    def get_excel_row_num(
        excel: ExcelObj, sheet_name: str = "", get_col_type: ColumnType = ColumnType.ALL, col: str = ""
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        if get_col_type == ColumnType.ALL:
            return r_end_row
        elif get_col_type == ColumnType.ONE_COLUMN:
            start_col_num = handle_column_input(col, r_end_col)
            for row in range(r_end_row, 0, -1):  # 倒序
                val = Range.get_range_data(Worksheet.get_cell(worksheet, row, start_col_num), False)
                if val not in [None, ""]:
                    return row  # Excel 行号 = row
            return 0  # 全空

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.get_row_type.value == '{}'".format(RowType.ONE_ROW.value),
                    )
                ],
            ),
        ],
        outputList=[
            atomicMg.param("excel_col_num", types="Int"),
        ],
    )
    def get_excel_col_num(
        excel: ExcelObj,
        sheet_name: str = "",
        get_row_type: RowType = RowType.ALL,
        row: str = "",
        output_type: ColumnOutputType = ColumnOutputType.NUMBER,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        r_start_row, r_start_col, r_end_row, r_end_col, r_address = used_range

        if get_row_type == RowType.ALL:
            return column_number_to_letter(r_end_col) if output_type == ColumnOutputType.LETTER else r_end_col
        elif get_row_type == RowType.ONE_ROW:
            start_row_num = handle_row_input(row, r_end_row)

            for col in range(r_end_col, 0, -1):  # 从最后一列向前查
                val = Range.get_range_data(Worksheet.get_cell(worksheet, start_row_num, col), False)
                if val not in [None, ""]:
                    return column_number_to_letter(col) if output_type == ColumnOutputType.LETTER else col
            return "" if output_type == ColumnOutputType.LETTER else 0

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("get_first_available_row", types="Int"),
        ],
    )
    def get_excel_first_available_row(excel: ExcelObj, sheet_name: str = ""):
        """
        获取第一个空行的行号

        Args:
            excel: ExcelObj 对象
            sheet_name: 工作表名称，默认为空（第一个工作表）

        Returns:
            第一个空行的行号（1-based），如果都不为空，返回最后一行+1
        """
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
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

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("get_first_available_col", types="Any"),
        ],
    )
    def get_excel_first_available_col(
        excel: ExcelObj, sheet_name: str = "", output_type: ColumnOutputType = ColumnOutputType.LETTER
    ):
        """
        获取第一个空列的列号或字母

        Args:
            excel: ExcelObj 对象
            sheet_name: 工作表名称，默认为空（第一个工作表）
            output_type: 返回类型，LETTER（字母）或 NUMBER（数字）

        Returns:
            第一个空列的列号或字母（1-based）。如果都不为空，返回最后一列+1
        """
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        r_start_row, r_start_col, r_end_row, r_end_col, r_address = used_range

        for col in range(r_start_col, r_end_col + 1):
            for row in range(r_start_row, r_end_row + 1):
                val = Range.get_range_data(Worksheet.get_cell(worksheet, row, col), False)
                if val not in (None, ""):
                    break
            else:
                return column_number_to_letter(col) if output_type == ColumnOutputType.LETTER else col
        return column_number_to_letter(r_end_col + 1) if output_type == ColumnOutputType.LETTER else r_end_col + 1

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.ROW.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.ROW.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.COLUMN.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return ['{}', '{}'].includes($this.select_type.value)".format(
                            SearchRangeType.COLUMN.value, SearchRangeType.AREA.value
                        ),
                    )
                ],
            ),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("key", types="Str"),
            atomicMg.param("value", types="Any"),
        ],
    )
    def loop_excel_content(
        excel: ExcelObj,
        sheet_name: str = "",
        select_type: SearchRangeType = SearchRangeType.ROW,
        start_row: str = "1",
        end_row: str = "-1",
        start_col: str = "A",
        end_col: str = "-1",
        real_text: bool = False,
        cell_strip: bool = False,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        r_end_col_letter = column_number_to_letter(r_end_col)

        start_col_num = handle_column_input(start_col, r_end_col)
        end_col_num = handle_column_input(end_col, r_end_col)
        start_row_num = handle_row_input(start_row, r_end_row)
        end_row_num = handle_row_input(end_row, r_end_row)

        if select_type == SearchRangeType.ROW:
            data_region = "{}{}:{}{}".format("A", start_row_num, r_end_col_letter, end_row_num)
        elif select_type == SearchRangeType.COLUMN:
            data_region = "{}{}:{}{}".format(
                column_number_to_letter(start_col_num), "1", column_number_to_letter(end_col_num), end_row_num
            )
        elif select_type == SearchRangeType.AREA:
            data_region = "{}{}:{}{}".format(
                column_number_to_letter(start_col_num), start_row_num, column_number_to_letter(end_col_num), end_row_num
            )
        elif select_type == SearchRangeType.ALL:
            data_region = "{}{}:{}{}".format("A", "1", r_end_col_letter, r_end_row)
        else:
            raise ValueError("不支持的操作类型：{}".format(select_type))

        content = Range.get_range_data(Worksheet.get_range(worksheet, data_region), True if real_text else False)
        if content:
            if cell_strip:
                content = util_trim(content)

            if content:
                if not isinstance(content, (list, tuple)):
                    content = ((content,),)
                if select_type == SearchRangeType.COLUMN:
                    keys = (column_number_to_letter(n) for n in range(start_col_num, end_col_num + 1))
                    vals = (list(col) for col in zip(*content))
                else:
                    keys = range(start_row_num, start_row_num + len(content))
                    vals = (list(row) for row in content)
                content = dict(zip(keys, vals))
        else:
            content = {}

        def table_generator():
            for i, v in content.items():
                yield i, v

        return table_generator()

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[
            atomicMg.param("get_cell_color", types="Str"),
        ],
    )
    def excel_get_cell_color(excel: ExcelObj, coordinate: str, sheet_name: str = ""):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        range_obj = Worksheet.get_range(worksheet, coordinate)
        r, g, b = Range.get_range_color(range_obj)
        color_str = "{},{},{}".format(r, g, b)
        return color_str

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "merge_cell_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.merge_cell_range.show",
                        expression="return $this.job_type.value == '{}'".format(MergeOrSplitType.MERGE.value),
                    )
                ],
            ),
            atomicMg.param(
                "split_cell_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.split_cell_range.show",
                        expression="return $this.job_type.value == '{}'".format(MergeOrSplitType.SPLIT.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def merge_split_excel_cell(
        excel: ExcelObj,
        sheet_name: str,
        job_type: MergeOrSplitType = MergeOrSplitType.MERGE,
        merge_cell_range: str = "A1:B2",
        split_cell_range: str = "A1:B2",
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        if job_type == MergeOrSplitType.MERGE:
            range_obj = Worksheet.get_range(worksheet, merge_cell_range)
        else:
            range_obj = Worksheet.get_range(worksheet, split_cell_range)
        Range.merge_range(range_obj, job_type.value)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "relative_sheet_name",
                dynamics=[
                    DynamicsItem(
                        key="$this.relative_sheet_name.show",
                        expression="return $this.insert_type.value == '{}' || $this.insert_type.value == '{}'".format(
                            SheetInsertType.BEFORE.value, SheetInsertType.AFTER.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def add_excel_worksheet(
        excel: ExcelObj,
        sheet_name: str,
        insert_type: SheetInsertType = SheetInsertType.FIRST,
        relative_sheet_name: str = "",
    ):
        """
        创建工作表

        Args:
            excel: ExcelObj 对象
            sheet_name: 工作表名称
            insert_type: 插入位置类型
            relative_sheet_name: 参考工作表名称（当 insert_type 为 BEFORE 或 AFTER 时使用）
        """
        sheet_names = Worksheet.get_all_worksheet_names(excel)
        if sheet_name in sheet_names:
            raise ValueError("新sheet名称已存在")
        if len(sheet_name) >= 31:
            raise ValueError("sheet名称过长,需要小于31个字符")

        if insert_type == SheetInsertType.FIRST:
            Worksheet.add_worksheet(excel, sheet_name, before=1)
        elif insert_type == SheetInsertType.LAST:
            Worksheet.add_worksheet(excel, sheet_name)
        else:
            if (not relative_sheet_name) or (relative_sheet_name not in sheet_names):
                raise ValueError("参考sheet名称不存在")
            if insert_type == SheetInsertType.BEFORE:
                Worksheet.add_worksheet(excel, sheet_name, before=relative_sheet_name)
            elif insert_type == SheetInsertType.AFTER:
                Worksheet.add_worksheet(excel, sheet_name, after=relative_sheet_name)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "move_to_sheet",
                dynamics=[
                    DynamicsItem(
                        key="$this.move_to_sheet.show",
                        expression="return ['{}', '{}'].includes($this.move_type.value)".format(
                            MoveSheetType.MOVE_AFTER.value, MoveSheetType.MOVE_BEFORE.value
                        ),
                    )
                ],
            )
        ],
        outputList=[],
    )
    def move_excel_worksheet(
        excel: ExcelObj,
        move_type: MoveSheetType = MoveSheetType.MOVE_AFTER,
        move_sheet: str = "",
        move_to_sheet: str = "",
    ):
        """
        移动工作表

        Args:
            excel: ExcelObj 对象
            move_type: 移动类型
            move_sheet: 要移动的工作表名称
            move_to_sheet: 目标工作表名称（当 move_type 为 MOVE_AFTER 或 MOVE_BEFORE 时使用）
        """
        sheet_names = Worksheet.get_all_worksheet_names(excel)
        move_worksheet = Worksheet.get_worksheet(excel, move_sheet, default=0)

        if move_type == MoveSheetType.MOVE_TO_FIRST:
            Worksheet.move_worksheet(move_worksheet, before=1)
        elif move_type == MoveSheetType.MOVE_TO_LAST:
            Worksheet.move_worksheet(move_worksheet)
        else:
            if (not move_to_sheet) or (move_to_sheet not in sheet_names):
                raise ValueError("参考sheet名称不存在")
            if move_type == MoveSheetType.MOVE_BEFORE:
                Worksheet.move_worksheet(move_worksheet, before=move_to_sheet)
            elif move_type == MoveSheetType.MOVE_AFTER:
                Worksheet.move_worksheet(move_worksheet, after=move_to_sheet)

    @staticmethod
    @atomicMg.atomic("Excel", inputList=[], outputList=[])
    def delete_excel_worksheet(excel: ExcelObj, del_sheet_name: str):
        """
        删除工作表

        Args:
            excel: ExcelObj 对象
            del_sheet_name: 需要删除的工作表名称
        """
        worksheet = Worksheet.get_worksheet(excel, del_sheet_name)
        Worksheet.delete_worksheet(worksheet)

    @staticmethod
    @atomicMg.atomic("Excel", inputList=[], outputList=[])
    def rename_excel_worksheet(excel: ExcelObj, source_sheet_name: str, new_sheet_name: str):
        """
        重命名工作表

        Args:
            excel: ExcelObj 对象
            source_sheet_name: 源工作表名称
            new_sheet_name: 新工作表名称
        """
        try:
            sheet_names = Worksheet.get_all_worksheet_names(excel)
            if new_sheet_name in sheet_names:
                raise ValueError("新sheet名称已存在")
            if len(new_sheet_name) >= 31:
                raise ValueError("sheet名称过长,需要小于31个字符")
            worksheet = Worksheet.get_worksheet(excel, source_sheet_name)
            Worksheet.rename_worksheet(worksheet, new_sheet_name)
        except Exception as err:
            raise err

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "other_excel_obj",
                dynamics=[
                    DynamicsItem(
                        key="$this.other_excel_obj.show",
                        expression="return $this.copy_type.value == '{}'".format(CopySheetType.OTHER_WORKBOOK.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def copy_excel_worksheet(
        excel: ExcelObj,
        source_sheet_name: str,
        new_sheet_name: str,
        location: CopySheetLocationType = CopySheetLocationType.LAST,
        copy_type: CopySheetType = CopySheetType.CURRENT_WORKBOOK,
        other_excel_obj: ExcelObj = "",
        is_cover: bool = False,
    ):
        """
        复制工作表

        Args:
            excel: ExcelObj 对象
            source_sheet_name: 需复制sheet名称
            new_sheet_name: 新复制的sheet名称
            location: 位置，BEFORE, AFTER, FIRST, LAST
            copy_type: 复制类型，CURRENT_WORKBOOK 当前工作簿，OTHER_WORKBOOK 其他工作簿
            other_excel_obj: 其他工作簿对象（当copy_type为OTHER_WORKBOOK时使用）
            is_cover: 是否覆盖同名工作表
        """
        sheet_names = Worksheet.get_all_worksheet_names(excel)
        other_sheet_names = []
        if other_excel_obj:
            other_sheet_names = Worksheet.get_all_worksheet_names(other_excel_obj)

        if copy_type == CopySheetType.CURRENT_WORKBOOK:
            trigger_excel = excel
            if new_sheet_name in sheet_names and not is_cover:
                raise ValueError("复制sheet名称已存在")
        else:
            trigger_excel = other_excel_obj
            if new_sheet_name in other_sheet_names and not is_cover:
                raise ValueError("复制sheet名称已存在")

        if len(new_sheet_name) >= 31:
            raise ValueError("sheet名称过长,需要小于31个字符")

        source_worksheet = Worksheet.get_worksheet(excel, source_sheet_name)

        # 删除
        if is_cover and new_sheet_name in sheet_names:
            Worksheet.delete_worksheet(Worksheet.get_worksheet(trigger_excel, new_sheet_name))

        # 复制，并设置active
        time.sleep(0.5)
        Worksheet.copy_worksheet(
            source_worksheet,
            trigger_excel,
            location,
            is_same_workbook=True if CopySheetType.CURRENT_WORKBOOK else False,
        )

        # 重命名
        Worksheet.rename_worksheet(Worksheet.get_active_worksheet(excel), new_sheet_name)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[],
        outputList=[
            atomicMg.param("sheet_names", types="Str"),
        ],
    )
    def get_excel_worksheet_names(excel: ExcelObj, sheet_range: SheetRangeType = SheetRangeType.ACTIVATED):
        """
        获取工作表名称

        Args:
            excel: ExcelObj 对象
            sheet_range: 范围类型，ACTIVATED 返回当前激活工作表名称，ALL 返回所有工作表名称列表

        Returns:
            工作表名称或名称列表
        """
        if sheet_range == SheetRangeType.ALL:
            return Worksheet.get_all_worksheet_names(excel)
        else:
            return Worksheet.get_worksheet_name(Worksheet.get_active_worksheet(excel))

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "sheet_name",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.sheet_name.show",
                        expression="return $this.lookup_range_excel.value == '{}'".format(SearchSheetType.ONE.value),
                    )
                ],
            ),
            atomicMg.param(
                "replace_str",
                dynamics=[
                    DynamicsItem(key="$this.replace_str.show", expression="return $this.replace_flag.value == true")
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return $this.search_range.value == '{}'".format(SearchRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("search_excel_result", types="Dict")],
    )
    def search_and_replace_excel_content(
        excel: ExcelObj,
        find_str: str,
        replace_flag: bool = False,
        replace_str: str = "",
        lookup_range_excel: SearchSheetType = SearchSheetType.ALL,
        sheet_name: str = "",
        search_range: SearchRangeType = SearchRangeType.ALL,
        row: str = "",
        col: str = "",
        start_row: str = "",
        end_row: str = "",
        start_col: str = "",
        end_col: str = "",
        exact_match: bool = False,
        case_flag: bool = False,
        match_range: MatchCountType = MatchCountType.ALL,
        output_type: SearchResultType = SearchResultType.CELL,
    ):
        """
        查找和替换 Excel 中的内容

        Args:
            excel: Excel对象
            find_str: 要查找的字符串
            replace_flag: 是否替换
            replace_str: 要替换的字符串
            lookup_range_excel: 查找范围（ALL: 所有工作表, ONE: 指定工作表）
            sheet_name: 工作表名称
            search_range: 搜索范围（ALL/ROW/COLUMN/AREA）
            row: 行号（用于ROW类型）
            col: 列号（用于COLUMN类型）
            start_row: 起始行号（用于AREA类型）
            end_row: 结束行号（用于AREA类型）
            start_col: 起始列号（用于AREA类型）
            end_col: 结束列号（用于AREA类型）
            exact_match: 是否精确匹配
            case_flag: 是否区分大小写
            match_range: 匹配范围（ALL: 所有, FIRST: 仅第一个）
            output_type: 输出类型（CELL: 单元格地址, COL_AND_ROW: 列和行）

        Returns:
            dict 或 list: 搜索结果，格式根据 output_type 和 lookup_range_excel 决定
        """
        # 处理 find_str 为复数类型的情况
        if isinstance(find_str, complex):
            find_str = str(find_str)

        # 确定要搜索的工作表列表
        if lookup_range_excel == SearchSheetType.ALL:
            sheet_list = Worksheet.get_all_worksheets(excel)
            sheet_name = ""
        else:
            worksheet = Worksheet.get_worksheet(excel, sheet_name, 1)
            sheet_list = [worksheet]
            sheet_name = Worksheet.get_worksheet_name(worksheet)

        contents = {}

        def _format_search_results(results: list, output_type: SearchResultType) -> list:
            """
            格式化搜索结果

            Args:
                results: 搜索结果列表，每个元素包含 {"row": 行号, "col": 列字母}
                output_type: 输出类型

            Returns:
                list: 格式化后的结果列表
            """
            formatted = []
            for result in results:
                if output_type == SearchResultType.CELL:
                    # 返回单元格地址，如 "A1"
                    formatted.append(result["col"] + result["row"])
                elif output_type == SearchResultType.COL_AND_ROW:
                    # 返回 [列字母, 行号]
                    formatted.append([result["col"], result["row"]])
            return formatted

        # 遍历每个工作表
        for worksheet in sheet_list:
            name = Worksheet.get_worksheet_name(worksheet)
            used_range = Worksheet.get_worksheet_used_range(worksheet)
            _, _, r_end_row, r_end_col, r_address = used_range

            # 对于 AREA 类型，需要特殊处理
            if search_range == SearchRangeType.AREA:
                # 处理区域范围
                start_row_num = handle_row_input(start_row, r_end_row)
                end_row_num = handle_row_input(end_row, r_end_row)
                start_col_num = handle_column_input(start_col, r_end_col)
                end_col_num = handle_column_input(end_col, r_end_col)
                start_col_letter = column_number_to_letter(start_col_num)
                end_col_letter = column_number_to_letter(end_col_num)
                cell_positions = [f"{start_col_letter}{start_row_num}:{end_col_letter}{end_row_num}"]
            else:
                # 根据 search_range 计算单元格位置
                cell_positions = calculate_cell_positions(
                    design_type=search_range.value,
                    cell_position="",
                    range_position="",
                    col=col,
                    row=row,
                    r_end_row=r_end_row,
                    r_end_col=r_end_col,
                    r_address=r_address,
                    support_comma=True,
                    support_colon=True,
                )

            # 在每个范围内搜索
            all_results = []
            for cell_pos in cell_positions:
                range_obj = Worksheet.get_range(worksheet, cell_pos)
                results = Range.search_and_replace(
                    range_obj,
                    find_str,
                    replace_str if replace_flag else "",
                    exact_match,
                    case_flag,
                    match_range == MatchCountType.ALL,
                )
                all_results.extend(results)

            # 格式化结果
            formatted_results = _format_search_results(all_results, output_type)
            contents[name] = formatted_results

        # 根据 lookup_range_excel 返回结果
        if lookup_range_excel == SearchSheetType.ONE:
            return contents.get(sheet_name, [])
        else:
            return contents

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "pic_height",
                dynamics=[
                    DynamicsItem(
                        key="$this.pic_height.show",
                        expression="return $this.pic_size_type.value == '{}'".format(ImageSizeType.NUMBER.value),
                    )
                ],
            ),
            atomicMg.param(
                "pic_width",
                dynamics=[
                    DynamicsItem(
                        key="$this.pic_width.show",
                        expression="return $this.pic_size_type.value == '{}'".format(ImageSizeType.NUMBER.value),
                    )
                ],
            ),
            atomicMg.param(
                "pic_scale",
                dynamics=[
                    DynamicsItem(
                        key="$this.pic_scale.show",
                        expression="return $this.pic_size_type.value == '{}'".format(ImageSizeType.SCALE.value),
                    )
                ],
            ),
            atomicMg.param(
                "pic_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value, params={"filters": [], "file_type": "file"}
                ),
            ),
        ],
        outputList=[],
    )
    def insert_pic(
        excel: ExcelObj,
        sheet_name: str,
        insert_pos: str,
        pic_path: str,
        pic_size_type: ImageSizeType = ImageSizeType.AUTO,
        pic_height: int = 300,
        pic_width: int = 400,
        pic_scale: float = 1.0,
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        r_obj = Worksheet.get_range(worksheet, insert_pos)

        left, top, width, height = Range.get_range_size(r_obj)
        scale = 1.0
        if pic_size_type == ImageSizeType.SCALE:
            scale = pic_scale
        elif pic_size_type == ImageSizeType.NUMBER:
            width = pic_width
            height = pic_height
        elif pic_size_type == ImageSizeType.AUTO:
            width = width
            height = height
        Worksheet.insert_picture(worksheet, pic_path, left, top, height, width, scale)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "start_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_row.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_row",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_row.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.DOWN.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "start_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.start_col.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "end_col",
                dynamics=[
                    DynamicsItem(
                        key="$this.end_col.show",
                        expression="return $this.insert_direction.value == '{}'".format(
                            InsertFormulaDirectionType.RIGHT.value
                        ),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def insert_formula(
        excel: ExcelObj,
        sheet_name: str = "",
        insert_direction: InsertFormulaDirectionType = InsertFormulaDirectionType.DOWN,
        col: str = "",
        start_row: str = "1",
        end_row: str = "-1",
        row: str = "",
        start_col: str = "A",
        end_col: str = "-1",
        formula: str = "",
    ):
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, _ = used_range

        if insert_direction == InsertFormulaDirectionType.DOWN:
            col_num = handle_column_input(col, r_end_col)
            col_letter = column_number_to_letter(col_num)
            start_row_num = handle_row_input(start_row, r_end_row)
            end_row_num = handle_row_input(end_row, r_end_row)

            starter = Worksheet.get_range(worksheet, "{}{}".format(col_letter, str(start_row_num)))
            Range.set_range_data(starter, formula)
            target_range = Worksheet.get_range(
                worksheet, "{}{}:{}{}".format(col_letter, str(start_row_num), col_letter, str(end_row_num))
            )
            Range.autofill_range(starter, target_range)

        if insert_direction == InsertFormulaDirectionType.RIGHT:
            start_col_num = handle_column_input(start_col, r_end_col)
            end_col_num = handle_column_input(end_col, r_end_col)
            start_col_letter = column_number_to_letter(start_col_num)
            end_col_letter = column_number_to_letter(end_col_num)
            row_num = handle_row_input(row, r_end_row)

            starter = Worksheet.get_range(worksheet, "{}{}".format(start_col_letter, str(row_num)))
            Range.set_range_data(starter, formula)
            target_range = Worksheet.get_range(
                worksheet, "{}{}:{}{}".format(start_col_letter, str(row_num), end_col_letter, str(row_num))
            )
            Range.autofill_range(starter, target_range)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.POSITION.value),
                    )
                ],
            ),
            atomicMg.param(
                "find_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.find_str.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "sheet_name",
                required=False,
                dynamics=[
                    DynamicsItem(
                        key="$this.sheet_name.show",
                        expression="return $this.comment_range.value == '{}' || $this.comment_type.value == '{}'".format(
                            SearchSheetType.ONE.value, CreateCommentType.POSITION.value
                        ),
                    )
                ],
            ),
            atomicMg.param(
                "comment_range",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_range.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.CONTENT.value),
                    )
                ],
            ),
            atomicMg.param(
                "comment_all",
                dynamics=[
                    DynamicsItem(
                        key="$this.comment_all.show",
                        expression="return $this.comment_type.value == '{}'".format(CreateCommentType.CONTENT.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def create_excel_comment(
        excel: ExcelObj,
        comment_type: CreateCommentType = CreateCommentType.POSITION,
        comment: str = "",
        sheet_name: str = "",
        cell_position: str = "",
        comment_range: SearchSheetType = SearchSheetType.ONE,
        find_str: str = "",
        comment_all: bool = False,
    ):
        """
        创建 Excel 批注

        Args:
            excel: Excel对象
            comment_type: 批注类型（POSITION: 指定位置, CONTENT: 指定内容）
            comment: 批注内容
            sheet_name: 工作表名称
            cell_position: 单元格位置（用于 POSITION 类型）
            comment_range: 批注范围（ONE: 指定工作表, ALL: 所有工作表）
            find_str: 待查找的内容（用于 CONTENT 类型）
            comment_all: 是否批注所有匹配的内容（用于 CONTENT 类型）
        """
        if comment_type == CreateCommentType.POSITION:
            # 指定位置批注
            worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)
            range_obj = Worksheet.get_range(worksheet, cell_position)
            Range.add_comment(range_obj, comment)
        elif comment_type == CreateCommentType.CONTENT:
            # 指定内容批注
            count = 0

            # 确定要搜索的工作表列表
            if comment_range == SearchSheetType.ALL:
                sheet_list = Worksheet.get_all_worksheets(excel)
            else:
                sheet_list = [Worksheet.get_worksheet(excel, sheet_name, 1)]

            # 遍历工作表搜索并添加批注
            for worksheet in sheet_list:
                used_range = Worksheet.get_worksheet_used_range(worksheet)
                _, _, r_end_row, r_end_col, _ = used_range

                # 遍历所有单元格查找匹配的内容
                for row in range(1, r_end_row + 1):
                    for col in range(1, r_end_col + 1):
                        cell = Worksheet.get_cell(worksheet, row, col)
                        cell_value = Range.get_range_data(cell, use_text=True)

                        # 检查是否匹配查找内容
                        if cell_value and find_str in str(cell_value):
                            Range.add_comment(cell, comment)
                            count += 1

                            # 如果只批注第一个匹配项，则退出所有循环
                            if count == 1 and not comment_all:
                                return

                    # 如果只批注第一个匹配项且已找到，则退出行循环
                    if count == 1 and not comment_all:
                        break

                # 如果只批注第一个匹配项且已找到，则退出工作表循环
                if count == 1 and not comment_all:
                    break

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(key="$this.cell_position.show", expression="return $this.delete_all.value == false")
                ],
            ),
            atomicMg.param("sheet_name", required=False),
        ],
        outputList=[],
    )
    def delete_excel_comment(
        excel: ExcelObj,
        delete_all: bool = False,
        sheet_name: str = "",
        cell_position: str = "",
    ):
        """
        删除 Excel 批注

        Args:
            excel: Excel对象
            delete_all: 是否删除所有批注
            sheet_name: 工作表名称
            cell_position: 单元格位置（当 delete_all=False 时使用）

        Raises:
            ValueError: 当不存在批注时抛出异常
        """
        worksheet = Worksheet.get_worksheet(excel, sheet_name, default=1)

        if delete_all:
            # 删除工作表中的所有批注
            Worksheet.delete_all_comments(worksheet)
        else:
            # 删除指定单元格的批注
            range_obj = Worksheet.get_range(worksheet, cell_position)
            Range.delete_comment(range_obj)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_location",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_location.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_text_to_number(
        excel_obj: ExcelObj,
        sheet_name: str = "",
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        range_location: str = "",
    ):
        """
        Excel 文本转数值格式

        Args:
            excel_obj: Excel对象
            sheet_name: 工作表名称
            select_type: 选择类型（CELL/ROW/COLUMN/AREA/ALL）
            cell_position: 单元格位置（用于CELL类型）
            row: 行号（用于ROW类型）
            col: 列号（用于COLUMN类型）
            range_location: 区域位置（用于AREA类型）
        """
        worksheet = Worksheet.get_worksheet(excel_obj, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        # 计算单元格位置
        cell_positions = calculate_cell_positions(
            design_type=select_type.value,
            cell_position=cell_position,
            range_position=range_location,
            col=col,
            row=row,
            r_end_row=r_end_row,
            r_end_col=r_end_col,
            r_address=r_address,
        )

        # 使用一个临时单元格来存储转换结果
        temp_cell = "{}{}".format(column_number_to_letter(r_end_col), r_end_row + 1)
        temp_range = Worksheet.get_range(worksheet, temp_cell)

        # 遍历所有单元格位置
        for cell_pos in cell_positions:
            range_obj = Worksheet.get_range(worksheet, cell_pos)
            Range.convert_text_to_number(range_obj, temp_range)

        # 清理临时单元格
        temp_range.Value = None

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "cell_position",
                dynamics=[
                    DynamicsItem(
                        key="$this.cell_position.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.CELL.value),
                    )
                ],
            ),
            atomicMg.param(
                "row",
                dynamics=[
                    DynamicsItem(
                        key="$this.row.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.ROW.value),
                    )
                ],
            ),
            atomicMg.param(
                "col",
                dynamics=[
                    DynamicsItem(
                        key="$this.col.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.COLUMN.value),
                    )
                ],
            ),
            atomicMg.param(
                "range_location",
                dynamics=[
                    DynamicsItem(
                        key="$this.range_location.show",
                        expression="return $this.select_type.value == '{}'".format(ReadRangeType.AREA.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_number_to_text(
        excel_obj: ExcelObj,
        sheet_name: str = "",
        select_type: ReadRangeType = ReadRangeType.CELL,
        cell_position: str = "",
        row: str = "",
        col: str = "",
        range_location: str = "",
    ):
        """
        Excel 数值转文本格式

        Args:
            excel_obj: Excel对象
            sheet_name: 工作表名称
            select_type: 选择类型（CELL/ROW/COLUMN/AREA/ALL）
            cell_position: 单元格位置（用于CELL类型）
            row: 行号（用于ROW类型）
            col: 列号（用于COLUMN类型）
            range_location: 区域位置（用于AREA类型）
        """
        worksheet = Worksheet.get_worksheet(excel_obj, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, r_address = used_range

        # 计算单元格位置
        cell_positions = calculate_cell_positions(
            design_type=select_type.value,
            cell_position=cell_position,
            range_position=range_location,
            col=col,
            row=row,
            r_end_row=r_end_row,
            r_end_col=r_end_col,
            r_address=r_address,
        )

        # 遍历所有单元格位置
        for cell_pos in cell_positions:
            range_obj = Worksheet.get_range(worksheet, cell_pos)
            Range.convert_number_to_text(range_obj)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "width",
                dynamics=[
                    DynamicsItem(
                        key="$this.width.show",
                        expression="return $this.set_type.value == '{}'".format(SetType.VALUE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_set_col_width(
        excel_obj: ExcelObj, sheet_name: str, set_type: SetType = SetType.AUTO, col: str = "", width: str = ""
    ):
        """
        设置指定列宽。
        :param excel_obj: Excel对象
        :param sheet_name: 工作表名称
        :param set_type: 设置方式 指定列宽,自动调整
        :param col: 指定列号（支持多列，如"A:B,C"或"1:3,5"）
        :param width: 指定列宽(0-255)
        """
        worksheet = Worksheet.get_worksheet(excel_obj, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, _ = used_range

        # 验证列宽输入
        if set_type == SetType.VALUE:
            if width == "":
                raise ValueError("指定列宽模式下，width参数不能为空！")
            try:
                width_float = float(width)
                assert width_float > 0
                assert width_float <= 255
            except Exception as e:
                raise ValueError("输入列宽有误，请检查！列宽范围：0-255")
        else:
            width_float = 0
        if col:
            col_list = handle_multiple_inputs(str(col), r_end_row, r_end_col, is_row=False)
        else:
            col_list = list(range(1, r_end_col + 1))
        for col_num in col_list:
            Range.set_column_width(Worksheet.get_columns(worksheet, col_num), set_type, width_float)

    @staticmethod
    @atomicMg.atomic(
        "Excel",
        inputList=[
            atomicMg.param("sheet_name", required=False),
            atomicMg.param(
                "height",
                dynamics=[
                    DynamicsItem(
                        key="$this.height.show",
                        expression="return $this.set_type.value == '{}'".format(SetType.VALUE.value),
                    )
                ],
            ),
        ],
        outputList=[],
    )
    def excel_set_row_height(
        excel_obj: ExcelObj, sheet_name: str, set_type: SetType = SetType.AUTO, row: str = "", height: str = ""
    ):
        """
        设置指定行高。
        :param excel_obj: Excel对象
        :param sheet_name: 工作表名称
        :param set_type: 设置方式 指定行高,自动调整
        :param row: 指定行号（支持多行，如"1:3,5"）
        :param height: 指定行高(0-409.5)
        """
        worksheet = Worksheet.get_worksheet(excel_obj, sheet_name, default=1)
        used_range = Worksheet.get_worksheet_used_range(worksheet)
        _, _, r_end_row, r_end_col, _ = used_range

        # 验证行高输入
        if set_type == SetType.VALUE:
            if height == "":
                raise ValueError("指定行高模式下，height参数不能为空！")
            try:
                height_float = float(height)
                assert height_float > 0
                assert height_float <= 409.5
            except Exception as e:
                raise ValueError("输入行高有误，请检查！行高范围：0-409.5")
        else:
            height_float = 0  # AUTO模式下不需要height

        if row:
            row_list = handle_multiple_inputs(str(row), r_end_row, r_end_col, is_row=True)
        else:
            row_list = list(range(1, r_end_row + 1))
        for row_num in row_list:
            Range.set_row_height(Worksheet.get_rows(worksheet, row_num), set_type, height_float)
