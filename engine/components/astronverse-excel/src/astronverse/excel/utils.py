import os
import re
from typing import Any

import psutil
from astronverse.excel import FileExistenceType, ReadRangeType


def get_excel_processes():
    """
    检查当前运行的Excel和WPS进程

    Returns:
        tuple: (excel_flag, wps_flag, excel_pid, wps_pid)
            - excel_flag: Excel进程是否存在
            - wps_flag: WPS进程是否存在
            - excel_pid: Excel进程ID，如果不存在则为None
            - wps_pid: WPS进程ID，如果不存在则为None
    """
    excel_flag, wps_flag = False, False
    excel_pid, wps_pid = None, None
    pid_list = psutil.pids()
    for pid in pid_list:
        try:
            p = psutil.Process(pid)
            p_name = p.name().lower()
            if p_name == "excel.exe":
                excel_flag = True
                excel_pid = pid
            elif p_name == "et.exe":
                wps_flag = True
                wps_pid = pid
        except Exception as e:
            pass
    return excel_flag, excel_pid, wps_flag, wps_pid


def resolve_file_path(file_path, exist_type):
    """
    根据文件存在类型解析文件路径

    Args:
        file_path: 目标文件路径
        exist_type: 文件存在时的处理方式（FileExistenceType枚举）
            - OVERWRITE: 覆盖已存在文件，直接返回原路径
            - RENAME: 如果文件存在，自动重命名为文件名_1、文件名_2等
            - CANCEL: 如果文件存在，返回空字符串；否则返回原路径

    Returns:
        str: 处理后的文件路径，如果CANCEL且文件存在则返回空字符串
    """
    if exist_type == FileExistenceType.OVERWRITE:
        return file_path
    elif exist_type == FileExistenceType.RENAME:
        if os.path.exists(file_path):
            full_file_name = os.path.basename(file_path)
            file_name, file_ext = os.path.splitext(full_file_name)
            count = 1
            while True:
                new_full_file_name = f"{file_name}_{count}{file_ext}"
                new_file_path = os.path.join(os.path.dirname(file_path), new_full_file_name)
                if os.path.exists(new_file_path):
                    count += 1
                else:
                    return new_file_path
        return file_path
    elif exist_type == FileExistenceType.CANCEL:
        if os.path.exists(file_path):
            return ""
        else:
            return file_path


def column_letter_to_number(column_letter: str) -> int:
    """
    将列字母转换为列号（1-based）

    支持Excel列字母格式（如"A", "B", "Z", "AA", "AB"等）和数字格式。

    Args:
        column_letter: 列字母字符串（如"A"）或数字字符串（如"1"），空字符串返回1

    Returns:
        int: 列号（1-based），例如"A"返回1，"B"返回2，"AA"返回27
    """
    if not column_letter:
        return 1
    if column_letter.isdigit():
        return int(column_letter)
    column_letter = column_letter.upper()
    column_number = 0
    for i in range(len(column_letter)):
        column_number += (ord(column_letter[i]) - ord("A") + 1) * (26 ** (len(column_letter) - i - 1))
    return column_number


def column_number_to_letter(column: int) -> str:
    """
    将列号转换为列字母

    将数字列号转换为Excel列字母格式（如1->"A", 2->"B", 27->"AA"等）。

    Args:
        column: 列号（1-based），如果小于等于0则返回"A"

    Returns:
        str: 列字母字符串，例如1返回"A"，2返回"B"，27返回"AA"
    """
    if column <= 0:
        return "A"
    result_str = ""
    while column > 0:
        column -= 1
        result_str = chr(ord("A") + column % 26) + result_str
        column //= 26
    return result_str


def handle_row_input(row: Any, used_row: int) -> int:
    """
    处理行号输入，支持负数（从末尾开始计算）

    支持正数、负数和空字符串输入。负数表示从末尾开始计算，
    例如：used_row=10, row=-1 -> 10+1+(-1)=10 (最后一行)

    Args:
        row: 行号字符串，可以是正数、负数或空字符串
        used_row: 已使用的行数

    Returns:
        int: 处理后的行号（1-based），空字符串返回1

    Raises:
        ValueError: 当输入值无法转换为数字时抛出异常
    """
    if not row:
        return 1
    try:
        row_num = int(row)
        if row_num < 0:
            # 负数表示从末尾开始计算：used_row + 1 + row_num
            return used_row + 1 + row_num
        else:
            if row_num == 0:
                return 1
            return row_num
    except (ValueError, TypeError):
        raise ValueError(f"行号输入异常，请输入数字或负数！输入值: {row}")


def handle_column_input(col: str, used_col: int) -> int:
    """
    处理列号输入，支持负数（从末尾开始计算）

    支持字母（如"A"）、数字（如"1"）、负数（如"-1"）或空字符串输入。
    负数表示从末尾开始计算，例如：used_col=5, col=-1 -> 5+1+(-1)=5 (最后一列)

    Args:
        col: 列号字符串，可以是字母（如"A"）、数字（如"1"）、负数（如"-1"）或空字符串
        used_col: 已使用的列数

    Returns:
        int: 处理后的列号（1-based），空字符串返回1

    Raises:
        ValueError: 当输入值无法转换为数字或字母时抛出异常
    """
    if not col:
        return 1

    try:
        col_num = int(col)
        if col_num < 0:
            # 负数表示从末尾开始计算：used_col + 1 + col_num
            return used_col + 1 + col_num
        else:
            if col_num == 0:
                return 1
            return col_num
    except (ValueError, TypeError):
        # 如果不是数字，尝试作为字母处理
        return column_letter_to_number(col)


def handle_used_range(address: str):
    # 处理带符号的used_range 比如 $A$1:$B$2
    # 当sheet完全没用过的时候，address是$A$1
    address_list = address.split(":")
    if len(address_list) == 1:
        starter = address_list[0]
        ender = address_list[0]
    else:
        starter = address_list[0]
        ender = address_list[1]
    if address.find("$") == -1:
        start_col = re.findall(r"[A-Z]+", starter)[0]
        start_row = re.findall(r"[0-9]+", starter)[0]
        end_col = re.findall(r"[A-Z]+", ender)[0]
        end_row = re.findall(r"[0-9]+", ender)[0]
    else:
        start_col = starter.split("$")[1]
        start_row = starter.split("$")[2]
        end_col = ender.split("$")[1]
        end_row = ender.split("$")[2]
    return [start_col, start_row, end_col, end_row]


def handle_multiple_inputs(inputs: str, used_row: int, used_col: int, is_row=True):
    """
    处理多个列或行输入，比如A:B,C,-1

    Args:
        inputs: 输入字符串，支持逗号分隔和冒号范围，如 "1:3,5" 或 "A:B,C"
        used_row: 已使用的最大行号
        used_col: 已使用的最大列号
        is_row: 是否为行输入，True表示行，False表示列

    Returns:
        List[int]: 处理后的行号或列号列表
    """
    inputs = inputs.replace("，", ",").replace("：", ":")
    inputs = inputs.split(",")
    result = []
    for element in inputs:
        element = element.strip()
        if ":" in element:
            left_element = element.split(":")[0].strip()
            right_element = element.split(":")[1].strip()
            if is_row:
                left_num = handle_row_input(left_element, used_row)
                right_num = handle_row_input(right_element, used_row)
            else:
                left_num = handle_column_input(left_element, used_col)
                right_num = handle_column_input(right_element, used_col)
            for i in range(left_num, right_num + 1):
                result.append(i)
        else:
            if is_row:
                result.append(handle_row_input(element, used_row))
            else:
                result.append(handle_column_input(element, used_col))
    return result


def check_color(color: str):
    if not color:
        return color
    if isinstance(color, str):
        color = color.split(",")
        try:
            color = [int(c.strip()) for c in color]
        except Exception as e:
            raise ValueError("请输入正确的颜色格式！")
    if isinstance(color, list):
        if len(color) != 3:
            raise ValueError("请输入正确的颜色格式！")
        for rgb in color:
            if (not isinstance(rgb, int)) or rgb >= 256 or rgb < 0:
                raise ValueError("请输入正确的颜色格式！")
    else:
        raise ValueError("请输入正确的颜色格式！")
    return color


def util_trim(value):
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return [util_trim(v) for v in value]
    return value


def util_replace_node(value):
    if value is None:
        return ""
    elif isinstance(value, list):
        return [util_replace_node(v) for v in value]
    return value


def calculate_cell_positions(
    design_type: str,
    cell_position: str = "",
    range_position: str = "",
    col: str = "",
    row: str = "",
    r_end_row: int = 0,
    r_end_col: int = 0,
    r_address: str = "",
    support_comma: bool = True,
    support_colon: bool = True,
) -> list[str]:
    end_col_letter = column_number_to_letter(r_end_col)
    positions: list[str] = []

    def _handler(raw: str, single_fn, range_fn) -> None:
        raw = raw.replace("，", ",").replace("：", ":")
        if ":" in raw:
            if not support_colon:
                raise Exception("不支持范围输入（冒号分隔）")
            a, b = raw.split(":", 1)
            positions.append(range_fn(a, b))
        elif "," in raw:
            if not support_comma:
                raise Exception("不支持多个值输入（逗号分隔）")
            for item in raw.split(","):
                positions.append(single_fn(item))
        else:
            positions.append(single_fn(raw))

    if design_type == ReadRangeType.CELL.value:
        positions.append(cell_position)
    elif design_type == ReadRangeType.ROW.value:
        if isinstance(row, str):
            _handler(
                row,
                lambda r: f"A{handle_row_input(r, r_end_row)}:{end_col_letter}{handle_row_input(r, r_end_row)}",
                lambda r1, r2: f"A{handle_row_input(r1, r_end_row)}:{end_col_letter}{handle_row_input(r2, r_end_row)}",
            )
        else:
            r = handle_row_input(row, r_end_row)
            positions.append(f"A{r}:{end_col_letter}{r}")
    elif design_type == ReadRangeType.COLUMN.value:
        if isinstance(col, str):
            _handler(
                col,
                lambda c: f"{column_number_to_letter(handle_column_input(c, r_end_col))}1:"
                f"{column_number_to_letter(handle_column_input(c, r_end_col))}{r_end_row}",
                lambda c1, c2: f"{column_number_to_letter(handle_column_input(c1, r_end_col))}1:"
                f"{column_number_to_letter(handle_column_input(c2, r_end_col))}{r_end_row}",
            )
        else:
            c = column_number_to_letter(handle_column_input(col, r_end_col))
            positions.append(f"{c}1:{c}{r_end_row}")
    elif design_type == ReadRangeType.AREA.value:
        c1, r1, c2, r2 = handle_used_range(range_position)
        positions.append(f"{c1}{r1}:{c2}{r2}")
    elif design_type == ReadRangeType.ALL.value:
        c1, r1, c2, r2 = handle_used_range(r_address)
        positions.append(f"{c1}{r1}:{c2}{r2}")
    else:
        raise NotImplementedError()
    return positions
