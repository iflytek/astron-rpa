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
VIRTUAL_DESK_NOT_ENABLED: ErrorCode = ErrorCode(BizCode.LocalErr, _("虚拟桌面未开启"))
VIRTUAL_DESK_TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, _("虚拟桌面启动超时"))

# 执行器
EXECUTOR_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("执行器错误: {}"))
EXECUTOR_LOG_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务日志上报异常"))
EXECUTOR_TIMEOUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("启动失败: 运行超时"))
EXECUTOR_RUNNING_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("已有实例运行，启动失败"))
EXECUTOR_API_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务端接口异常，工程运行失败"))
EXECUTOR_PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数传递失败"))
EXECUTOR_START_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("启动失败: {}"))

# 通知
NOTIFY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("通知发送失败: {}"))
EMAIL_LOGIN_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("发送异常邮件登陆失败"))
EMAIL_SEND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("发送异常邮件发送失败"))
SMS_SEND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("发送短信接口调用失败"))
SMS_SEND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("发送短信接口调用失败: {}"))

# 凭证
CREDENTIAL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("凭证错误: {}"))
CREDENTIAL_EXISTS_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("凭证 '{}' 已存在"))

# 工具解析
PARSE_PYTHON_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("解析 Python 代码失败: {}"))
DOCSTRING_TITLE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("docstring 第一行应为 'title: ...'"))
PARSE_PARAM_LINE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法解析参数行: {}"))
PARSE_FIELD_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("解析字段类型失败: {}"))

# AI 工具
UNSUPPORTED_FILE_EXT_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的文件扩展类型: {}"))
CUSTOM_FACTORS_FORMAT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("custom_factors 格式错误，请检查"))

# pip
PIP_DOWNLOAD_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("pip 下载失败: {}"))
PIP_INSTALL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("pip 安装失败: {}"))
