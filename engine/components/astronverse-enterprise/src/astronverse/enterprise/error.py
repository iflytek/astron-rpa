from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException


SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误: {}"))
PATH_INVALID_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("上传路径有误: {}"))
FILE_UPLOAD_FAILED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("上传失败: {}"))
FILE_DOWNLOAD_FAILED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("下载失败: {}"))
FOLDER_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件夹路径错误: {}"))
