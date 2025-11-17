from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""

    phone: str = Field(..., description="用户手机号", min_length=1, max_length=20)


class UserRegisterResponse(BaseModel):
    """用户注册响应模型"""

    user_id: str = Field(..., description="用户ID")
    api_key: str = Field(..., description="API Key")
    account: str = Field(..., description="账号")
    password: str = Field(..., description="密码")
    url: str = Field(..., description="下载链接")
