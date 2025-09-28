from enum import Enum


class VerifyCodeConfig:
    url = "http://127.0.0.1:8003/api/rpa-ai-service/jfbym/customApi"


class PictureCodeType(Enum):
    GENERAL1234 = "10110"
    GENERAL5678 = "10111"
    GENERAL1234_PLUS = "10211"


class HintPosition(Enum):
    BOTTOM = "bottom"
    TOP = "top"


class ElementGetAttributeTypeFlag(Enum):
    GetText = "getText"
    GetHtml = "getHtml"
    GetValue = "getValue"
    GetLink = "getLink"
    GetAttribute = "getAttribute"
    GetPosition = "getPosition"
    GetSelection = "getSelection"
