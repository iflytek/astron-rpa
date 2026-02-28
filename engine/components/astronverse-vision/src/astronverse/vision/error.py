from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 参数错误
INPUT_DATA_NONE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("input_data 不能为空"))
SAVE_PATH_REQUIRED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("必须提供 save_path 参数以保存图像"))
SPECIFIC_POSITION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未指定点击位置，请检查参数设置"))

# 文件路径错误
SAVE_PATH_INVALID_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("路径无效或不存在: {}"))
SAVE_IMAGE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("保存图像时发生错误: {}"))

# CV 匹配错误
CV_MATCH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未匹配到目标元素，请检查当前界面或降低匹配相似度后重试"))
MATCH_RESULT_INVALID_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("match.process_image 未返回有效的 (out_img, match_box) 元组"))
COORDINATE_CONVERSION_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("坐标转换失败，请检查锚点是否已正确设置，或重新拾取新的图像元素"))
TARGET_EXISTS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("当前界面目标元素不存在"))

# 鼠标操作错误
MOUSE_CLICK_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("鼠标点击失败"))
MOUSE_HOVER_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("鼠标悬停失败"))

# 输入错误
CV_INPUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("输入文本失败"))
