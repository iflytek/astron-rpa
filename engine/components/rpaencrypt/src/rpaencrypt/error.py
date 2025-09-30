from rpaframe.i18n.i18n import _
from rpaframe.error.error import BaseException, BizCode, ErrorCode

BaseException = BaseException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空") + ": {}")
