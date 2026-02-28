from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# 平台和浏览器相关错误
UNSUPPORTED_PLATFORM: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的平台: {}"))
UNSUPPORTED_BROWSER: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的浏览器类型: {}"))

# 文件和注册表相关错误
FILE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件未找到: {}"))
REGISTRY_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("注册表项未找到: {}"))
INVALID_FILENAME: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件名不匹配预期格式"))

# 插件相关错误
PLUGIN_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到插件"))
NO_PERMISSION: ErrorCode = ErrorCode(BizCode.LocalErr, _("没有权限写入: {}"))
