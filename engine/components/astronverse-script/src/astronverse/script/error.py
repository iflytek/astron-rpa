from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误: {}"))

# 模块导入相关错误
MODULE_IMPORT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法导入模块: {}"))
MODULE_MAIN_FUNCTION_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("模块 {} 未定义可调用的 main 函数"))

MSG_MODULE_VERSION_WARRING = _("当前脚本为旧版规范, 建议更新新版脚本规范")
