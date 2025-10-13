"""本组件加密相关错误与错误码定义。

避免直接覆盖内置 `BaseException`，使用别名导入。
"""

from astronverse.baseline.error.error import BaseException as CoreBaseException
from astronverse.baseline.error.error import BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

__all__ = [
    "MSG_EMPTY_FORMAT",
    "BizCode",
    "CoreBaseException",
    "ErrorCode",
]

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空") + ": {}")
