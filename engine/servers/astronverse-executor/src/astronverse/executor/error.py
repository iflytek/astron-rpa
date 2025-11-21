import re
from functools import wraps
from astronverse.baseline.error.error import ErrorCode, BaseException, BizCode
from astronverse.baseline.i18n.i18n import _

BaseException = BaseException

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
MSG_DOWNLOAD_FORMAT = _("{}动态下载中...")
MSG_DOWNLOAD_SUCCESS_FORMAT = _("{}下载完成")


def python_base_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NameError as e:
            error_str = str(e)
            name_error_translations = [
                (r"name '(.+)' is not defined", "未定义的名称 '{}'"),
            ]
            for pattern, translation in name_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except TypeError as e:
            type_error_translations = [
                (
                    r"unsupported operand type\(s\) for ([^:]+): '(.+)' and '(.+)'",
                    "对于运算符 '{}' 不支持的操作数类型: '{}' 和 '{}'",
                ),
                (
                    r'can only concatenate ([^(]+) \(not \"([^"]+)\"\) to ([^(]+)',
                    "只能将 '{}' (而不是 '{}') 与 '{}' 连接",
                ),
                (r"'(.+)' object is not subscriptable", "'{}' 对象不支持索引操作"),
                (r"'(.+)' object is not callable", "'{}' 对象不可调用"),
                (r"'(.+)' object is not iterable", "'{}' 对象不是可迭代的"),
                (r"([^()]+)\(\) missing (\d+) required positional argument(s)?", "函数 '{}' 缺少 {} 个位置参数"),
                (
                    r"([^()]+)\(\) takes (\d+) positional argument(?:s)? but (\d+) (was|were) given",
                    "函数 '{}' 需要 {} 个位置参数，但给出了 {} 个",
                ),
                (r"([^()]+)\(\) got an unexpected keyword argument '(.+)'", "函数 '{}' 收到未预期的关键字参数 '{}'"),
                (r"unhashable type: '(.+)'", "无法哈希的类型: '{}'"),
            ]

            error_str = str(e)
            for pattern, translation in type_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except IndexError as e:
            index_error_translations = [
                (r"list index out of range", "列表索引超出范围"),
                (r"tuple index out of range", "元组索引超出范围"),
                (r"string index out of range", "字符串索引超出范围"),
            ]
            error_str = str(e)
            for pattern, translation in index_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except KeyError as e:
            key_error_translations = [
                (r"'(.+)'", "字典中不存在键 '{}'"),
            ]
            error_str = str(e)
            for pattern, translation in key_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except ValueError as e:
            value_error_translations = [
                (r"invalid literal for int\(\) with base 10: '(.+)'", "无效的字面量 '{}' 不能转换为整数"),
                (r"could not convert string to float: '(.+)'", "无效的字面量 '{}' 不能转换为浮点数"),
            ]
            error_str = str(e)
            for pattern, translation in value_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except AttributeError as e:
            attribute_error_translations = [
                (r"(.+) object has no attribute '(.+)'", "{} 对象没有属性 '{}'"),
            ]
            error_str = str(e)
            for pattern, translation in attribute_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except ZeroDivisionError as e:
            error_str = "除零错误,除数不能为零"
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except ImportError as e:
            import_error_translations = [
                (r"cannot import name '(.+)' from '(.+)'", "无法从 '{}' 导入名称 '{}'"),
                (r"No module named '(.+)'", "没有名为 '{}' 的模块"),
            ]
            error_str = str(e)
            for pattern, translation in import_error_translations:
                match = re.search(pattern, error_str)
                if match:
                    error_str = translation.format(*match.groups())
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except SyntaxError as e:
            error_str = f"语法错误, 文件名: '{e.filename}', 行号: {e.lineno}, 列号: {e.offset}, 代码行: {repr(e.text)}"
            raise BaseException(GENERAL_ERROR_FORMAT.format(error_str), error_str) from e
        except Exception as e:
            raise e

    return wrapper
