from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

CODE_INNER: ErrorCode = ErrorCode(BizCode.LocalErr, _("内部错误"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("{} 参数异常"))
TIMEOUT: ErrorCode = ErrorCode(BizCode.LocalErr, "拾取超时")
TIMEOUT_LAG: ErrorCode = ErrorCode(BizCode.LocalErr, "拾取卡顿超过15s，请退出编辑器后重新进入")
NO_WEB_INFO: ErrorCode = ErrorCode(BizCode.LocalErr, "缺乏元素的web信息")

BROWSER_EXTENSION_INSTALL_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件通信出错，请重试"))

BROWSER_EXTENSION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("浏览器插件错误: {}"))

WEB_GET_ElE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("网页元素查找失败 {}"))

WEB_EXEC_ElE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("脚本执行错误: {}"))

# Picker 特定错误
CUR_RECT_NOT_INITIALIZED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("cur_rect 未初始化"))
MOUSE_POSITION_OUT_OF_RANGE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("鼠标点位不在当前元素范围内"))
PROCESSOR_INHERITANCE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("处理器必须继承自HTMLProcessor"))
CANNOT_REMOVE_DEFAULT_PROCESSOR_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("不能移除默认处理器"))
CONDITION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("条件异常，请输入正确的条件！"))

# UIA/MSAA 拾取错误
TAG_NAME_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("tag_name 为空，无法唯一识别元素"))
SIMILAR_ELEMENT_NOT_FOUND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("找不到相似元素"))
MSAA_SIMILAR_NOT_SUPPORTED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("msaa暂不支持相似元素"))

# 智能组件错误
SMART_COMPONENT_SIMILAR_NOT_IMPLEMENTED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("智能组件的相似拾取暂未实现"))
SMART_COMPONENT_BATCH_NOT_IMPLEMENTED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("智能组件的批量抓取暂未实现"))
PROCESSOR_NOT_SET_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未设置当前处理器"))
PROCESSOR_NOT_FOUND_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("未找到名为 '{}' 的处理器"))

# 录制器错误
PICKER_CONVERTER_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("拾取转换器出错，请退出项目重新开始"))
PICKER_CONVERTER_MISSING_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("缺少拾取转换器"))

# 表格过滤错误 - 动态消息
COLUMN_DATA_MISSING_PARAM_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("第{}列数据处理缺少参数"))

