from enum import Enum


class ReportLevelType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RequestType(Enum):
    POST = "post"
    GET = "get"
    CONNECT = "connect"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    OPTIONS = "options"
    HEAD = "head"
    TRACE = "trace"


class ListType(Enum):
    ALL = "all"  # 获取当前工作目录下全部文件及子文件夹
    FILE = "file"  # 获取全部文件
    FOLDER = "folder"  # 获取全部文件夹


class FileType(Enum):
    FILE = "file"  # 获取全部文件
    FOLDER = "folder"  # 获取全部文件夹


class StateType(Enum):
    CREATE = "create"  # 新建
    ERROR = "error"  # 提示并报错


class SaveType(Enum):
    YES = "yes"
    NO = "no"


class FileExistenceType(Enum):
    RENAME = "rename"
    OVERWRITE = "overwrite"
    CANCEL = "cancel"
