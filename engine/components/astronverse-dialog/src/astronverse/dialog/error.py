from astronverse.baseline.error.error import *
from astronverse.baseline.i18n.i18n import _

BizException = BizException

EXECUTABLE_PATH_NOT_FOUND_ERROR: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("指定窗口运行路径不存在,请检查路径信息: {}")
)
DIALOG_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("对话框操作失败: {}"))
