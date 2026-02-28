from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# 任务相关错误
TASK_TYPE_NOT_SUPPORTED: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的任务类型"))
TASK_NOT_IMPLEMENTED: ErrorCode = ErrorCode(BizCode.LocalErr, _("任务类型未实现"))

# 邮件相关错误
MAIL_PROTOCOL_NOT_SUPPORTED: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的邮件协议: {}"))

# 定时任务相关错误
FREQUENCY_FLAG_REQUIRED: ErrorCode = ErrorCode(BizCode.LocalErr, _("频率标识不能为空"))
FREQUENCY_OPTION_INVALID: ErrorCode = ErrorCode(BizCode.LocalErr, _("请选择正确的频次选项"))
FREQUENCY_NOT_IMPLEMENTED: ErrorCode = ErrorCode(BizCode.LocalErr, _("频率类型未实现"))

# 网关相关错误
GATEWAY_LIST_TRIGGER_FAILED: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取任务列表失败"))
