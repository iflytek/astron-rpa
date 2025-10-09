from enum import Enum


class KeyboardType(Enum):
    NORMAL = "normal"  # 普通输入
    DRIVER = "driver"  # 驱动输入
    CLIP = "clip"  # 剪贴板输入
    GBLID = "gblid"  # 虚拟键盘输入


class BtnType(Enum):  # 按键类型
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


class BtnModel(Enum):  # 按键模式
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    DOWN = "down"
    UP = "up"


class KeyModel(Enum):  # 按键模式
    CLICK = "click"
    DOWN = "down"
    UP = "up"


class ScrollType(Enum):
    TIME = "time"
    PX = "px"


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    # LEFT = "left"
    # RIGHT = "right"


class ControlType(Enum):
    EMPTY = "none"
    CTRL = "ctrl"
    ALT = "alt"
    SHIFT = "shift"
    WIN = "win"
    SPACE = "space"


class WindowType(Enum):
    FULL_SCREEN = "fullscreen"
    ACTIVE_WINDOW = "active_window"


class Speed(Enum):
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


class MoveType(Enum):
    LINEAR = "linear"
    SIMULATION = "simulation"
    TELEPORTATION = "teleportation"


class Simulate_flag(Enum):
    YES = "yes"
    NO = "no"
