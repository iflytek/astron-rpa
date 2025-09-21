from enum import Enum


class InputType(Enum):
    FILE = "file"
    TEXT = "text"


class DifyFileTypes(Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CUSTOM = "custom"


class JobWebsitesTypes(Enum):
    BOSS = "boss"
    LP = "liepin"
    ZL = "zhilian"


class RatingSystemTypes(Enum):
    DEFAULT = "default"
    CUSTOM = "custom"


class LLMModelTypes(Enum):
    DS_CHAT = "deepseek-v3-0324"
    DS_REASONER = "claude-4-sonnet"  # 先顶一下
