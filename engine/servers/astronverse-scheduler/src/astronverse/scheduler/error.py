from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# 文件
FILE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件不存在: {}"))

# 虚拟桌面
VIRTUAL_DESK_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("虚拟桌面错误: {}"))

# 执行器
EXECUTOR_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("执行器错误: {}"))

# 通知
NOTIFY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("通知发送失败: {}"))

# 凭证
CREDENTIAL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("凭证错误: {}"))
