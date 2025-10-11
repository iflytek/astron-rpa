from astronverse.baseline.error.error import BaseException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

PATH_INVALID_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("上传路径有误") + ": {}")
FILE_UPLOAD_FAILED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("上传失败") + ": {}")
FILE_DOWNLOAD_FAILED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("下载失败") + ": {}")
