"""Public enums and model/type definitions for astronverse.ai package."""

from enum import Enum


class InputType(Enum):
    """Supported input payload types."""

    FILE = "file"
    TEXT = "text"


class DifyFileTypes(Enum):
    """File type categories supported by Dify uploads."""

    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CUSTOM = "custom"


class JobWebsitesTypes(Enum):
    """Supported job website code identifiers."""

    BOSS = "boss"
    LP = "liepin"
    ZL = "zhilian"


class RatingSystemTypes(Enum):
    """Rating system strategy types."""

    DEFAULT = "default"
    CUSTOM = "custom"


class LLMModelTypes(Enum):
    DS_CHAT = "deepseek-chat"
    DS_REASONER = "deepseek-reasoner"  # 先顶一下
    CUSTOM_MODEL = "custom"
