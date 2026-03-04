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
    DEEPSEEK_V3_2 = "xopdeepseekv32"
    KIMI_K2_5 = "xopkimik25"
    KIMI_K2_INSTRUCT = "xopkimik2blins"
    QWEN_3_5_397B = "xopqwen35397b"
    QWEN3_235B = "xop3qwen235b"
    QWEN3_30B = "xop3qwen30b2507"
    MINIMAX_M2_5 = "xminimaxm25"
    MINIMAX_M2_1 = "xminimaxm2"
    GLM_5 = "xopglm5"
    GLM_4_7_FLASH = "xopglmv47flash"
    CUSTOM_MODEL = "custom"
