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


class OutputType(Enum):
    """Output format types."""

    TEXT = "text"
    MINDMAP = "mindmap"


class SaveType(Enum):
    """Document save types."""

    SAVE = "保存"
    SAVE_AS = "另存为"


class TemplateType(Enum):
    """Document template types."""

    GENERAL = "通用公文"
    ACADEMIC = "学术论文"
    CONTRACT = "合同协议"


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


class LLMMultiModalModelTypes(Enum):
    QWEN_IMAGE_2512 = "xopqwentti20b"
    KOLORS = "xskolorss2b6"
    STABLEDIFFUSION_XL_BASE_1 = "xssdxl"


class VLLMModelTypes(Enum):
    QWEN_2_5_VL_32B_Instruct = "xqwen2d5s32bvl"
    QWEN_3_VL_32B_Instruct = "xop3qwen32bvl"
    DeepSeek_OCR = "xopdeepseekocr"


class AspectRatio(Enum):
    """Image aspect ratio options."""

    RATIO_1_1 = "1:1"
    RATIO_3_4 = "3:4"
    RATIO_4_3 = "4:3"
    RATIO_4_7 = "4:7"
    RATIO_7_4 = "7:4"
    RATIO_9_16 = "9:16"
    RATIO_16_9 = "16:9"


class ImageSize(Enum):
    """Image size options."""

    SIZE_1024P = "1024p"
    SIZE_720P = "720p"
