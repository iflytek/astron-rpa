from sqlalchemy import Column, String, DateTime, func, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.workflow import ExecutionStatus
import json

class Workflow(Base):
    """工作流数据库模型"""
    __tablename__ = "openai_workflows"

    project_id = Column(String(100), primary_key=True, index=True)  # 项目ID作为主键
    name = Column(String(100), index=True, nullable=False)
    english_name = Column(String(100), nullable=True)  # 翻译后的英文名称
    description = Column(String(500), nullable=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    status = Column(Integer, default=1, nullable=False)
    parameters = Column(Text, nullable=True)  # 存储JSON字符串格式的参数
    user_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """将Workflow对象转换为可序列化的字典"""
        # 处理parameters字段的反序列化
        parameters_dict = None
        if self.parameters:
            try:
                parameters_dict = json.loads(self.parameters)
            except (json.JSONDecodeError, TypeError):
                parameters_dict = None
        
        workflow_dict = {
            "project_id": self.project_id,
            "name": self.name,
            "english_name": self.english_name,
            "description": self.description,
            "version": self.version,
            "status": self.status,
            "parameters": parameters_dict,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        return workflow_dict

    def get_parameters_as_dict(self):
        """将parameters字段从JSON字符串转换为字典"""
        if self.parameters:
            try:
                return json.loads(self.parameters)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def set_parameters_from_dict(self, params_dict):
        """将字典转换为JSON字符串存储到parameters字段"""
        if params_dict:
            self.parameters = json.dumps(params_dict, ensure_ascii=False)
        else:
            self.parameters = None

class Execution(Base):
    """工作流执行记录数据库模型"""
    __tablename__ = "openai_executions"

    id = Column(String(36), primary_key=True, index=True)  # UUID格式
    project_id = Column(String(100), nullable=False, index=True)
    status = Column(String(20), default="PENDING", nullable=False)
    parameters = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    user_id = Column(String(50), nullable=False, index=True)
    exec_position = Column(String(50), default="EXECUTOR", nullable=False)  # 执行位置
    start_time = Column(DateTime, default=func.now(), nullable=False)
    end_time = Column(DateTime, nullable=True)

    def to_dict(self):
        """将Execution对象转换为可序列化的字典"""
        # 处理parameters和result字段的反序列化
        parameters_dict = None
        if self.parameters:
            try:
                parameters_dict = json.loads(self.parameters)
            except (json.JSONDecodeError, TypeError):
                parameters_dict = None
        
        result_dict = None
        if self.result:
            try:
                result_dict = json.loads(self.result)
            except (json.JSONDecodeError, TypeError):
                result_dict = None
        
        execution_dict = {
            "id": self.id,
            "project_id": self.project_id,
            "status": self.status,
            "parameters": parameters_dict,
            "result": result_dict,
            "error": self.error,
            "exec_position": self.exec_position,
            "user_id": self.user_id,
            "start_time": self.start_time,
            "end_time": self.end_time
        }
        return execution_dict

    def get_parameters_as_dict(self):
        """将parameters字段从JSON字符串转换为字典"""
        if self.parameters:
            try:
                return json.loads(self.parameters)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def get_result_as_dict(self):
        """将result字段从JSON字符串转换为字典"""
        if self.result:
            try:
                return json.loads(self.result)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def set_parameters_from_dict(self, params_dict):
        """将字典转换为JSON字符串存储到parameters字段"""
        if params_dict:
            self.parameters = json.dumps(params_dict, ensure_ascii=False)
        else:
            self.parameters = None

    def set_result_from_dict(self, result_dict):
        """将字典转换为JSON字符串存储到result字段"""
        if result_dict:
            self.result = json.dumps(result_dict, ensure_ascii=False)
        else:
            self.result = None
