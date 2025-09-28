from dataclasses import dataclass
from enum import Enum
from typing import Any


class WindowSizeType(Enum):
    CUSTOM = "custom"
    MAX = "max"
    MIN = "min"


class WindowExistType(Enum):
    EXIST = "exist"
    NOT_EXIST = "not_exist"


@dataclass
class ControlInfo:
    name: str
    classname: str
    position: Any
    handler: Any


@dataclass
class WalkControlInfo:
    name: str
    classname: str
    position: Any
    control: Any
    depth: int
    control_type: Any
    control_type_name: str
