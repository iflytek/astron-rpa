"""
错误定义模块

定义RPA定位器相关的错误码和异常类型。
"""

from astronverse.baseline.error.error import ErrorCode, BaseException as RPABaseException, BizCode
from astronverse.baseline.i18n.i18n import _

# 重新导出基础异常类
RPABaseException = RPABaseException

NO_FIND_ELEMENT: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素无法找到"))
