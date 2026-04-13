import uuid
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel

from astronverse.picker import PickerType, PickerAction, RecordAction, SmartComponentAction


class ResponseKey(Enum):
    """引擎响应消息的key值"""

    SUCCESS = "success"
    ERROR = "error"
    CANCEL = "cancel"
    PING = "ping"


class PickMode(Enum):
    WEB_PICK = "WebPick"
    NORMAL = "Normal"


class RequestMessage(BaseModel):
    pick_type: PickerType = PickerType.ELEMENT
    pick_action: Optional[PickerAction] = None
    record_action: Optional[RecordAction] = None
    smart_component_action: Optional[SmartComponentAction] = None
    data: Any = None
    pick_mode: str = None
    ext_data: dict = None


class ResponseMessage(BaseModel):
    err_msg: str = ""
    data: str = ""
    key: Optional[str] = None

    @classmethod
    def create_response(cls, key: ResponseKey, data: str = "", err_msg: str = ""):
        """创建响应消息"""
        return cls(
            key=key.value,
            data=data,
            err_msg=err_msg,
        )


class PushKey(Enum):
    """引擎推送消息的key值"""

    RECORD_START = "record_start"
    RECORD_PAUSE = "record_pause"
    RECORD_AUTOMIC_CHOICE = "record_automic_start"
    RECORD_AUTOMIC_DRAW_END = "record_automic_draw_end"


class RequestPush(BaseModel):
    message_type: str = "push"
    message_id: str
    key: str
    data: Any = None
    err_msg: str = ""

    @classmethod
    def create_push(cls, key: PushKey, data: str = "", err_msg: str = ""):
        """创建推送消息（带ID）"""
        return cls(
            key=key.value,
            data=data,
            err_msg=err_msg,
            message_id=str(uuid.uuid4()),  # 生成唯一ID
        )


class ResponsePush(BaseModel):
    """推送消息确认模型 - 专门用于确认推送消息"""

    message_type: str = "ack"
    reply_to: str
    data: Any = None
    err_msg: str = ""
