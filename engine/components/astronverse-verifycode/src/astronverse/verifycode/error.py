from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 固定错误消息
API_RESULT_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("第三方接口返回为空"))
MARGIN_LEFT_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到 margin-left / left属性。请尝试重新拾取。"))
ELEMENT_NOT_UNIQUE: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器元素定位不唯一，请检查！"))
