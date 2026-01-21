from typing import Optional, Union

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


class AstronAgentCreate(BaseModel):
    """创建星辰Agent请求模型"""

    api_key: str = Field(..., description="API Key", min_length=1, max_length=100)
    api_secret: str = Field(..., description="API Secret", min_length=1, max_length=100)
    app_id: Optional[str] = Field(None, description="应用ID", min_length=1, max_length=100)
    name: str = Field(..., description="用户名称", min_length=1, max_length=100)


class AstronAgentDelete(BaseModel):
    """删除星辰Agent请求模型"""

    id: Union[int, str] = Field(..., description="星辰Agent ID")


class AstronAgentUpdate(BaseModel):
    """更新星辰Agent请求模型"""

    id: Union[int, str] = Field(..., description="星辰Agent ID")
    name: Optional[str] = Field(None, description="用户名称", min_length=1, max_length=100)
    app_id: Optional[str] = Field(None, description="应用ID", min_length=1, max_length=100)
    api_key: Optional[str] = Field(None, description="API Key", min_length=1, max_length=100)
    api_secret: Optional[str] = Field(None, description="API Secret", min_length=1, max_length=100)
