"""code 相关类型定义"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ControlInfo:
    """窗口控件信息"""

    name: str
    classname: str
    position: Any
    handler: Any
    client_position: Any = None
