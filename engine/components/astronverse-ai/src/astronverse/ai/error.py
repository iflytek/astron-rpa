from astronverse.baseline.error.error import *
from astronverse.baseline.i18n.i18n import _

BizException = BizException

LLM_NO_RESPONSE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("大模型无返回结果，请重试") + ": {}")
