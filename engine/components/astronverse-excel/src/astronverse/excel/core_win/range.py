from typing import Any, Optional

from astronverse.excel import (
    ClearType,
    FontNameType,
    FontType,
    HorizontalAlign,
    NumberFormatType,
    ReadRangeType,
    SetType,
    VerticalAlign,
)


class Range:
    @staticmethod
    def get_range_data(range_obj, use_text: bool = False) -> Any:
        """
        获取区域数据

        Args:
            range_obj: Range 对象
            use_text: 是否返回文本，默认为 False
        """
        try:
            return range_obj.Text if use_text else range_obj.Value
        except Exception as e:
            raise ValueError(f"获取区域数据失败: {e}")

    @staticmethod
    def get_range_color(range_obj) -> tuple[int, int, int]:
        """
        获取单元格区域的背景颜色（RGB格式）

        Args:
            range_obj: Range 对象

        Returns:
            Tuple[int, int, int]: RGB颜色元组 (r, g, b)，每个值范围 0-255
        """
        try:
            # Excel 的 Interior.Color 返回 BGR 格式的颜色值
            color_num = range_obj.Interior.Color
            # 将 BGR 转换为 RGB
            # Excel 颜色格式: B + (G * 256) + (R * 65536)
            r = int(color_num) // (256**2) % 256
            g = (int(color_num) // 256) % 256
            b = int(color_num) % 256
            return r, g, b
        except Exception as e:
            raise ValueError(f"获取单元格颜色失败: {e}")

    @staticmethod
    def get_range_size(range_obj) -> tuple[int, int, int, int]:
        """
        获取区域的位置
        """
        return range_obj.Left, range_obj.Top, range_obj.Width, range_obj.Height

    @staticmethod
    def set_range_data(range_obj, value: Any):
        """
        设置区域数据

        Args:
            range_obj: Range 对象
            value: 要设置的值
        """
        try:
            range_obj.Value = value
        except Exception as e:
            raise ValueError(f"设置区域数据失败: {e}")

    @staticmethod
    def set_range_type(
        range_obj,
        col_width: Optional[str] = None,
        bg_color: Optional[tuple[int, int, int]] = None,
        font_color: Optional[tuple[int, int, int]] = None,
        font_type: FontType = FontType.NO_CHANGE,
        font_name: FontNameType = FontNameType.NO_CHANGE,
        font_size: Optional[int] = None,
        number_format: NumberFormatType = NumberFormatType.NO_CHANGE,
        number_format_other: str = "",
        horizontal_align: HorizontalAlign = HorizontalAlign.NO_CHANGE,
        vertical_align: VerticalAlign = VerticalAlign.NO_CHANGE,
        wrap_text: bool = True,
        design_type: ReadRangeType = ReadRangeType.CELL,
        auto_row_height: bool = False,
        auto_column_width: bool = False,
    ):
        """
        设置区域格式

        Args:
            range_obj: Range 对象
            col_width: 列宽
            bg_color: 背景颜色 RGB 元组 (r, g, b)
            font_color: 字体颜色 RGB 元组 (r, g, b)
            font_type: 字体类型
            font_name: 字体名称
            font_size: 字体大小
            number_format: 数字格式类型
            number_format_other: 自定义数字格式
            horizontal_align: 水平对齐方式
            vertical_align: 垂直对齐方式
            wrap_text: 是否自动换行
            design_type: 设计类型（用于判断自动调整行高/列宽）
            auto_row_height: 是否自动调整行高
            auto_column_width: 是否自动调整列宽
        """
        # Excel 对齐常量映射
        XlHAlign_map = {
            HorizontalAlign.DEFAULT.value: 1,  # xlHAlignGeneral
            HorizontalAlign.LEFT.value: -4131,  # xlHAlignLeft
            HorizontalAlign.RIGHT.value: -4152,  # xlHAlignRight
            HorizontalAlign.CENTER.value: -4108,  # xlHAlignCenter
            HorizontalAlign.PADDING.value: 5,  # xlHAlignFill
            HorizontalAlign.BOTH.value: -4130,  # xlHAlignJustify
            HorizontalAlign.CROSS.value: 7,  # xlHAlignCenterAcrossSelection
            HorizontalAlign.DISTRIBUTED.value: -4117,  # xlHAlignDistributed
        }

        XlVAlign_map = {
            VerticalAlign.UP.value: -4160,  # xlVAlignTop
            VerticalAlign.MIDDLE.value: -4108,  # xlVAlignCenter
            VerticalAlign.DOWN.value: -4107,  # xlVAlignBottom
            VerticalAlign.BOTH.value: -4130,  # xlVAlignJustify
            VerticalAlign.DISTRIBUTED.value: -4117,  # xlVAlignDistributed
        }

        # RGB 函数（Excel COM 对象使用 BGR 顺序）
        def RGB(r, g, b):
            return b + (g * 256) + (r * 65536)

        # 设置列宽
        if col_width:
            range_obj.ColumnWidth = col_width

        # 设置字体颜色
        if font_color:
            range_obj.Font.Color = RGB(
                font_color[0],
                font_color[1],
                font_color[2],
            )
        else:
            range_obj.Font.Color = RGB(0, 0, 0)

        # 设置背景颜色
        if bg_color:
            bg_color = tuple(bg_color)
            range_obj.Interior.Color = RGB(
                bg_color[0],
                bg_color[1],
                bg_color[2],
            )
        else:
            range_obj.Interior.ColorIndex = 0

        # 设置字体名称
        if font_name != FontNameType.NO_CHANGE:
            range_obj.Font.Name = font_name.value

        # 设置字体大小
        if font_size:
            range_obj.Font.Size = font_size

        # 设置字体类型
        if font_type == FontType.BOLD:
            range_obj.Font.Bold = True
        elif font_type == FontType.ITALIC:
            range_obj.Font.Italic = True
        elif font_type == FontType.BOLD_ITALIC:
            range_obj.Font.Bold = True
            range_obj.Font.Italic = True
        elif font_type == FontType.NORMAL:
            range_obj.Font.Bold = False
            range_obj.Font.Italic = False

        # 自动换行
        range_obj.WrapText = True if wrap_text is True else False

        # 水平对齐
        if horizontal_align != HorizontalAlign.NO_CHANGE:
            range_obj.HorizontalAlignment = XlHAlign_map.get(horizontal_align.value)

        # 垂直对齐
        if vertical_align != VerticalAlign.NO_CHANGE:
            range_obj.VerticalAlignment = XlVAlign_map.get(vertical_align.value)

        # 自适应列宽/行高
        if design_type == ReadRangeType.ROW and auto_row_height:
            range_obj.Rows.AutoFit()
        if design_type == ReadRangeType.COLUMN and auto_column_width:
            range_obj.Columns.AutoFit()

        # 数字格式
        if number_format != NumberFormatType.NO_CHANGE:
            if number_format == NumberFormatType.CUSTOM:
                format_str = number_format_other
            else:
                format_str = number_format.value
            range_obj.NumberFormat = format_str

    @staticmethod
    def delete_range(range_obj, direction: str = "") -> None:
        """
        删除指定区域，可选择左移或上移

        Args:
            range_obj: Range 对象
            direction: 移动方向，RIGHT_MOVE_LEFT(右侧单元格左移)，LOWER_MOVE_UP(下方单元格上移)
        """
        try:
            XlDeleteShiftDirection_map = {
                "right_move_left": -4159,  # xlToLeft
                "lower_move_up": -4162,  # xlUp
            }
            shift = XlDeleteShiftDirection_map.get(direction)
            if shift:
                range_obj.Delete(Shift=shift)
            else:
                range_obj.Delete()
        except Exception as e:
            raise ValueError(f"删除区域失败: {e}")

    @staticmethod
    def clear_range(range_obj, clear_type: str = ""):
        """
        清理单元格区域内容、格式或全部

        Args:
            range_obj: Range 对象
            clear_type: 清理类型
        """
        try:
            if clear_type == ClearType.CONTENT.value:
                range_obj.ClearContents()
            elif clear_type == ClearType.STYLE.value:
                range_obj.ClearFormats()
            elif clear_type == ClearType.ALL.value:
                range_obj.ClearFormats()
                range_obj.Clear()
            else:
                raise ValueError(f"不支持的清理类型: {clear_type}")
        except Exception as e:
            raise ValueError(f"清理区域失败: {e}")

    @staticmethod
    def copy_range(
        range_obj,
    ):
        """
        拷贝单元格区域
        Args:
            range_obj: Range 对象
        """
        range_obj.Copy()

    @staticmethod
    def paste_range(
        range_obj,
        paste_type: str = "",
        skip_blanks=False,
        transpose=False,
    ):
        """
        粘贴区域的内容，支持多种粘贴方式

        Args:
            range_obj: Range 对象，粘贴起始区域
            paste_type: 粘贴类型
            skip_blanks: 跳过空白单元格
            transpose: 是否转置粘贴
        """
        paste_type_conf = {
            "all": -4104,  # 默认全部
            "value_and_format": 12,  # 值和数字格式
            "format": -4122,  # 仅格式
            "exclude_frame": 7,  # 边框除外
            "col_width_only": 8,  # 仅列宽
            "formula_only": -4123,  # 仅公式
            "formula_and_format": 11,  # 公式和数字格式
            "paste_value": -4163,  # 粘贴值
        }
        paste_type_value = paste_type_conf.get(paste_type)
        if paste_type_value is None:
            raise ValueError(f"不支持的粘贴类型: {paste_type_value}")

        try:
            range_obj.PasteSpecial(Paste=paste_type_value, SkipBlanks=bool(skip_blanks), Transpose=bool(transpose))
        except Exception as e:
            raise ValueError(f"区域粘贴失败: {e}")

    @staticmethod
    def insert_range(range_obj, axis: str = "row"):
        """
        插入整行或整列

        Args:
            range_obj: Range 对象
            axis: "row" 表示插入行, "column" 表示插入列
        """
        if axis == "row":
            # Excel 常量 -4162 表示 xlShiftDown
            range_obj.EntireRow.Insert(Shift=-4162)
        elif axis == "column":
            # Excel 常量 -4159 表示 xlShiftToRight
            range_obj.EntireColumn.Insert(Shift=-4159)
        else:
            raise ValueError(f"不支持的axis参数: {axis}")

    @staticmethod
    def merge_range(
        range_obj,
        job_type: str,
    ):
        """
        合并或拆分单元格区域

        Args:
            range_obj: Range 对象
            job_type: 操作类型，MERGE 表示合并，SPLIT 表示拆分
        """
        try:
            if job_type == "merge":
                range_obj.Merge()
            else:
                range_obj.UnMerge()
        except Exception as e:
            raise ValueError(f"合并/拆分单元格失败: {e}")

    @staticmethod
    def autofill_range(range_obj, target_range):
        """
        区域自动填充

        Args:
            range_obj: 起始 Range 对象（要自动填充的单元格/区域）
            target_range: 目标填充范围（Range 对象）
        """
        try:
            range_obj.AutoFill(target_range, 0)
        except Exception as e:
            raise ValueError(f"区域自动填充失败: {e}")

    @staticmethod
    def set_row_height(range_obj, set_type: SetType, height_float: float):
        """
        设置行高

        Args:
            range_obj: Range 对象（通常是 worksheet.Rows(row_num) 返回的 Range）
            set_type: 设置类型（VALUE 或 AUTO）
            height_float: 行高值（仅在 VALUE 模式下使用）
        """
        if set_type == SetType.VALUE:
            # 指定行高
            range_obj.RowHeight = height_float
        elif set_type == SetType.AUTO:
            # 自动调整行高
            range_obj.AutoFit()

    @staticmethod
    def set_column_width(range_obj, set_type: SetType, width_float: float):
        """
        设置列宽

        Args:
            range_obj: Range 对象（通常是 worksheet.Columns(col_num) 返回的 Range）
            set_type: 设置类型（VALUE 或 AUTO）
            width_float: 列宽值（仅在 VALUE 模式下使用）
        """
        if set_type == SetType.VALUE:
            # 指定列宽
            range_obj.ColumnWidth = width_float
        elif set_type == SetType.AUTO:
            # 自动调整列宽
            range_obj.AutoFit()

    @staticmethod
    def convert_text_to_number(range_obj, temp_range):
        """
        将范围内的文本格式转换为数值格式

        Args:
            range_obj: Range 对象（要转换的范围）
            temp_range: 临时单元格 Range 对象（用于存储 VALUE 函数结果）
        """
        # 遍历范围内的每个单元格
        for cell in range_obj.Cells:
            cell_address = cell.Address.replace("$", "")
            cell_value = cell.Value

            # 跳过空单元格
            if cell_value in ["", None]:
                continue

            # 设置数字格式为通用格式
            cell.NumberFormat = "G/通用格式"

            # 使用 VALUE 函数转换
            temp_range.Value = "=VALUE({})".format(cell_address)
            temp_value = temp_range.Value

            # 如果转换成功（不是错误值），更新单元格值
            # Excel 错误值通常是 -2146826273.0 (xlErrValue)
            if temp_value != -2146826273.0:
                cell.Value = temp_value

    @staticmethod
    def convert_number_to_text(range_obj):
        """
        将范围内的数值格式转换为文本格式

        Args:
            range_obj: Range 对象（要转换的范围）
        """
        # 遍历范围内的每个单元格
        for cell in range_obj.Cells:
            cell_value = cell.Value

            # 如果值不是字符串类型，转换为文本格式
            if not isinstance(cell_value, str):
                # 设置数字格式为文本格式（"@" 表示文本）
                cell.NumberFormat = "@"
                # 使用 Text 属性获取显示值并设置为文本
                cell.Value = cell.Text

    @staticmethod
    def add_comment(range_obj, comment_text: str):
        """
        为范围添加批注

        Args:
            range_obj: Range 对象（要添加批注的单元格）
            comment_text: 批注文本内容
        """
        if not range_obj.Comment:
            range_obj.AddComment()
        range_obj.Comment.Text(comment_text)

    @staticmethod
    def delete_comment(range_obj):
        """
        删除范围的批注

        Args:
            range_obj: Range 对象（要删除批注的单元格）

        Raises:
            ValueError: 当单元格不存在批注时抛出异常
        """
        if range_obj.Comment:
            range_obj.ClearComments()
        else:
            raise ValueError("不存在批注")

    @staticmethod
    def search_and_replace(
        range_obj,
        find_str: str,
        replace_str: str = "",
        exact_match: bool = False,
        case_flag: bool = False,
        match_all: bool = True,
    ) -> list:
        """
        在范围内搜索并可选地替换文本

        Args:
            range_obj: Range 对象（要搜索的范围）
            find_str: 要查找的字符串
            replace_str: 要替换的字符串（如果为空则不替换）
            exact_match: 是否精确匹配（True: 完全匹配, False: 部分匹配）
            case_flag: 是否区分大小写
            match_all: 是否查找所有匹配项（True: 所有, False: 仅第一个）

        Returns:
            list: 匹配的单元格信息列表，每个元素包含 {"row": 行号, "col": 列字母}
        """
        # Excel 常量
        xlWhole = 1  # 完全匹配
        xlPart = 2  # 部分匹配
        xlValues = -4163  # 在值中查找

        look_at = xlWhole if exact_match else xlPart
        match_case = 1 if case_flag else 0

        positions = set()
        found_cell = range_obj.Find(
            find_str,
            LookAt=look_at,
            LookIn=xlValues,
            MatchCase=match_case,
        )

        if found_cell is not None:
            first_address = found_cell.Address
            positions.add(first_address)

            # 如果需要替换
            if replace_str:
                cell_value = str(found_cell.Value) if found_cell.Value is not None else ""
                found_cell.Value = cell_value.replace(find_str, replace_str)

            # 如果需要查找所有匹配项
            if match_all:
                while True:
                    found_cell = range_obj.FindNext(found_cell)
                    if found_cell is None or found_cell.Address == first_address:
                        break
                    positions.add(found_cell.Address)

                    # 如果需要替换
                    if replace_str:
                        cell_value = str(found_cell.Value) if found_cell.Value is not None else ""
                        found_cell.Value = cell_value.replace(find_str, replace_str)

        # 格式化结果
        res = []
        import re

        from astronverse.excel.utils import column_letter_to_number

        for address in positions:
            # 地址格式通常是 "$A$1" 或 "A1"，需要提取列和行
            # 去掉 $ 符号后，使用正则表达式提取列字母和行号
            address_clean = address.replace("$", "")
            match = re.match(r"([A-Z]+)(\d+)", address_clean)
            if match:
                col = match.group(1)
                row = match.group(2)
                res.append({"row": int(row), "col": col, "col_num": column_letter_to_number(col)})

        # 按照行号优先，列号次之的顺序排序
        res.sort(key=lambda x: (x["row"], x["col_num"]))

        # 将行号转换回字符串
        for item in res:
            item["row"] = str(item["row"])
            del item["col_num"]

        return res
