from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

CODE_OK: ErrorCode = ErrorCode(BizCode.LocalOK, "ok", 200)
CODE_INNER: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"), 200)
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"), 200)
PARAMETER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"), 200)

# Native Messaging 相关错误
UNSUPPORTED_PLATFORM: ErrorCode = ErrorCode(BizCode.LocalErr, _("native messaging 仅支持 Windows 平台"))
INVALID_BROWSER_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("无效的浏览器类型: {}"))
