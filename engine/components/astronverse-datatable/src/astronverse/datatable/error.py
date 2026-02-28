from astronverse.baseline.error.error import *
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 动态错误码（包含变量内容）
ROW_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("行数据有误， 行只能是大于0的正整数: {}"))
COL_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("列数据有误，列名只能是A,AB...: {}"))
DATAFRAME_FILE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据文件读取失败: {}"))
WRITE_DATA_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据写入失败: {}"))
WRITE_PERMISSION_DENIED_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("写入数据权限被拒绝，请关闭相关文件后重试: {}")
)
FORMULA_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("公式格式有误，公式必须是以=开头的字符串: {}"))
IMPORT_FILE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("导入文件失败: {}"))
IMPORT_FILE_NOT_FOUND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("导入文件不存在: {}"))

# 固定错误码（不包含变量）
COL_RANGE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("结束列不能小于开始列"))
ROW_RANGE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("结束行不能小于开始行"))
COL_PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("必须提供列名或列索引"))
IMPORT_FILE_PATH_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("导入文件路径不能为空"))
IMPORT_FILE_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("仅支持导入Excel(.xlsx, .xls)和CSV(.csv)文件"))

# 读取操作错误
READ_CELL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("读取单元格需要指定行列"))
READ_ROW_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("读取行需要指定行号"))
READ_COL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("读取列需要指定列号"))
READ_AREA_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("读取区域需要指定开始行列"))

# 写入操作错误
DATA_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据不能为空"))
WRITE_CELL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("写入单元格需要指定行列"))
WRITE_ROW_NUMBER_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("行号不能为空"))
WRITE_COL_NUMBER_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("列号不能为空"))
WRITE_AREA_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("区域写入需要指定开始行列"))

# 复制操作错误
COPY_CELL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("复制单元格需要指定行列"))
COPY_ROW_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("复制行需要指定行号"))
COPY_COL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("复制列需要指定列号"))
COPY_AREA_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("复制区域需要指定开始行列"))

# 粘贴操作错误
PASTE_CELL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("粘贴单元格需要指定行列"))
PASTE_ROW_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("粘贴行需要指定行号"))
PASTE_COL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("粘贴列需要指定列号"))
PASTE_AREA_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("粘贴区域需要指定开始行列"))

# 删除操作错误
DELETE_CELL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("删除单元格需要指定行列"))
DELETE_ROW_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("删除行需要指定行号"))
DELETE_COL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("删除列需要指定列号"))
DELETE_AREA_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("删除区域需要指定开始行列"))

# 遍历操作错误
LOOP_ROW_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("遍历行需要指定行号"))
LOOP_COL_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("遍历列需要指定列号"))
LOOP_AREA_PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("遍历区域需要指定开始行列"))

# 插入操作错误
INSERT_COUNT_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("插入数量不能为空"))
INSERT_COUNT_INVALID_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("插入数量必须大于0"))

# 公式操作错误
FORMULA_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("公式不能为空"))

# 列操作错误
COL_INFO_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("列信息不能为空"))

# 查找操作错误
FIND_CONTENT_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("查找内容不能为空"))

# 筛选操作错误
DATE_RANGE_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("日期范围不能为空"))
DATE_RANGE_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("日期范围格式错误，正确格式如：2023-01-01,2023-12-31"))

# 导出操作错误
EXPORT_FOLDER_PATH_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("导出文件夹路径不能为空"))
