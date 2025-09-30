from rpaframe.i18n.i18n import _
from rpaframe.error.error import BaseException, BizCode, ErrorCode

BaseException = BaseException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空") + ": {}")
AI_SERVER_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("ai服务器无响应或错误"))
AI_REQ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("ai服务请求异常 {}"))
IMAGE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片路径不存在或格式错误"))
