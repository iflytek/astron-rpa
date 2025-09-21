from datetime import datetime
from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field

class ApiKeyCreate(BaseModel):
    """创建API Key请求模型"""
    name: str = Field(..., description="API Key名称", min_length=1, max_length=100)

class ApiKeyDelete(BaseModel):
    """删除API Key请求模型"""
    id: Union[int, str] = Field(..., description="API Key ID")


# class ApiKeyResponse(BaseModel):
#     """API Key响应模型"""
#     id: int = Field(..., description="API Key ID")
#     api_key: str = Field(..., description="API Key 值（带掩码）")
#     name: str = Field(..., description="API Key名称")
#     createTime: datetime = Field(..., description="创建时间")
#     recentTime: datetime = Field(..., description="最近更新时间")

#     model_config = {"from_attributes": True}
