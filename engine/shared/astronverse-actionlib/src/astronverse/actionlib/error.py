from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
IGNORE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{}"))
TYPE_KIND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("类型错误: {}"))

# 配置文件错误
CONFIG_LOAD_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("配置文件加载出错: {}"))
CONFIG_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("配置文件解析不支持该类型: {}"))

# 参数错误
REQUIRED_PARAM_MISSING: ErrorCode = ErrorCode(BizCode.LocalErr, _("缺少必填参数: {}"))
PARAM_ARGS_NO_SUPPORT_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数不支持args: {}"))
PARAM_REQUIRED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数 {} 必填"))
PARAM_VALUE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数 {} 的值错误{}"))
PARAM_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{} 的值类型错误{}"))
PARAM_CONVERT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数 {} 的值转换成 {} 失败，原始值: {}"))
PARAM_VERIFY_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数 {} 验证失败: {}"))
VALUE_IS_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("{} 参数值不能为空"))

# 报告相关消息
ReportStartMsgFormat = _("{} 执行第{}条指令 [{}]")
ReportCodeError = _("执行错误")
ReportCodeSkip = _("执行错误跳过")
ReportCodeRetry = _("执行错误重试")


class IgnoreException(BizException):
    """内部已经处理了错误, 外部可忽略错误细节的错误"""

    pass


class ParamException(BizException):
    """参数错误，额外携带出错的参数名"""

    pass
