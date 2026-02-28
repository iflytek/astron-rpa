from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空: {}"))
FILE_PATH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件路径有误，请输入正确的路径！"))
EXCEL_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未检测到Excel/WPS应用"))
EXCEL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Excel错误: {}"))
DOCUMENT_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("文档不存在，请先打开文档！"))
FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("格式有误: {}"))
SHEET_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Sheet操作错误: {}"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# Excel 特定错误
LIST_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("填写的列表格式有误"))
CONTENT_LIST_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("填写内容的列表格式有误"))
INSERT_CONTENT_LIST_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("插入内容填写的列表格式有误"))
SHEET_NAME_EXISTS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("sheet名称已存在"))
SHEET_NAME_TOO_LONG_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("sheet名称过长,需要小于31个字符"))
REFERENCE_SHEET_NOT_FOUND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参考sheet名称不存在"))
COPY_SHEET_NAME_EXISTS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("复制sheet名称已存在"))
WIDTH_PARAM_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("指定列宽模式下，width参数不能为空！"))
WIDTH_VALUE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入列宽有误，请检查！列宽范围：0-255"))
HEIGHT_PARAM_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("指定行高模式下，height参数不能为空！"))
HEIGHT_VALUE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入行高有误，请检查！行高范围：0-409.5"))
