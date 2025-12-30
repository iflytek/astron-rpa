from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

DATAFRAME_EXPECTION = BaseException

PARAMS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数有误") + ": {}")
DATAFRAME_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据表格格式有误") + ": {}")
ROW_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("行数据有误， 行只能是大于1的正整数") + ": {}")
COL_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("列数据有误，列名只能是A,AB...") + ": {}")
AREA_FORMAT_ERROR: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("区域数据有误，区域数据只能是字符串，字符串数组，二维字符串数组的一种") + ": {}"
)

CELL_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("单元格读取失败") + ": {}")
DATAFRAME_FILE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据文件读取失败") + ": {}")

DATA_NONE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据不能为空") + ": {}")
WRITE_DATA_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据写入失败") + ": {}")
WRITE_PERMISSION_DENIED_ERROR_FORMAT: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("写入数据权限被拒绝，请关闭相关文件后重试") + ": {}"
)

FORMULA_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("公式格式有误，公式必须是以=开头的字符串") + ": {}")
IMPORT_FILE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("导入文件失败") + ": {}")
