from enum import Enum


class KeyboardType(Enum):
    NORMAL = "normal"
    DRIVER = "driver"
    CLIP = "clip"
    GBLID = "gblid"


class BtnType(Enum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


class BtnModel(Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    DOWN = "down"
    UP = "up"


class KeyModel(Enum):
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
