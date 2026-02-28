from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# 文档路径错误
DOCUMENT_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word文件路径有误，请输入正确的路径: {}"))
PATH_NOT_FOUND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("路径未找到"))
PATH_NOT_INPUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("没有输入路径，请检查输入的word路径是否正确"))
IMAGE_PATH_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("图片路径错误"))

# 文档操作错误
DOCUMENT_NOT_EXIST_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("文档不存在，请先打开文档"))
DOCUMENT_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("文档为空"))
DOCUMENT_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word文件读取失败，请检查文件是否损坏: {}"))
DOCUMENT_SAVE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文档保存失败: {}"))
DOCUMENT_INSERT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("插入失败，请检查文档是否打开"))

# 内容操作错误
CONTENT_INPUT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("请正确输入起始行号或段落号"))
CONTENT_VALUE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("请输入正确的数值"))
CONTENT_NOT_EXIST_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("内容不存在"))
CONTENT_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("内容为空"))

# 表格和文件错误
TABLE_NOT_EXIST_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("表格不存在: {}"))
FILENAME_ALREADY_EXISTS_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件名已存在: {}"))

# 剪贴板错误
CLIPBOARD_PASTE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("请检查剪贴板是否存在内容"))

# Word 初始化错误
WORD_INITIALIZATION_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("Word初始化失败，请检查Word是否安装正确: {}"))
WPS_INIT_FAILED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("WPS初始化失败"))
WORD_FALLBACK_FAILED_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("兜底失败，请尝试手动删除 %LOCALAPPDATA%\\Temp\\gen_py 目录再运行"))
WORD_REGISTRY_NOT_FOUND_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("未检测到wps和office注册表信息"))
