from astronverse.baseline.error.error import *
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# AI组件特定错误
LLM_NO_RESPONSE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("大模型无返回结果，请重试: {}"))
FILE_NOT_FOUND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件不存在: {}"))
UNSUPPORTED_FILE_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的文件类型: {}"))
UNKNOWN_RESPONSE_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未知的响应格式"))
