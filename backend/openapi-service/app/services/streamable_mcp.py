import os
import json
from pathlib import Path
from mcp.server.fastmcp.tools import Tool

from app.logger import get_logger
from typing import Dict, List, Optional, Tuple
import mcp.types as types

logger = get_logger(__name__)


class ToolsConfig:
    """工具配置管理器"""

    def __init__(self):
        self.redis = None

    async def _ensure_redis_connection(self):
        """确保Redis连接已初始化"""
        if self.redis is None:
            try:
                from app.redis import get_redis

                async for redis_conn in get_redis():
                    self.redis = redis_conn
                    break
            except Exception as e:
                logger.warning(f"Failed to initialize Redis connection: {e}")
                self.redis = None

    async def _get_workflow_service(self):
        """获取WorkflowService实例"""
        await self._ensure_redis_connection()
        from app.database import AsyncSessionLocal
        from app.dependencies import get_workflow_service

        # 创建数据库会话
        db = AsyncSessionLocal()
        try:
            # 获取WorkflowService实例
            workflow_service = await get_workflow_service(db, self.redis)
            return workflow_service, db
        except Exception as e:
            # 如果出错，立即关闭数据库会话
            await db.close()
            raise e

    async def cleanup_connections(self):
        """清理Redis连接"""
        # Redis连接会自动返回到连接池，不需要手动关闭
        self.redis = None

    async def get_uid_from_raw_key(self, api_key: str) -> Optional[str]:
        """
        直接传递API Key，查询数据库得到 user_id (用于MCP工具函数)
        使用依赖注入模式
        """
        if not api_key:
            return None

        from app.models.api_key import OpenAPIDB
        from app.utils.api_key import APIKeyUtils
        from sqlalchemy.future import select
        from app.database import AsyncSessionLocal

        db = None
        try:
            db = AsyncSessionLocal()

            # 使用前缀匹配和哈希验证
            keys = await db.execute(select(OpenAPIDB).where(OpenAPIDB.prefix == api_key[:8], OpenAPIDB.is_active == 1))
            api_keys = keys.scalars().all()

            for key in api_keys:
                hashed_key = key.api_key
                if APIKeyUtils.verify_api_key(api_key, hashed_key):
                    return str(key.user_id)
            return None
        except Exception as e:
            logger.error(f"Error getting user ID from API key: {e}")
            if db:
                await db.rollback()
            return None
        finally:
            # 确保数据库会话被关闭
            if db:
                await db.close()

    async def get_user_workflows(self, user_id: str) -> List[Dict]:
        """获取用户允许使用的工具列表"""
        db = None
        try:
            workflow_service, db = await self._get_workflow_service()

            # 获取用户工作流
            user_workflows = await workflow_service.get_workflows(user_id)
            workflows = []
            for workflow in user_workflows:
                workflows.append(workflow.to_dict())
            return workflows
        except Exception as e:
            logger.error(f"Error getting user workflows: {e}")
            return []
        finally:
            # 确保数据库会话被关闭
            if db:
                await db.close()

    async def get_project_id_by_name(self, name: str, user_id: str) -> Optional[Tuple[str, int]]:
        """根据工具名称和用户ID查找对应的工作流项目ID"""
        db = None
        try:
            workflow_service, db = await self._get_workflow_service()

            # 获取用户工作流
            user_workflows = await workflow_service.get_workflows(user_id)

            # 查找匹配的工作流
            for workflow in user_workflows:
                # 优先使用 english_name，如果没有则使用 name
                workflow_name = workflow.english_name if workflow.english_name else workflow.name
                if workflow_name == name:
                    return workflow.project_id, workflow.version

            return None
        except Exception as e:
            logger.error(f"Error getting project_id for name '{name}' and user_id '{user_id}': {e}")
            return None
        finally:
            # 确保数据库会话被关闭
            if db:
                await db.close()

    async def execute_workflow_by_name(self, name: str, user_id: str, arguments: dict) -> dict:
        """根据工具名称执行对应的工作流"""
        await self._ensure_redis_connection()

        try:
            # 查找对应的工作流项目ID
            project_id, version = await self.get_project_id_by_name(name, user_id)
            if not project_id:
                return {
                    "success": False,
                    "error": f"No workflow found for tool '{name}' or permission denied",
                }

            # 创建执行参数
            from app.schemas.workflow import ExecutionCreate

            execution_data = ExecutionCreate(
                project_id=project_id, params=arguments, exec_position="EXECUTOR", version=version
            )

            # 创建执行服务并执行工作流
            from app.services.execution import ExecutionService
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as db_session:
                execution_service = ExecutionService(db_session)
                logger.info(f"[execute_workflow_by_name] user_id '{user_id}'")
                # 异步执行工作流
                execution = await execution_service.execute_workflow(
                    execution_data=execution_data,
                    user_id=user_id,
                    wait=True,  # 这里等待结果，用同步方法
                    workflow_timeout=600,
                )

                return {
                    "success": True,
                    "execution_id": execution.id,
                    "project_id": project_id,
                    "data": execution.to_dict(),
                    "message": json.loads(execution.result),
                }

        except Exception as e:
            logger.error(f"Error executing workflow for tool '{name}': {e}")
            return {"success": False, "error": f"Failed to execute workflow: {str(e)}"}

    @staticmethod
    def workflow_to_tool(workflow: Dict):
        """将工作流配置转换为MCP工具配置"""
        # 优先使用english_name作为工具名称
        tool_name = workflow.get("english_name") or workflow.get("name")

        # 如果有自定义parameters，使用它作为输入参数配置
        parameters = workflow.get("parameters")
        if parameters and isinstance(parameters, list):
            # 转换参数数组为JSON Schema格式
            tool_input_schema = ToolsConfig._convert_parameters_to_schema(parameters)
        else:
            tool_input_schema = parameters or {"type": "object"}

        tool_config = types.Tool(
            name=tool_name,
            description=workflow.get("description"),
            inputSchema=tool_input_schema,
        )

        return tool_config

    @staticmethod
    def _convert_parameters_to_schema(parameters: List[Dict]) -> Dict:
        """将工作流参数数组转换为JSON Schema格式"""
        schema = {"type": "object", "properties": {}, "required": []}

        # 类型映射表
        type_mapping = {
            "Str": "string",
            "Int": "integer",
            "Float": "number",
            "PATH": "string",
            "DIRPATH": "string",
            "Date": "string",
            "Password": "string",
        }

        for param in parameters:
            # 只处理输入参数 (varDirection = 0)
            if param.get("varDirection") == 0:
                var_name = param.get("varName")
                var_type = param.get("varType", "Str")
                var_describe = param.get("varDescribe", "")
                var_value = param.get("varValue", "")

                if var_name:
                    # 映射类型
                    json_type = type_mapping.get(var_type, "string")

                    # 构建属性定义
                    property_def = {"type": json_type, "description": var_describe}

                    # 如果有默认值，添加默认值
                    if var_value and var_value != "":
                        if json_type == "integer":
                            try:
                                property_def["default"] = int(var_value)
                            except ValueError:
                                pass
                        elif json_type == "number":
                            try:
                                property_def["default"] = float(var_value)
                            except ValueError:
                                pass
                        else:
                            property_def["default"] = var_value

                    schema["properties"][var_name] = property_def

                    # 如果没有默认值，添加到必需字段
                    if not var_value or var_value == "":
                        schema["required"].append(var_name)

        return schema

    async def get_tools_for_user(self, user_id: str) -> List[types.Tool]:
        """获取用户可用的工具配置列表"""
        user_workflows = await self.get_user_workflows(user_id)
        user_tools = []
        for workflow in user_workflows:
            user_tools.append(self.workflow_to_tool(workflow))

        return user_tools
