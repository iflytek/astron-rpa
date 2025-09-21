"""策略相关类型定义模块 - 仅包含数据类型定义"""

import dataclasses
import platform
import sys
from typing import Any

from .. import APP, PickerDomain, Point


@dataclasses.dataclass
class StrategyEnv:
    """策略环境类"""

    os_name: str = platform.system()
    os_version: str = platform.version()
    os_arch: str = platform.machine()
    # 更加详细的win版本
    win_version: str = sys.getwindowsversion() if platform.system() == "Windows" else ""


@dataclasses.dataclass
class StrategySvc:
    """策略上下文"""

    # 内部收集
    app: APP = None
    process_id: int = ""
    last_point: Point = None
    start_control: Any = None

    # 外部输入
    data: dict = None

    # 处理域
    domain: PickerDomain = PickerDomain.UIA
