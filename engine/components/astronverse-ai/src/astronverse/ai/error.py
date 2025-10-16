"""AI 相关错误与错误码定义。"""

from astronverse.baseline.error.error import (
    BaseException as BaselineBaseException,
)
from astronverse.baseline.error.error import (
    BizCode,
    ErrorCode,
)
from astronverse.baseline.i18n.i18n import _


class AIBaseError(BaselineBaseException):
    """AI 模块自定义基础异常。"""


LLM_NO_RESPONSE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("大模型无返回结果，请重试") + ": {}")

# 保留兼容：外部仍可能引用 BaseException，这里导出 Baseline 基类
BaseException = BaselineBaseException  # type: ignore
