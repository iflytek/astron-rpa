from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

FILE_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片文件不存在!"))

# 加密/解密特定错误
ENCRYPT_OBJECT_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("加密对象不能为空"))
DECRYPT_OBJECT_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("解密对象不能为空"))
STRING_TYPE_REQUIRED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("请提供字符串类型对象"))
