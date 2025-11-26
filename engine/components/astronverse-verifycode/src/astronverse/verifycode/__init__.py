from enum import Enum
from astronverse.actionlib.atomic import atomicMg


class VerifyCodeConfig:
    url = "http://127.0.0.1:{}/api/rpa-ai-service/jfbym/customApi".format(
        atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
    )


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
