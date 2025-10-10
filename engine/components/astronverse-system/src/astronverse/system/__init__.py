from enum import Enum


class ReportLevelType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ExistType(Enum):
    EXIST = "exist"  # 存在
    NOT_EXIST = "not_exist"  # 不存在


class OptionType(Enum):
    OVERWRITE = "overwrite"  # 覆盖
    SKIP = "skip"  # 跳过
    GENERATE = "generate"  # 生成副本


class DeleteType(Enum):
    DELETE = "delete"  # 彻底删除
    TRASH = "trash"  # 移入回收站


class WriteType(Enum):
    OVERWRITE = "overwrite"  # 覆盖写入
    APPEND = "append"  # 追加写入


class EncodeType(Enum):
    DEFAULT = "default"
    ANSI = "ansi"
    UTF8 = "utf-8"
    UTF16 = "utf-16"
    UTF_16_BE = "utf-16 be"
    GBK = "gbk"
    GB2312 = "gb2312"
    GB18030 = "gb18030"


class StateType(Enum):
    CREATE = "create"  # 新建
    ERROR = "error"  # 提示并报错


class ReadType(Enum):
    ALL = "all"  # 读取全部内容
    List = "list"  # 读取到列表中
    BYTE = "byte"  # 二进制方式


class SearchType(Enum):
    EXACT = "exact"  # 精确匹配
    FUZZY = "fuzzy"  # 模糊匹配
    REGEX = "regex"  # 正则表达式匹配


class TraverseType(Enum):
    YES = "yes"  # 遍历子文件夹
    NO = "no"  # 不遍历子文件夹


class StatusType(Enum):
    CREATED = "created"  # 被创建
    DELETED = "deleted"  # 被删除


class InfoType(Enum):
    ALL = "all"
    ABS_PATH = "abs_path"
    ROOT = "root"
    DIRECTORY = "directory"
    SIZE = "size"
    NAME_EXT = "name_ext"
    NAME = "name"
    EXTENSION = "extension"
    C_TIME = "c_time"
    M_TIME = "m_time"


class OutputType(Enum):
    LIST = "list"  # 列表输出
    EXCEL = "excel"  # 表格文档


class SortMethod(Enum):
    NONE = "none"  # 不排序
    CTIME = "ctime"  # 按创建时间排序
    MTIME = "mtime"  # 按修改时间排序


class SortType(Enum):
    ASCENDING = "ascending"  # 升序
    DESCENDING = "descending"  # 降序


class ContentType(Enum):
    MSG = "msg"  # 文本信息
    HTML = "html"  # HTML格式文本
    FILE = "file"  # 文件
    FOLDER = "folder"  # 文件夹


class ScreenType(Enum):
    FULL = "full"  # 全屏
    REGION = "region"  # 区域


class RunType(Enum):
    CONTINUE = "continue"
    COMPLETE = "complete"


class CmdType(Enum):
    NORMAL = "normal"  # 正常运行
    ADMIN = "admin"  # 以管理员身份运行


class PidType(Enum):
    ALL = "all"  # 获取所有符合的PID
    ONE = "one"  # 获取匹配的第一个应用程序的PID


class TerminationType(Enum):
    PID = "pid"
    NAME = "name"


class DirType(Enum):
    SOURCE = "source"  # 源路径
    NEW = "new"  # 新路径


class SaveType(Enum):
    DELETE = "delete"
    SAVE = "save"


class PwdType(Enum):
    RSA = "rsa"  # 密钥
    PASSWORD = "password"  # 密码


class BatchType(Enum):
    BATCH = "batch"
    SINGLE = "single"


class PrinterType(Enum):
    CUSTOM = "custom"
    DEFAULT = "default"


class OrientationType(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class FileType(Enum):
    PICTURE = "picture"
    WORD = "word"
    PDF = "pdf"
    EXCEL = "excel"


class MarginType(Enum):
    CUSTOM = "custom"
    DEFAULT = "default"


class PaperType(Enum):
    A3 = "A3"
    A4 = "A4"
    LA4 = "LA4"
    A5 = "A5"
    B4 = "B4"
    B5 = "B5"
    C_SHEET = "C_SHEET"
    D_SHEET = "D_SHEET"
    CUSTOM = "CUSTOM"


class FileFolderType(Enum):
    FILE = "file"
    FOLDER = "folder"
    BOTH = "both"  # 文件和文件夹一起压缩
