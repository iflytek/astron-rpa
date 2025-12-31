from datetime import datetime

from astronverse.datatable import ConditionType, FilterType
from astronverse.datatable.error import COL_FORMAT_ERROR, DATAFRAME_EXPECTION, FORMULA_FORMAT_ERROR, ROW_FORMAT_ERROR


def validate(row=1, col="A"):
    """
    验证行列格式
    :param row: 行号
    :param col: 列标
    """
    print(f"Validating row: {row}, col: {col}")
    if col is None:
        raise DATAFRAME_EXPECTION(COL_FORMAT_ERROR.format(col), "列格式错误")
    if row is None:
        raise DATAFRAME_EXPECTION(ROW_FORMAT_ERROR.format(row), "行格式错误")
    try:
        row = int(row)
    except ValueError:
        pass
    try:
        col = int(col)
    except ValueError:
        pass
    if isinstance(col, str):
        if not (col.isalpha() and col.upper() >= "A"):
            raise DATAFRAME_EXPECTION(COL_FORMAT_ERROR.format(col), "列格式错误")
    elif isinstance(col, int) and col < 1:
        raise DATAFRAME_EXPECTION(COL_FORMAT_ERROR.format(col), "列格式错误")
    if not isinstance(row, int) or row < 1:
        raise DATAFRAME_EXPECTION(ROW_FORMAT_ERROR.format(row), "行格式错误")


def col_to_index(col="A") -> int:
    """将列标转换为索引"""
    try:
        col = int(col)
    except ValueError:
        pass
    if isinstance(col, int):
        return col - 1
    col = col.upper()
    index = 0
    for i, char in enumerate(reversed(col)):
        index += (ord(char) - ord("A") + 1) * (26**i)
    return index


def index_to_col(index=1) -> str:
    """将索引转换为列标"""
    col = ""
    index += 1  # 转换为1-based索引
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        col = chr(65 + remainder) + col
    return col


def validate_formula(formula: str):
    """
    验证公式格式
    :param formula: 公式字符串
    """
    if not isinstance(formula, str) or not formula.startswith("="):
        raise DATAFRAME_EXPECTION(FORMULA_FORMAT_ERROR.format(formula), "公式格式错误")


def filter_data(
    data: list,
    filter_type: FilterType,
    condition_type: ConditionType,
    condition_value: str,
    date_value: str,
    date_range: str,
    is_case_sensitive: bool,
) -> list:
    filtered_data = []
    if not data:
        return []
    if filter_type == FilterType.TABLE:  # 过滤表格数据
        for row in data:
            filtered_row = []
            for item in row:
                if value_check(
                    value=item,
                    condition_type=condition_type,
                    condition_value=condition_value,
                    date_value=date_value,
                    date_range=date_range,
                    is_case_sensitive=is_case_sensitive,
                ):
                    filtered_row.append(item)
            if filtered_row:
                filtered_data.append(filtered_row)
    else:
        for item in data:
            if value_check(
                value=item,
                condition_type=condition_type,
                condition_value=condition_value,
                date_value=date_value,
                date_range=date_range,
                is_case_sensitive=is_case_sensitive,
            ):
                if isinstance(item, datetime):
                    item = item.strftime("%Y-%m-%d %H:%M:%S")
                filtered_data.append(item)
    return filtered_data


def value_check(
    value: any, condition_type: ConditionType, condition_value: str, date_value, date_range, is_case_sensitive: bool
) -> bool:
    """过滤处理器"""
    val = value
    cond_val = condition_value

    # Handle case sensitivity for string operations
    if isinstance(val, str) and isinstance(cond_val, str) and not is_case_sensitive:
        val = val.lower()
        cond_val = cond_val.lower()

    if condition_type == ConditionType.EQUALS:
        return str(val) == str(cond_val)
    elif condition_type == ConditionType.NOT_EQUALS:
        return str(val) != str(cond_val)
    elif condition_type == ConditionType.GREATER_THAN:
        try:
            val_num = float(val)
            cond_val_num = float(cond_val)
            return val_num > cond_val_num
        except (ValueError, TypeError):
            return False
    elif condition_type == ConditionType.LESS_THAN:
        try:
            val_num = float(val)
            cond_val_num = float(cond_val)
            return val_num < cond_val_num
        except (ValueError, TypeError):
            return False
    elif condition_type == ConditionType.GREATER_THAN_OR_EQUAL:
        try:
            val_num = float(val)
            cond_val_num = float(cond_val)
            return val_num >= cond_val_num
        except (ValueError, TypeError):
            return False
    elif condition_type == ConditionType.LESS_THAN_OR_EQUAL:
        try:
            val_num = float(val)
            cond_val_num = float(cond_val)
            return val_num <= cond_val_num
        except (ValueError, TypeError):
            return False
    elif condition_type == ConditionType.CONTAINS:
        return str(val).find(str(cond_val)) != -1
    elif condition_type == ConditionType.NOT_CONTAINS:
        return str(val).find(str(cond_val)) == -1
    elif condition_type == ConditionType.IS_EMPTY:
        return val is None or val == ""
    elif condition_type == ConditionType.IS_NOT_EMPTY:
        return val is not None and val != ""
    elif condition_type == ConditionType.STARTS_WITH:
        return str(val).startswith(str(cond_val))
    elif condition_type == ConditionType.ENDS_WITH:
        return str(val).endswith(str(cond_val))
    elif condition_type == ConditionType.DATE_AFTER:
        try:
            val_date = val if isinstance(val, datetime) else datetime.strptime(val, "%Y-%m-%d")
            cond_date = datetime.strptime(date_value, "%Y-%m-%d")
            return val_date > cond_date
        except (ValueError, TypeError):
            return False
    elif condition_type == ConditionType.DATE_BEFORE:
        try:
            val_date = val if isinstance(val, datetime) else datetime.strptime(val, "%Y-%m-%d")
            cond_date = datetime.strptime(date_value, "%Y-%m-%d")
            return val_date < cond_date
        except (ValueError, TypeError):
            return False
    elif condition_type == ConditionType.DATE_BETWEEN:
        try:
            val_date = val if isinstance(val, datetime) else datetime.strptime(val, "%Y-%m-%d")
            start_date_str, end_date_str = date_range.split(",")
            start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d")
            return start_date <= val_date <= end_date
        except (ValueError, TypeError):
            return False
    return False
