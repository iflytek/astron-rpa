from enum import Enum


class EmailServerType(Enum):
    OTHER = "other"
    NETEASE_126 = "126"
    NETEASE_163 = "163"
    QQ = "qq"
    IFLYTEK = "iflytek"


class EmailReceiverType(Enum):
    POP3 = "pop3"
    IMAP = "imap"


class EmailSeenType(Enum):
    ALL = "ALL"
    UNSEEN = "Unseen"
