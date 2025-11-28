from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误") + ": {}")
CODE_INNER: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{} 参数异常"))
TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, "拾取超时")
TIMEOUT_LAG: ErrorCode = ErrorCode(BizCode.LocalErr, "拾取卡顿超过15s，请退出编辑器后重新进入")
NO_WEB_INFO: ErrorCode = ErrorCode(BizCode.LocalErr, "缺乏元素的web信息")

BROWSER_EXTENSION_INSTALL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件通信出错，请重试"))

BROWSER_EXTENSION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件错误") + ": {}")

WEB_GET_ElE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("网页元素查找失败") + " {}")

WEB_EXEC_ElE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("脚本执行错误") + ": {}")

BROWSER_EXTENSION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件错误") + ": {}")
