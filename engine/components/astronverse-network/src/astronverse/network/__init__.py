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
    ALL = "all"
    FILE = "file"
    FOLDER = "folder"


class FileType(Enum):
    FILE = "file"
    FOLDER = "folder"


class StateType(Enum):
    CREATE = "create"
    ERROR = "error"


class SaveType(Enum):
    YES = "yes"
    NO = "no"


class FileExistenceType(Enum):
    RENAME = "rename"
    OVERWRITE = "overwrite"
    CANCEL = "cancel"
