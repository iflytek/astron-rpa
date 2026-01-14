import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from redis.asyncio import Redis
from rpawebsocket.ws import BaseMsg
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.logger import get_logger
from app.models.workflow import Execution
from app.schemas.workflow import ExecutionCreate, ExecutionStatus

logger = get_logger(__name__)


class ExecutionService:
    def __init__(self, db: AsyncSession, redis: Redis = None):
        self.db = db
        self.redis = redis

    async def create_execution(self, execution_data: ExecutionCreate, user_id: str) -> Execution:
        """创建执行记录"""
        execution_id = str(uuid4())
        parameters = execution_data.params or {}

        # 使用json.dumps确保参数以有效的JSON格式存储
        parameters_json = json.dumps(parameters, ensure_ascii=False) if parameters else "{}"

        execution = Execution(
            id=execution_id,
            project_id=execution_data.project_id,
            parameters=parameters_json,
            user_id=user_id,
            exec_position=execution_data.exec_position,  # 保存执行位置
            version=execution_data.version,  # 保存版本号
            recording_config=execution_data.recording_config,  # 保存录制配置
            status=ExecutionStatus.PENDING.value,
        )

        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)

        return execution

    async def get_execution(self, execution_id: str, user_id: str | None = None) -> Optional[Execution]:
        """获取执行记录"""
        query = select(Execution).where(Execution.id == execution_id)

        # 不校验user_id
        # if user_id is not None:
        #     query = query.where(Execution.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_executions(
        self,
        project_id: str | None = None,
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Execution]:
        """获取执行记录列表"""
        query = select(Execution).order_by(Execution.start_time.desc()).offset(skip).limit(limit)

        if project_id is not None:
            query = query.where(Execution.project_id == project_id)
        if user_id is not None:
            query = query.where(Execution.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_executions_by_user(
        self,
        user_id: str,
        pageNo: int = 1,
        pageSize: int = 10,
    ) -> tuple[list[Execution], int]:
        """分页获取用户的执行记录"""
        skip = (pageNo - 1) * pageSize

        # 查询总数
        count_query = select(Execution).where(Execution.user_id == user_id)
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())

        # 查询分页数据
        query = (
            select(Execution)
            .where(Execution.user_id == user_id)
            .order_by(Execution.start_time.desc())
            .offset(skip)
            .limit(pageSize)
        )
        result = await self.db.execute(query)
        executions = result.scalars().all()

        return executions, total

    async def update_execution_status(
        self,
        execution_id: str,
        status: str,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Optional[Execution]:
        """更新执行记录状态"""
        try:
            # 直接使用SQL更新，避免会话状态问题
            update_stmt = update(Execution).where(Execution.id == execution_id)

            update_data = {Execution.status: status}
            if result is not None:
                if isinstance(result, dict):
                    update_data[Execution.result] = json.dumps(result, ensure_ascii=False)
                else:
                    # 如果不是字典，尝试转换为字符串
                    update_data[Execution.result] = str(result)
            if error is not None:
                update_data[Execution.error] = error
            if status in [
                ExecutionStatus.COMPLETED.value,
                ExecutionStatus.FAILED.value,
                ExecutionStatus.CANCELLED.value,
            ]:
                update_data[Execution.end_time] = datetime.now()

            update_stmt = update_stmt.values(update_data)
            await self.db.execute(update_stmt)
            await self.db.commit()

            # 返回更新后的执行记录
            return await self.get_execution(execution_id)
        except Exception as e:
            # 如果更新失败，回滚事务并记录错误
            try:
                await self.db.rollback()
            except:
                pass  # 如果回滚失败，忽略错误
            logger.exception("Failed to update execution %s", execution_id)
            return None

    async def execute_workflow(
        self,
        execution_data: ExecutionCreate,
        user_id: str,
        wait: bool = True,
        workflow_timeout: int = 36000,
    ) -> Optional[Execution]:
        """执行工作流"""
        # 创建执行记录
        execution = await self.create_execution(execution_data, user_id)

        # 确保执行记录已经提交到数据库
        await self.db.commit()
        logger.info("Created execution %s and committed to database", execution.id)
        logger.info("[execute_workflow] user_id: %s ", user_id)

        # 保存 execution_id，后续需要用
        execution_id = execution.id

        # 执行工作流逻辑（异步/同步）
        # 添加短暂延迟，确保数据库事务完全提交
        await asyncio.sleep(0.1)

        if wait:
            # 同步执行模式 - 使用新的数据库会话，避免长时间占用连接
            await self._run_workflow_with_new_session_sync(execution_id, workflow_timeout, user_id)

            # 使用原会话重新获取最新状态
            await self.db.refresh(execution)
        else:
            # 异步执行模式，后台执行（不等待结果）
            asyncio.create_task(self._run_workflow_with_new_session(execution_id, workflow_timeout, user_id))

        return execution

    async def _run_workflow(self, execution_id: str, workflow_timeout: int = 36000, user_id: str = "") -> None:
        """运行工作流执行逻辑"""
        try:
            # 获取执行记录
            execution = await self.get_execution(execution_id)
            if not execution:
                logger.info("Execution not found for execution_id: %s", execution_id)
                raise Exception(f"Execution not found for execution_id: {execution_id}")
            logger.info("[_run_workflow] user_id: %s ", user_id)
            # 设置超时
            await asyncio.wait_for(
                self._execute_workflow_logic(execution, user_id),
                timeout=workflow_timeout,
            )
        except TimeoutError:
            # 超时处理 - 使用update_execution_status方法避免会话问题
            await self.update_execution_status(execution_id, ExecutionStatus.RUNNING.value)
            raise
        except Exception as e:
            await self.update_execution_status(execution_id, ExecutionStatus.FAILED.value, error=str(e))

    async def _run_workflow_with_new_session_sync(self, execution_id: str, workflow_timeout: int, user_id: str) -> None:
        """使用新的数据库会话运行工作流（同步版本，会抛出异常）"""
        async with AsyncSessionLocal() as db:
            execution_service = ExecutionService(db, self.redis)
            logger.info("Running workflow execution %s", execution_id)
            await execution_service._run_workflow(execution_id, workflow_timeout, user_id)

    async def _run_workflow_with_new_session(self, execution_id: str, workflow_timeout: int, user_id: str) -> None:
        """使用新的数据库会话运行工作流（异步版本，不抛出异常）"""
        async with AsyncSessionLocal() as db:
            try:
                execution_service = ExecutionService(db, self.redis)
                logger.info("Running background workflow execution %s", execution_id)
                await execution_service._run_workflow(execution_id, workflow_timeout, user_id)
            except Exception as e:
                # 记录错误日志
                logger.exception("Error in background workflow execution %s", execution_id)

                # 更新执行状态为失败，确保用户能看到错误
                try:
                    # 使用新的会话来更新状态，避免会话问题
                    async with AsyncSessionLocal() as update_db:
                        update_service = ExecutionService(update_db, self.redis)
                        await update_service.update_execution_status(
                            execution_id, ExecutionStatus.FAILED.value, error=str(e)
                        )
                except Exception as update_error:
                    logger.exception("Failed to update execution status for %s", execution_id)

    async def _execute_workflow_logic(self, execution: Execution, user_id: str) -> None:
        """
        实现工作流执行的实际逻辑
        这里是一个示例，实际项目中需要根据不同工作流实现不同的逻辑
        """
        import json

        logger.info("Starting workflow execution logic for execution %s", execution.id)

        try:
            # 模拟异步工作流执行
            # 实际项目中可能涉及调用外部系统、处理数据等操作
            # 回调事件
            from app.dependencies import get_ws_service

            websocket_service = await get_ws_service()
            logger.info("Got websocket service for execution %s", execution.id)
            logger.info("execution.user_id: %s", execution.user_id)
            logger.info("input user_id: %s", user_id)

            wait = asyncio.Event()
            res = {}
            res_e = None

            def callback(watch_msg: BaseMsg | None = None, e: Exception | None = None):
                nonlocal wait, res, res_e
                if watch_msg:
                    res = watch_msg.data
                    logger.info("Received response for execution %s: %s", execution.id, res)
                    # Received response for execution 71e3147f-55cd-43f5-b7a8-b734d1075618:
                    # {'code': '5001', 'msg': '', 'data': None}
                if e:
                    res_e = e
                    logger.error("Received error for execution %s: %s", execution.id, e)
                wait.set()

            # 解析参数，确保是字典格式
            if execution.parameters is None:
                parameters_dict = {}
            elif isinstance(execution.parameters, str):
                try:
                    parameters_dict = json.loads(execution.parameters)
                except json.JSONDecodeError as e:
                    logger.exception("Failed to parse parameters JSON for execution %s", execution.id)
                    parameters_dict = {}
            else:
                parameters_dict = execution.parameters

            run_param = []
            for key, value in parameters_dict.items():
                logger.debug("参数: %s=%s", key, value)
                run_param.append({"varName": key, "varValue": value})
            run_param = json.dumps(run_param, ensure_ascii=False)

            executor_data = {
                "project_id": execution.project_id,
                "exec_position": execution.exec_position,
                "jwt": "",
                "run_param": run_param,
            }
            if execution.recording_config:
                executor_data["recording_config"] = execution.recording_config
            if execution.version:
                executor_data["version"] = execution.version

            base_msg = BaseMsg(
                channel="remote",
                key="run",
                uuid="$root$",
                send_uuid=f"{user_id}",
                need_reply=True,
                data=executor_data,
            ).init()

            logger.info("Sending WebSocket message for execution %s: %s", execution.id, base_msg.data)
            await websocket_service.ws_manager.send_reply(base_msg, 10 * 3600, callback)

            # 等待
            logger.info("Waiting for response for execution %s", execution.id)
            await wait.wait()
            logger.info("Received response for execution %s", execution.id)

            # 假设工作流执行成功
            if res.get("code") == "0000":
                await self.update_execution_status(
                    execution.id,
                    ExecutionStatus.COMPLETED.value,
                    result=res,
                    error=str(res_e) if res_e else None,
                )
                logger.info("Updated execution %s status to COMPLETED", execution.id)
            elif res.get("code") == "5001":
                await self.update_execution_status(
                    execution.id,
                    ExecutionStatus.FAILED.value,
                    result=res,
                    error=str(res_e) if res_e else None,
                )
                logger.info("Updated execution %s status to FAILED", execution.id)

        except Exception as e:
            logger.exception("Error in workflow execution logic for %s", execution.id)
            raise

    async def cancel_execution(self, execution_id: str, user_id: str) -> bool:
        """取消执行"""
        try:
            execution = await self.get_execution(execution_id, user_id)
            if not execution or execution.status not in [
                ExecutionStatus.PENDING.value,
                ExecutionStatus.RUNNING.value,
            ]:
                return False

            # 使用update_execution_status方法
            updated_execution = await self.update_execution_status(execution_id, ExecutionStatus.CANCELLED.value)

            return updated_execution is not None
        except Exception as e:
            logger.exception("Failed to cancel execution %s", execution_id)
            return False
