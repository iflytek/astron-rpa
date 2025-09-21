import json
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Execution
from app.schemas.workflow import ExecutionCreate, ExecutionStatus
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from redis.asyncio import Redis
import asyncio

from app.services.websocket import WsManagerService
from rpawebsocket.ws import Conn, IWebSocket, BaseMsg
from app.database import AsyncSessionLocal
from app.logger import get_logger
logger = get_logger(__name__)

class ExecutionService:
    def __init__(self, db: AsyncSession, redis: Redis = None):
        self.db = db
        self.redis = redis
    
    async def create_execution(self, execution_data: ExecutionCreate, user_id: str) -> Execution:
        """创建执行记录"""
        execution_id = str(uuid4())
        parameters = execution_data.params if execution_data.params else {}
        
        # 使用json.dumps确保参数以有效的JSON格式存储
        parameters_json = json.dumps(parameters, ensure_ascii=False) if parameters else "{}"
        
        execution = Execution(
            id=execution_id,
            project_id=execution_data.project_id,
            parameters=parameters_json,
            user_id=user_id,
            exec_position=execution_data.exec_position,  # 保存执行位置
            status=ExecutionStatus.PENDING.value
        )
        
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)
        
        return execution
    
    async def get_execution(self, execution_id: str, user_id: str = None) -> Optional[Execution]:
        """获取执行记录"""
        query = select(Execution).where(Execution.id == execution_id)
        if user_id is not None:
            query = query.where(Execution.user_id == user_id)
            
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_executions(self, project_id: str = None, user_id: str = None, skip: int = 0, limit: int = 100) -> List[Execution]:
        """获取执行记录列表"""
        query = select(Execution).order_by(Execution.start_time.desc()).offset(skip).limit(limit)
        
        if project_id is not None:
            query = query.where(Execution.project_id == project_id)
        if user_id is not None:
            query = query.where(Execution.user_id == user_id)
            
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_execution_status(self, execution_id: str, status: str, result: Dict[str, Any] = None, error: str = None) -> Optional[Execution]:
        """更新执行记录状态"""
        try:
            # 直接使用SQL更新，避免会话状态问题
            update_stmt = update(Execution).where(Execution.id == execution_id)
            
            update_data = {"status": status}
            if result is not None:
                # 使用json.dumps确保result以有效的JSON格式存储
                update_data["result"] = json.dumps(result, ensure_ascii=False)
            if error is not None:
                update_data["error"] = error
            if status in [ExecutionStatus.COMPLETED.value, ExecutionStatus.FAILED.value, ExecutionStatus.CANCELLED.value]:
                update_data["end_time"] = datetime.now()
            
            update_stmt = update_stmt.values(**update_data)
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
            
            logger.error(f"Failed to update execution status for {execution_id}: {str(e)}")
            return None
    
    async def execute_workflow(self, execution_data: ExecutionCreate, 
                               user_id: str, wait: bool = True, timeout: int = 60) -> Optional[Execution]:
        """执行工作流"""
        # 创建执行记录
        execution = await self.create_execution(execution_data, user_id)
        
        # 确保执行记录已经提交到数据库
        await self.db.commit()
        logger.info(f"Created execution {execution.id} and committed to database")
        
        # 执行工作流逻辑（异步/同步）
        if wait:
            # 同步执行模式，等待结果
            try:
                await self._run_workflow(execution.id, timeout)
                # 重新获取执行记录以获取最新状态
                await self.db.refresh(execution)
            except asyncio.TimeoutError:
                # 超时情况下返回当前执行状态
                execution.status = ExecutionStatus.RUNNING.value
                await self.db.commit()
        else:
            # 异步执行模式，后台执行
            # 为后台任务创建新的数据库会话，避免会话状态冲突
            # 添加短暂延迟，确保数据库事务完全提交
            await asyncio.sleep(0.1)
            asyncio.create_task(self._run_workflow_with_new_session(execution.id, timeout, user_id))
            
        return execution
    
    async def _run_workflow(self, execution_id: str, timeout: int = 60) -> None:
        """运行工作流执行逻辑"""
        try:
            # 获取执行记录
            execution = await self.get_execution(execution_id)
            if not execution:
                logger.info(f"Execution not found for execution_id: {execution_id}")
                raise Exception(f"Execution not found for execution_id: {execution_id}")
            
            # 设置超时
            await asyncio.wait_for(
                self._execute_workflow_logic(execution),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            # 超时处理 - 使用update_execution_status方法避免会话问题
            await self.update_execution_status(execution_id, ExecutionStatus.RUNNING.value)
            raise
        except Exception as e:
            await self.update_execution_status(
                execution_id, 
                ExecutionStatus.FAILED.value, 
                error=str(e)
            )
    
    async def _run_workflow_with_new_session(self, execution_id: str, timeout: int, user_id: str) -> None:
        """使用新的数据库会话运行工作流"""
        async with AsyncSessionLocal() as db:
            try:
                # 创建新的ExecutionService实例，使用新的数据库会话
                execution_service = ExecutionService(db, self.redis)
                
                # 添加重试机制，处理可能的时序问题
                max_retries = 3
                retry_delay = 0.5
                
                for attempt in range(max_retries):
                    try:
                        await execution_service._run_workflow(execution_id, timeout)
                        break  # 成功执行，跳出重试循环
                    except Exception as retry_error:
                        if "Execution not found" in str(retry_error) and attempt < max_retries - 1:
                            logger.warning(f"Execution {execution_id} not found on attempt {attempt + 1}, retrying in {retry_delay}s...")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # 指数退避
                            continue
                        else:
                            raise retry_error
                            
            except Exception as e:
                # 记录错误日志
                logger.error(f"Error in background workflow execution {execution_id}: {str(e)}")
                
                # 更新执行状态为失败，确保用户能看到错误
                try:
                    await execution_service.update_execution_status(
                        execution_id, 
                        ExecutionStatus.FAILED.value, 
                        error=str(e)
                    )
                except Exception as update_error:
                    logger.error(f"Failed to update execution status for {execution_id}: {str(update_error)}")
    
    async def _execute_workflow_logic(self, execution: Execution) -> None:
        """
        实现工作流执行的实际逻辑
        这里是一个示例，实际项目中需要根据不同工作流实现不同的逻辑
        """
        import json
        logger.info(f"Starting workflow execution logic for execution {execution.id}")
        
        try:
            # 模拟异步工作流执行
            # 实际项目中可能涉及调用外部系统、处理数据等操作
            # 回调事件
            from app.dependencies import get_ws_service
            websocket_service = await get_ws_service()
            logger.info(f"Got websocket service for execution {execution.id}")
            
            wait = asyncio.Event()
            res = {}
            res_e = None
            def callback(watch_msg: BaseMsg = None, e: Exception = None):
                nonlocal wait, res, res_e
                if watch_msg:
                    res = watch_msg.data
                    logger.info(f"Received response for execution {execution.id}: {res}")
                if e:
                    res_e = e
                    logger.error(f"Received error for execution {execution.id}: {e}")
                wait.set()

            # 解析参数，确保是字典格式
            if execution.parameters is None:
                execution.parameters = {}
            elif isinstance(execution.parameters, str):
                try:
                    execution.parameters = json.loads(execution.parameters)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse parameters JSON for execution {execution.id}: {e}")
                    execution.parameters = {}

            run_param = []
            for key, value in execution.parameters.items():
                logger.debug(f"参数: {key}={value}")
                run_param.append({"varName": key, "varValue": value})
            run_param = json.dumps(run_param, ensure_ascii=False)

            base_msg = BaseMsg(
                channel="remote",
                key="run",
                uuid="$root$",
                send_uuid=f"{execution.user_id}",
                need_reply=True,
                data={"project_id": execution.project_id, "exec_position": execution.exec_position, 
                      "jwt": "", "run_param": run_param}
            ).init()

            logger.info(f"Sending WebSocket message for execution {execution.id}: {base_msg.data}")
            await websocket_service.ws_manager.send_reply(base_msg, 10 * 3600, callback)

            # 等待
            logger.info(f"Waiting for response for execution {execution.id}")
            await wait.wait()
            logger.info(f"Received response for execution {execution.id}")
            
            # 假设工作流执行成功
            await self.update_execution_status(
                execution.id,
                ExecutionStatus.COMPLETED.value,
                result=res,
                error=str(res_e) if res_e else None
            )
            logger.info(f"Updated execution {execution.id} status to COMPLETED")
            
        except Exception as e:
            logger.error(f"Error in workflow execution logic for {execution.id}: {str(e)}")
            raise
    
    async def cancel_execution(self, execution_id: str, user_id: str) -> bool:
        """取消执行"""
        try:
            execution = await self.get_execution(execution_id, user_id)
            if not execution or execution.status not in [ExecutionStatus.PENDING.value, ExecutionStatus.RUNNING.value]:
                return False
            
            # 使用update_execution_status方法
            updated_execution = await self.update_execution_status(
                execution_id, 
                ExecutionStatus.CANCELLED.value
            )
            
            return updated_execution is not None
        except Exception as e:
            logger.error(f"Failed to cancel execution {execution_id}: {str(e)}")
            return False
    