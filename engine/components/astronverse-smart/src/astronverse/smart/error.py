from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))
ELEMENT_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素未找到"))
UNSUPPORTED_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的类型: {}"))
