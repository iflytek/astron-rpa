"""Enterprise module initialization"""

from enum import Enum


class ReportLevelType(Enum):
    """Report level types"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
