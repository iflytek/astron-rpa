import json
from typing import Optional

from mcp import types

from app.logger import get_logger
from app.security.workflow_authorization import WorkflowAccessError

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
                logger.warning("Failed to initialize Redis connection: %s", e)
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
        from app.database import AsyncSessionLocal
        from app.security.api_key import validate_api_key

        async with AsyncSessionLocal() as db:
            return await validate_api_key(db, api_key)

    async def get_user_workflows(self, user_id: str) -> list[dict]:
        """获取用户允许使用的工具列表"""
        db = None
        try:
            workflow_service, db = await self._get_workflow_service()

            # 获取用户工作流
            user_workflows = await workflow_service.get_external_workflows(user_id)
            workflows = []
            for workflow in user_workflows:
                workflows.append(workflow.to_dict())
            return workflows
        except Exception as e:
            logger.error("Workflow discovery failed: %s", type(e).__name__)  # noqa: TRY400 -- omit SQL parameters
            raise RuntimeError("Workflow discovery unavailable") from None
        finally:
            # 确保数据库会话被关闭
            if db:
                await db.close()

    async def get_project_id_by_name(self, name: str, user_id: str) -> Optional[tuple[str, int]]:
        """根据工具名称和用户ID查找对应的工作流项目ID"""
        db = None
        try:
            workflow_service, db = await self._get_workflow_service()

            # 获取用户工作流
            user_workflows = await workflow_service.get_external_workflows(user_id)

            # 查找匹配的工作流
            for workflow in user_workflows:
                # 优先使用 english_name，如果没有则使用 name
                workflow_name = workflow.english_name or workflow.name
                if workflow_name == name:
                    return workflow.project_id, workflow.version

            return None
        except Exception as e:
            logger.error("Workflow lookup failed: %s", type(e).__name__)  # noqa: TRY400 -- omit SQL parameters
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
            workflow_ref = await self.get_project_id_by_name(name, user_id)
            if not workflow_ref or not workflow_ref[0]:
                return {
                    "success": False,
                    "error": f"No workflow found for tool '{name}' or permission denied",
                }
            project_id, version = workflow_ref

            # 创建执行参数
            from app.schemas.workflow import ExecutionCreate

            execution_data = ExecutionCreate(
                project_id=project_id, params=arguments, exec_position="EXECUTOR", version=version
            )

            # 创建执行服务并执行工作流
            from app.database import AsyncSessionLocal
            from app.services.execution import ExecutionService

            async with AsyncSessionLocal() as db_session:
                execution_service = ExecutionService(db_session)
                logger.info("[execute_workflow_by_name] user_id '%s'", user_id)
                # 异步执行工作流
                execution = await execution_service.execute_authorized_workflow(
                    execution_data=execution_data,
                    user_id=user_id,
                    wait=True,  # 这里等待结果，用同步方法
                    workflow_timeout=600,
                    transport="mcp",
                )

                message = execution.get_result_as_dict()
                if not message:
                    return {
                        "success": False,
                        "error": "RPA client is offline or disconnected"
                        if execution.error == "RPA client is offline or disconnected"
                        else "Workflow execution result is unavailable",
                    }

                return {
                    "success": True,
                    "execution_id": execution.id,
                    "project_id": project_id,
                    "data": execution.to_dict(),
                    "message": message,
                }

        except Exception as e:
            logger.error("MCP execution failed: %s", type(e).__name__)  # noqa: TRY400 -- do not expose arguments
            return {"success": False, "error": "Workflow unavailable or execution failed"}

    @staticmethod
    def workflow_to_tool(workflow: dict):
        """将工作流配置转换为MCP工具配置"""
        from app.models.workflow import Workflow
        from app.services.workflow_schema import workflow_input_schema

        source = Workflow(parameters=json.dumps(workflow.get("parameters") or []))
        return types.Tool(
            name=workflow.get("english_name") or workflow.get("name"),
            description=workflow.get("description"),
            inputSchema=workflow_input_schema(source),
        )

    @staticmethod
    def _convert_parameters_to_schema(parameters: list[dict]) -> dict:
        from app.models.workflow import Workflow
        from app.services.workflow_schema import workflow_input_schema

        return workflow_input_schema(Workflow(parameters=json.dumps(parameters)))

    async def get_tools_for_user(self, user_id: str) -> list[types.Tool]:
        """获取用户可用的工具配置列表"""
        user_workflows = await self.get_user_workflows(user_id)
        user_tools = []
        for workflow in user_workflows:
            try:
                user_tools.append(self.workflow_to_tool(workflow))
            except WorkflowAccessError:
                # Unsupported workflows stay addressable for a safe detail error,
                # but cannot advertise an executable, misleading dynamic schema.
                continue

        return user_tools
