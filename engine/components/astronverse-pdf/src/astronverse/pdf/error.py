from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

FILE_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("PDF文件路径有误，请输入正确的路径！: {}"))
PDF_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("PDF文件读取失败，请检查文件是否损坏！: {}"))
PDF_PASSWORD_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("PDF文件读取失败，请检查密码是否正确！: {}"))
PDF_PAGE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("页码错误: {}"))
PDF_TABLE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("所选页面没有表格"))
PDF_TABLE_MERGE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法拼接多表，建议将【是否合并】设置为否"))
IMAGE_LIST_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片文件列表不能为空"))
IMAGE_FILE_NOT_FOUND_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片文件不存在: {}"))
IMAGE_NO_VALID_FILES: ErrorCode = ErrorCode(BizCode.LocalErr, _("没有找到有效的图片文件"))
IMAGE_TO_PDF_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片转PDF失败: {}"))
