from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 元素查找错误
ELEMENT_NO_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到元素"))
ELEMENT_WAIT_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("等待后未找到元素"))

# 窗口操作错误
WINDOW_NO_FIND_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("找不到窗口，请检查窗口是否已关闭: {}"))
WINDOW_SCROLL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("窗口滚动失败，请检查窗口是否已关闭: {}"))

# 拾取错误
UNPICKABLE_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("拾取元素不支持该拾取类型: {}"))
PATH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("拾取或保存路径有误"))

# 凭据错误
CREDENTIAL_NOT_SELECTED: ErrorCode = ErrorCode(BizCode.LocalErr, _("请先选择凭据名称"))
