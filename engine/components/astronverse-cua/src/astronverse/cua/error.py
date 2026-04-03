from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# CUA 特定错误
UNKNOWN_RESPONSE_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("未知的响应格式"))
ASPECT_RATIO_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片宽高比错误: {}"))
ACTION_PARSE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("动作解析失败: {}"))
ACTION_PARSE_NO_MATCH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("在输入字符串中未找到匹配的模式"))
