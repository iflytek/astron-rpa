from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空") + ": {}")
LOGIN_FAIL_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("登录失败") + ": {}")
