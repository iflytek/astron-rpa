from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))

# 参数错误
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))
IOBJECTID_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("iObjectId必须是整数类型"))

# 元素定位错误
NO_FIND_ELEMENT: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素无法找到"))

# 浏览器插件相关错误
BROWSER_PLUGIN_CHANNEL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件通信通道出错，请重启应用"))
BROWSER_PLUGIN_COMMUNICATION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件通信失败, 请检查插件是否安装并启用"))
BROWSER_PLUGIN_GET_ELEMENT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件获取元素失败: {}"))
BROWSER_PLUGIN_CONNECTION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法连接浏览器插件服务，请确认插件状态"))
BROWSER_PLUGIN_TIMEOUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件响应超时，请检查插件是否安装并启用"))
BROWSER_WINDOW_NOT_FOUND_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到浏览器窗口: {}"))
