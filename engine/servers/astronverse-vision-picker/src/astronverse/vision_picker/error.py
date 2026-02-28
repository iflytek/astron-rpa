from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 图像处理相关错误
IMAGE_NOT_PROVIDED: ErrorCode = ErrorCode(BizCode.LocalErr, _("未提供图像"))
IMAGE_SAVE_PATH_REQUIRED: ErrorCode = ErrorCode(BizCode.LocalErr, _("必须提供保存路径"))
IMAGE_PATH_INVALID: ErrorCode = ErrorCode(BizCode.LocalErr, _("路径无效或不存在: {}"))
IMAGE_SAVE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("保存图像时发生错误: {}"))

# 平台和系统相关错误
PLATFORM_NOT_SUPPORTED: ErrorCode = ErrorCode(BizCode.LocalErr, _("平台不支持: {}"))
DESKTOP_SCREENSHOT_NOT_EXIST: ErrorCode = ErrorCode(BizCode.LocalErr, _("桌面截图不存在"))

# 拾取相关错误
PICK_STATUS_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("执行状态有误"))
TARGET_ACQUIRE_FAILED: ErrorCode = ErrorCode(BizCode.LocalErr, _("目标获取失败"))
TARGET_COORDINATE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("目标元素坐标为空"))

# 服务器相关错误
SERVER_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("服务器错误: {}"))
