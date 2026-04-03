from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# 平台和浏览器相关错误
UNSUPPORTED_PLATFORM_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的平台: {}"))
UNSUPPORTED_BROWSER_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的浏览器类型: {}"))

# 文件和注册表相关错误
FILE_NOT_FOUND_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件未找到: {}"))
REGISTRY_NOT_FOUND_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("注册表项未找到: {}"))
INVALID_FILENAME: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件名不匹配预期格式"))

# 浏览器特定错误
FIREFOX_PROFILE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("Firefox profile 未找到"))
BROWSER_360_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("360浏览器未安装或注册表项未找到"))
BROWSER_360X_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("360极速浏览器未安装或注册表项未找到"))
CHROME_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("Chrome 未安装或注册表项未找到"))
FIREFOX_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("Firefox 未安装或注册表项未找到"))
EDGE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("Microsoft Edge 未安装或注册表项未找到"))

# 插件相关错误
PLUGIN_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到插件"))
NO_PERMISSION_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("没有权限写入: {}"))
