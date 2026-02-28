from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException


INVALID_APP_PATH_ERROR_CODE: ErrorCode = ErrorCode(BizCode.LocalErr, _("应用程序路径有误，请输入正确的路径！: {}"))
