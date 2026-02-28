from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))
FILE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片文件不存在!"))
