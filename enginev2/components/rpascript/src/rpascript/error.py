from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

CODE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("脚本数据为空"))
SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误") + ": {}")
