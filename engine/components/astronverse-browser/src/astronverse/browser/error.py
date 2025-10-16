"""浏览器相关错误码定义。

注意：不要覆盖内置 ``BaseException`` ，这里引入的是框架自定义的异常类 ``BaseException``。

"""

from astronverse.baseline.error.error import BaseException as FrameworkBaseException
from astronverse.baseline.error.error import BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

# 对外仍然暴露 BaseException 名称
# pylint: disable=redefined-builtin
BaseException = FrameworkBaseException

PARAMETER_INVALID_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数异常") + ": {}")

WEB_LOAD_TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, _("网页加载超时，请重试"))
WEB_GET_BROWSER_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取浏览器对象失败"))
WEB_GET_URL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取网页URL失败"))
WEB_GET_TITLE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取当前页面标题失败"))
WEB_GET_ELE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("网页元素查找失败") + " {}")
WEB_GET_SIMILAR_ELE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器获取相似元素列表失败"))
WEB_GET_SELECTED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器获取下拉框选中值失败"))
WEB_GET_CHECKBOX_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器获取复选框选中值失败"))
WEB_PAGES_NUM_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("页面数量必须是整数"))
WEB_WAIT_TIME_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("等待时间不能小于0！"))
WEB_ELE_ATTR_NAME_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("请输入元素属性名称"))
WEB_EXEC_ELE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("脚本执行错误") + ": {}")


DOWNLOAD_WINDOW_NO_FIND: ErrorCode = ErrorCode(
    BizCode.LocalErr,
    _("未弹出下载窗口，可以尝试用模拟人工点击或设置浏览器始终弹出下载窗口"),
)
UPLOAD_WINDOW_NO_FIND: ErrorCode = ErrorCode(
    BizCode.LocalErr,
    _("未弹出上传窗口，可以尝试用模拟人工点击或设置浏览器始终弹出上传窗口"),
)

SWITCH_TAB_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("切换网页失败，没有找到符合条件的网页"))

BROWSER_EXTENSION_INSTALL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件通信出错，请重试"))
BROWSER_EXTENSION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件错误") + ": {}")

BROWSER_OPEN_TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, _("打开浏览器超时"))
BROWSER_GET_TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, _("目标浏览器未打开"))
BROWSER_PATH_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到浏览器路径，请输入浏览器路径再运行"))
BROWSER_NO_INSTALL: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器暂未安装"))

CODE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("脚本数据为空"))
CODE_NO_MAIN_FUNC: ErrorCode = ErrorCode(BizCode.LocalErr, _("代码中必须包含main函数"))

FOCUS_TIMEOUT_MUST_BE_POSITIVE: ErrorCode = ErrorCode(BizCode.LocalErr, _("焦点超时时间必须大于0"))
KEY_PRESS_INTERVAL_MUST_BE_NON_NEGATIVE: ErrorCode = ErrorCode(BizCode.LocalErr, _("按键输入间隔必须大于等于0"))
SELECT_MATCHING_APP_PATH: ErrorCode = ErrorCode(BizCode.LocalErr, _("请选择跟浏览器匹配的应用路径"))

LINUX_MUST_BROWSER_PATH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("Linux必须手动填入浏览器地址"))

# 显式导出符号，便于静态分析工具识别
__all__ = [
    "BROWSER_EXTENSION_ERROR_FORMAT",
    "BROWSER_EXTENSION_INSTALL_ERROR",
    "BROWSER_GET_TIMEOUT",
    "BROWSER_NO_INSTALL",
    "BROWSER_OPEN_TIMEOUT",
    "BROWSER_PATH_EMPTY",
    "CODE_EMPTY",
    "CODE_NO_MAIN_FUNC",
    "DOWNLOAD_WINDOW_NO_FIND",
    "FOCUS_TIMEOUT_MUST_BE_POSITIVE",
    "KEY_PRESS_INTERVAL_MUST_BE_NON_NEGATIVE",
    "LINUX_MUST_BROWSER_PATH_ERROR",
    "PARAMETER_INVALID_FORMAT",
    "SELECT_MATCHING_APP_PATH",
    "SWITCH_TAB_ERROR",
    "UPLOAD_WINDOW_NO_FIND",
    "WEB_ELE_ATTR_NAME_ERROR",
    "WEB_EXEC_ELE_ERROR",
    "WEB_GET_BROWSER_ERROR",
    "WEB_GET_CHECKBOX_ERROR",
    "WEB_GET_ELE_ERROR",
    "WEB_GET_SELECTED_ERROR",
    "WEB_GET_SIMILAR_ELE_ERROR",
    "WEB_GET_TITLE_ERROR",
    "WEB_GET_URL_ERROR",
    "WEB_LOAD_TIMEOUT",
    "WEB_PAGES_NUM_ERROR",
    "WEB_WAIT_TIME_ERROR",
    "BaseException",
]
