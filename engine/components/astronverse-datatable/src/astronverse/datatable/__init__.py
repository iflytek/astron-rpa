from enum import Enum


class BaseOperateType(Enum):
    CELL = "cell"  # 单元格操作
    ROW = "row"  # 行操作
    COLUMN = "column"  # 列操作
    AREA = "area"  # 区域操作


ReadType = BaseOperateType
WriteType = BaseOperateType
CopyType = BaseOperateType
PasteType = BaseOperateType
DeleteType = BaseOperateType


class WriteMode(Enum):
    OVERWRITE = "overwrite"  # 覆盖写入
    INSERT = "insert"  # 插入写入
    APPEND = "append"  # 追加写入


class CellInsertShift(Enum):
    """单元格插入，指定插入时其他单元格的移动方向"""

    DOWN = "down"  # 向下移动
    RIGHT = "right"  # 向右移动


class RowInsertShift(Enum):
    """行插入，指定插入到指定行的上方还是下方"""

    UP = "up"  # 向上插入
    DOWN = "down"  # 向下插入


class ColumnInsertShift(Enum):
    """列插入，指定插入到指定列的左侧还是右侧"""

    LEFT = "left"  # 向左插入
    RIGHT = "right"  # 向右插入


class AppendShift(Enum):
    ROW = "row"  # 行追加
    COLUMN = "column"  # 列追加


class InsertType(Enum):
    ROW = "row"  # 插入行
    COLUMN = "column"  # 插入列


class PasteValueType(Enum):
    VALUE = "value"  # 仅粘贴值
    FORMULA = "formula"  # 仅粘贴公式


class DeleteCellMove(Enum):
    LEFT = "left"  # 向左移动
    UP = "up"  # 向上移动


class SortOrder(Enum):
    ASCENDING = "ascending"  # 升序
    DESCENDING = "descending"  # 降序


class ExportFileType(Enum):
    XLSX = "xlsx"  # Excel 文件 .xlsx
    XLS = "xls"  # Excel 文件 .xls
    CSV = "csv"  # CSV 文件 .csv
    JSON = "json"  # JSON 文件 .json


class FilterType(Enum):
    ROW = "row"  # 按行过滤
    COLUMN = "column"  # 按列过滤
    TABLE = "table"  # 按表格过滤


class LoopType(Enum):
    ROW = "row"  # 按行遍历
    COLUMN = "column"  # 按列遍历
    AREA = "area"  # 按区域遍历


class ConditionType(Enum):
    EQUALS = "equals"  # 等于
    NOT_EQUALS = "not_equals"  # 不等于
    GREATER_THAN = "greater_than"  # 大于
    LESS_THAN = "less_than"  # 小于
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"  # 大于等于
    LESS_THAN_OR_EQUAL = "less_than_or_equal"  # 小于等于
    CONTAINS = "contains"  # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    IS_EMPTY = "is_empty"  # 为空
    IS_NOT_EMPTY = "is_not_empty"  # 不为空
    STARTS_WITH = "starts_with"  # 以...开头
    ENDS_WITH = "ends_with"  # 以...结尾
    DATE_BEFORE = "date_before"  # 日期在...之前
    DATE_AFTER = "date_after"  # 日期在...之后
    DATE_BETWEEN = "date_between"  # 日期在...之间


class FindType(Enum):
    COLUMN = "column"  # 按列查找
    TABLE = "table"  # 按表格查找
