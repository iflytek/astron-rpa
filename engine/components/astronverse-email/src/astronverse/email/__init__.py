"""
电子邮件相关的枚举类型定义。
"""

from enum import Enum


class EmailServerType(Enum):
    """电子邮件服务器类型枚举。"""

    OTHER = "other"
    NETEASE_126 = "126"
    NETEASE_163 = "163"
    QQ = "qq"
    IFLYTEK = "iflytek"


class EmailReceiverType(Enum):
    """电子邮件接收协议类型枚举。"""

    POP3 = "pop3"
    IMAP = "imap"


class EmailSeenType(Enum):
    """邮件已读状态类型枚举。"""

    ALL = "ALL"
    UNSEEN = "Unseen"
