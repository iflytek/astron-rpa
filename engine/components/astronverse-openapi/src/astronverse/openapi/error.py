from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("消息为空: {}"))
AI_SERVER_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("ai服务器无响应或错误"))
AI_REQ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("ai服务请求异常 {}"))
IMAGE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片路径不存在或格式错误"))
INVALID_URL_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("无效的请求URL: {}"))
EXCEL_WORKSHEET_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法获取活动工作表"))
