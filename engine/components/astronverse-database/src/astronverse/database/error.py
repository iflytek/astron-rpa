from astronverse.baseline.error.error import *
from astronverse.baseline.i18n.i18n import _

BizException = BizException

UNSUPPORTED_DATABASE_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("找不到该数据库类型!"))
