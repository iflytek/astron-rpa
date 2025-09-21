from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum

class ResCode(Enum):
    ERR = "5001"
    SUCCESS = "0000"

class StandardResponse(BaseModel):
    """标准响应模型"""
    code: ResCode = Field(ResCode.SUCCESS, description="响应码")
    msg: str = Field("", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")