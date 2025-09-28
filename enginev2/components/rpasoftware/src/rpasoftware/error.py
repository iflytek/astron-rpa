from astronverse.baseline.i18n.i18n import _
from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode

BaseException = BaseException

APP_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("应用程序路径有误，请输入正确的路径！") + ": {}")
