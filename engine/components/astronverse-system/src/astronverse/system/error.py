from astronverse.baseline.error.error import BizException, BizCode, ErrorCode
from astronverse.baseline.i18n.i18n import _

BizException = BizException

# 通用错误（动态消息）
ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("错误: {}"))
PARAM_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("参数错误: {}"))

# 剪切板相关错误
MSG_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("请重新输入待复制内容"))
MSG_EMPTY_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("内容为空: {}"))
CONTENT_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取剪切板内容类型错误"))

# 文件相关错误（固定消息）
FILE_LIST_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("获取文件夹下文件列表失败"))

# 文件相关错误（动态消息）
FILE_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件路径错误: {}"))
SAVE_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("保存格式错误: {}"))
FILE_READ_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件读取失败: {}"))
FILE_WRITE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件写入失败: {}"))
FILE_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件拓展名缺失: {}"))
FILE_DELETE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件删除失败: {}"))
PermissionError_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件被占用: {}"))

# 文件夹相关错误（动态消息）
FOLDER_PATH_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件夹路径错误: {}"))
FOLDER_DELETE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件夹删除失败: {}"))

# 文件格式相关错误（动态消息）
READ_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件格式不支持读取: {}"))
RENAME_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("重命名错误: {}"))
ENCODE_TYPE_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("文件编码格式冲突: {}"))

# 系统操作相关错误（动态消息）
SCREENSHOT_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("截图失败: {}"))
SCREENLOCK_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("屏幕锁定失败: {}"))
CMD_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("CMD命令执行失败: {}"))

# 压缩相关错误
UNSUPPORTED_COMPRESS_TYPE: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持的压缩类型"))
COMPRESS_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("压缩失败: {}"))
DECOMPRESS_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("解压缩失败: {}"))

# 打印机相关错误（固定消息）
PRINT_FILE_EMPTY: ErrorCode = ErrorCode(BizCode.LocalErr, _("待打印文件为空"))
PRINT_FILE_TYPE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("不支持打印的文件类型"))
REGISTRY_NOT_FOUND: ErrorCode = ErrorCode(BizCode.LocalErr, _("未检测到程序的注册表信息"))
SOFTWARE_OPEN_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法打开软件"))
PAGE_RANGE_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("页码范围错误"))
PRINTER_CONTEXT_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("无法创建打印设备上下文"))
GENPY_REBUILD_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("兜底失败，请尝试手动删除 %LOCALAPPDATA%\\Temp\\gen_py 目录再运行！"))

# 打印机相关错误（动态消息）
PRINTER_NOT_FOUND_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("未发现打印机: {}"))
PRINTER_NOT_SUPPORTED_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("打印机不支持打印: {}"))

# 进程相关错误（固定消息）
COMMAND_EMPTY_ERROR: ErrorCode = ErrorCode(BizCode.LocalErr, _("命令不能为空"))

# 进程相关错误（动态消息）
COMMAND_EXEC_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("执行命令失败: {}"))
PROCESS_KILL_ERROR_FORMAT: ErrorCode = ErrorCode(BizCode.LocalErr, _("终止进程失败: {}"))
