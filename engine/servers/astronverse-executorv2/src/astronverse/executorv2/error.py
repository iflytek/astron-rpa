import re
from functools import wraps
from astronverse.actionlib import IgnoreException
from astronverse.baseline.error.error import ErrorCode, BaseException, BizCode
from astronverse.baseline.i18n.i18n import _

# 通用错误
SUCCESS: ErrorCode = ErrorCode(BizCode.LocalOK, "ok")
GENERAL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
INTERNAL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误: {}"))
SERVER_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误: {}"))
SYNTAX_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("语法错误: {}"))

# 解析错误
LOOP_CONTROL_STATEMENT_ERROR = _("break和continue语句必须在循环结构中使用")
ATOMIC_CAPABILITY_PARSE_ERROR_FORMAT = _("原子能力 {} 解析失败")
MISSING_REQUIRED_KEY_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("缺少必需的key字段 {}"))
ONLY_ONE_CATCH_CAN_BE_RETAINED = _("只能保留一个catch语句")

# 外部获取
ELEMENT_ACCESS_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("元素获取异常: {}"))
PROCESS_ACCESS_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("工程数据异常: {}"))

# 报告和状态消息
MSG_FLOW_INIT_START = _("开始初始化...")
MSG_FLOW_INIT_SUCCESS = _("初始化完成")
MSG_TASK_EXECUTION_START = _("开始执行")
MSG_TASK_EXECUTION_END = _("执行结束")
MSG_TASK_USER_CANCELLED = _("执行结束，用户主动关闭")
MSG_TASK_EXECUTION_ERROR = _("执行错误")
MSG_INSTRUCTION_EXECUTION_FORMAT = _("{} 执行第{}条指令 [{}]")
MSG_DEBUG_INSTRUCTION_START_FORMAT = _("{} 开始调试第{}条指令 [{}]")
MSG_ERROR_SKIP = _("执行错误跳过")
MSG_EXECUTION_ERROR = _("执行错误")
MSG_VIDEO_PROCESSING_WAIT = _("录屏数据处理中，可能时间较长，请稍等")
