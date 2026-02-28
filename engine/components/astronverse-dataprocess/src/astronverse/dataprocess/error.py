from astronverse.baseline.error.error import *
from astronverse.baseline.i18n.i18n import _

BizException = BizException

VALUE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入数据类型有误，无法设置为变量: {}"))
INVALID_REGEX_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的正则表达式有误: {}"))
INVALID_NUMBER_RANGE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的数字范围有误: {}"))
INVALID_NUMBER_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的数字格式有误: {}"))
INVALID_LIST_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的列表格式有误: {}"))
INVALID_DICT_FORMAT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的字典格式有误: {}"))
INVALID_INDEX_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的索引值有误: {}"))
INVALID_MATH_EXPRESSION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入的数学表达式有误: {}"))

# 字典操作错误
DICT_KEY_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("字典中不存在该键"))

# 数据转换错误
DATA_CONVERT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("数据类型不支持强转str"))
INVALID_CONVERT_STRING: ErrorCode = ErrorCode(BizCode.LocalErr, _("请输入正确的待转换目标字符串"))

# 数学运算错误
UNSUPPORTED_NUMBER_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的 number_type"))
UNSUPPORTED_OPERATION_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的加减类型"))

# 时间处理错误
UNSUPPORTED_TIMESTAMP_UNIT: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的时间戳单位"))
UNSUPPORTED_TIMESTAMP_LENGTH: ErrorCode = ErrorCode(BizCode.LocalErr, _("时间戳长度不支持"))
UNSUPPORTED_TIME_UNIT: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的时间单位"))

# 字符串处理错误
STRING_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("目标文本或补充文本不能为空"))
INVALID_LENGTH_INPUT: ErrorCode = ErrorCode(BizCode.LocalErr, _("长度输入不合法,请提供整数类型数据"))
STRING_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到指定字符串"))
UNSUPPORTED_CASE_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的大小写转换类型"))

# 列表操作错误
LIST_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("列表不能为空"))
LIST_INDEX_OUT_OF_RANGE: ErrorCode = ErrorCode(BizCode.LocalErr, _("数组索引值超出范围"))
INVALID_INDEX_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("请提供有效的整数类型索引"))
INVALID_LIST_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("用户自定义列表类型错误"))
ELEMENT_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("列表中不存在该对象"))
INCONSISTENT_LIST_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("请提供元素数据类型一致的列表进行排序"))
