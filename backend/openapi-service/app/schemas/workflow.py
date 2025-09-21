from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


class WorkflowStatus(int, Enum):
    ACTIVE = 1
    INACTIVE = 0


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WorkflowBase(BaseModel):
    """工作流基本数据模型"""
    project_id: Union[str,int] = Field(..., description="项目ID")
    name: str = Field(..., description="工作流名称", min_length=1, max_length=100)
    english_name: Optional[str] = Field(None, description="工作流英文名称", max_length=100)
    description: Optional[str] = Field(None, description="工作流描述", max_length=500)
    version: str = Field("1.0.0", description="工作流版本号", min_length=1, max_length=20)
    status: int = Field(1, description="工作流状态")
    parameters: Optional[str] = Field(None, description="工作流参数(JSON格式)")

class WorkflowResponse(WorkflowBase):
    """工作流响应模型"""
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = {"from_attributes": True}


class WorkflowListResponse(BaseModel):
    """工作流列表响应模型"""
    data: List[WorkflowResponse] = Field(..., description="工作流列表")


class ExecutionCreate(BaseModel):
    """创建工作流执行记录请求模型"""
    project_id: str = Field(..., description="项目ID")
    params: Optional[Dict[str, Any]] = Field(None, description="执行参数")
    exec_position: str = Field("EXECUTOR", description="执行位置")


class ExecutionResponse(BaseModel):
    """执行记录响应模型"""
    id: str = Field(..., description="执行记录ID")
    project_id: str = Field(..., description="项目ID")
    status: str = Field(..., description="执行状态")
    parameters: Optional[Dict[str, Any]] = Field(None, description="执行参数")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    exec_position: str = Field(..., description="执行位置")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")

    model_config = {"from_attributes": True}
    

