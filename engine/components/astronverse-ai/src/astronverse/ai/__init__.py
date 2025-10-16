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
    """LLM model identifiers used across API calls."""

    DS_CHAT = "deepseek-v3-0324"
    DS_REASONER = "claude-4-sonnet"  # 先顶一下
