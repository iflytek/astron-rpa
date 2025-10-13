from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

EXECUTABLE_PATH_NOT_FOUND_ERROR: ErrorCode = ErrorCode(
    BizCode.LocalErr, _("指定窗口运行路径不存在,请检查路径信息") + ": {}"
)
