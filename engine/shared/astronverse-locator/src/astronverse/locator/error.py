from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

NO_FIND_ELEMENT: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素无法找到"))
