from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

CODE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("脚本数据为空"))
SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误") + ": {}")

# 模块导入相关错误
MODULE_IMPORT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法导入模块: {}"))
MODULE_MAIN_FUNCTION_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("模块 {} 未定义可调用的 main 函数"))
