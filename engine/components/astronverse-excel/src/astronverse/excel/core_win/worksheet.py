from astronverse.excel import CopySheetLocationType
from astronverse.excel.excel_obj import ExcelObj


class Worksheet:
    @staticmethod
    def get_worksheet(excel_obj: ExcelObj, sheet_name: str = "", default: int = 0) -> object:
        workbook = excel_obj.obj
        if not sheet_name:
            if default == 0:
                return Worksheet.get_active_worksheet(excel_obj)
            else:
                sheet_name = default

        # 尝试按名称获取
        try:
            return workbook.Worksheets(sheet_name)
        except Exception:
            # 尝试按索引获取
            try:
                sheet_index = int(sheet_name)
                if 1 <= sheet_index <= workbook.Sheets.Count:
                    return workbook.Worksheets(sheet_index)
            except ValueError:
                pass
            raise ValueError(f"工作表'{sheet_name}'不存在")

    @staticmethod
    def get_all_worksheets(excel_obj: ExcelObj) -> list[object]:
        """
        获取所有工作表对象列表

        Args:
            excel_obj: ExcelObj 实例

        Returns:
            所有工作表对象的列表
        """
        workbook = excel_obj.obj
        return [ws for ws in workbook.Sheets]

    @staticmethod
    def get_all_worksheet_names(excel_obj: ExcelObj) -> list[str]:
        """
        获取所有工作表名称

        Args:
            excel_obj: ExcelObj 实例

        Returns:
            所有工作表名称的列表
        """
        workbook = excel_obj.obj
        return [ws.Name for ws in workbook.Sheets]

    @staticmethod
    def get_active_worksheet(excel_obj: ExcelObj) -> object:
        """
        获取当前激活的工作表对象

        Args:
            excel_obj: ExcelObj 实例

        Returns:
            当前激活的工作表对象
        """
        workbook = excel_obj.obj
        return workbook.ActiveSheet

    @staticmethod
    def add_worksheet(excel_obj: ExcelObj, sheet_name: str, before=None, after=None):
        """
        新增工作表

        Args:
            excel_obj: ExcelObj 实例
            sheet_name: 新工作表名称
            before: 在指定工作表之前插入
            after: 在指定工作表之后插入
        """
        workbook = excel_obj.obj
        if before:
            new_sheet = workbook.Sheets.Add(Before=workbook.Sheets(before))
        elif after:
            new_sheet = workbook.Sheets.Add(After=workbook.Sheets(after))
        else:
            new_sheet = workbook.Sheets.Add(After=workbook.Sheets(workbook.Sheets.Count))
        new_sheet.Name = sheet_name
        return new_sheet

    @staticmethod
    def move_worksheet(worksheet, before=None, after=None):
        """
        移动指定工作表

        Args:
            worksheet: 要移动的工作表
            before: 移动到此工作表之前
            after: 移动到此工作表之后
        """
        workbook = worksheet.Parent
        ws = worksheet
        if before:
            ws.Move(Before=workbook.Sheets(before))
        elif after:
            ws.Move(After=workbook.Sheets(after))
        else:
            ws.Move(After=workbook.Sheets(workbook.Sheets.Count))

    @staticmethod
    def get_worksheet_name(worksheet) -> str:
        """
        获取工作表名称
        """
        return worksheet.Name

    @staticmethod
    def rename_worksheet(worksheet, new_name: str):
        """
        重命名工作表
        """
        worksheet.Name = new_name

    @staticmethod
    def delete_worksheet(worksheet):
        """
        删除指定工作表
        """
        workbook = worksheet.Parent
        worksheet.Delete()

    @staticmethod
    def copy_worksheet(
        worksheet, excel, location: CopySheetLocationType = CopySheetLocationType.LAST, is_same_workbook=False
    ):
        """
        复制工作表到指定工作簿

        Args:
            worksheet: 要复制的工作表对象
            excel: 目标工作簿对象
            location: 复制位置，BEFORE, AFTER, FIRST, LAST
            is_same_workbook
        """
        # 根据位置执行复制
        target_workbook = excel.obj
        if is_same_workbook:
            # 当前工作簿内复制，BEFORE/AFTER 相对于源工作表
            if location == CopySheetLocationType.BEFORE:
                worksheet.Copy(Before=worksheet)
            elif location == CopySheetLocationType.AFTER:
                worksheet.Copy(After=worksheet)
            elif location == CopySheetLocationType.FIRST:
                worksheet.Copy(Before=target_workbook.Worksheets(1))
            elif location == CopySheetLocationType.LAST:
                worksheet.Copy(After=target_workbook.Worksheets(target_workbook.Sheets.Count))
        else:
            # 跨工作簿复制，BEFORE/AFTER 相对于目标工作簿的活动工作表
            if location == CopySheetLocationType.BEFORE:
                worksheet.Copy(Before=target_workbook.Worksheets(target_workbook.ActiveSheet.Name))
            elif location == CopySheetLocationType.AFTER:
                worksheet.Copy(After=target_workbook.Worksheets(target_workbook.ActiveSheet.Name))
            elif location == CopySheetLocationType.FIRST:
                worksheet.Copy(Before=target_workbook.Worksheets(1))
            elif location == CopySheetLocationType.LAST:
                worksheet.Copy(After=target_workbook.Worksheets(target_workbook.Sheets.Count))

    @staticmethod
    def get_worksheet_used_range(worksheet):
        """安全获取已使用区域"""
        used_range = worksheet.UsedRange
        if used_range is None:
            return 1, 1, 0, 0
        return (
            used_range.Row,
            used_range.Column,
            used_range.Row + used_range.Rows.Count - 1,
            used_range.Column + used_range.Columns.Count - 1,
            used_range.Address,
        )

    @staticmethod
    def get_cell(worksheet, row: int, col: int) -> object:
        """
        获取单元格 Range 对象

        Args:
            worksheet: 工作表对象
            row: 行号（1-based）
            col: 列号（1-based）

        Returns:
            单元格 Range 对象（worksheet.Cells 返回的就是 Range 对象）
        """
        try:
            return worksheet.Cells(row, col)
        except Exception as e:
            raise ValueError(f"获取单元格({row}, {col})失败: {e}")

    @staticmethod
    def get_range(worksheet, cell: str) -> object:
        """
        获取区域 Range 对象

        Args:
            worksheet: 工作表对象
            cell: 区域字符串，如 "A1", "A1:B10"

        Returns:
            区域 Range 对象
        """
        try:
            return worksheet.Range(cell)
        except Exception as e:
            raise ValueError(f"获取区域 '{cell}' 失败: {e}")

    @staticmethod
    def get_rows(worksheet, rows) -> object:
        try:
            return worksheet.Rows(rows)
        except Exception as e:
            raise ValueError(f"获取区域 '{rows}' 失败: {e}")

    @staticmethod
    def get_columns(worksheet, columns) -> object:
        try:
            return worksheet.Columns(columns)
        except Exception as e:
            raise ValueError(f"获取区域 '{columns}' 失败: {e}")

    @staticmethod
    def get_range_from_cells(worksheet, start_cell, end_cell) -> object:
        """
        通过两个 Range 对象（Cells 对象）获取区域 Range 对象

        Args:
            worksheet: 工作表对象
            start_cell: 起始单元格 Range 对象（如 worksheet.Cells(row, col)）
            end_cell: 结束单元格 Range 对象（如 worksheet.Cells(row, col)）

        Returns:
            区域 Range 对象

        Example:
            start = worksheet.Cells(1, 1)
            end = worksheet.Cells(10, 5)
            range_obj = Worksheet.get_range_from_cells(worksheet, start, end)
        """
        try:
            return worksheet.Range(start_cell, end_cell)
        except Exception as e:
            raise ValueError(f"通过 Range 对象获取区域失败: {e}")

    @staticmethod
    def insert_picture(worksheet, image_path, pic_left=0, pic_top=0, pic_height=300, pic_width=400, pic_scale=1.0):
        """
        插入图片，并设置图片大小
        """
        picture = worksheet.Pictures().Insert(image_path)

        try:
            shape = picture.ShapeRange.Item(1)
            shape.LockAspectRatio = False
        except Exception:
            # 获取ShapeRange可能失败，兼容部分WPS等
            pass

        # 默认使用缩放比例
        if pic_scale != 1.0:
            from PIL import Image

            image = Image.open(image_path)
            width, height = image.size
            picture.Width = width * pic_scale
            picture.Height = height * pic_scale
        else:
            picture.Width = pic_width
            picture.Height = pic_height
        picture.Left = pic_left
        picture.Top = pic_top
        return picture

    @staticmethod
    def delete_all_comments(worksheet):
        """
        删除工作表中的所有批注

        Args:
            worksheet: 工作表对象

        Raises:
            ValueError: 当工作表中不存在批注时抛出异常
        """
        if worksheet.Comments.Count > 0:
            # 注意：Comments.Item 是动态的，删除后索引会变化，所以每次删除第一个
            while worksheet.Comments.Count > 0:
                worksheet.Comments.Item(1).Delete()
        else:
            raise ValueError("不存在批注")
