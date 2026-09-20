import asyncio
import json
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from redis.asyncio import Redis
from rpawebsocket.ws import BaseMsg
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.logger import get_logger
from app.models.workflow import Execution, Workflow
from app.schemas.integration import SERVICE_READ_CLASSES
from app.schemas.workflow import ExecutionCreate, ExecutionStatus
from app.security.workflow_authorization import WorkflowAccessError
from app.services import execution_management as management
from app.services.integration_policy import require_admission
from app.services.workflow import WorkflowService
from app.services.workflow_schema import (
    JSON_LIMITS,
    bind_arguments,
    validate_json_value,
    workflow_input_schema,
    workflow_secret_fields,
)

logger = get_logger(__name__)

# Keep dispatched work alive if an HTTP/MCP caller stops waiting. This is
# process-local ownership, not a durable queue or cancellation API.
_execution_tasks: set[asyncio.Task] = set()


def _log_execution_error(operation: str, execution_id: str, error: Exception) -> None:
    # SQL and client exception messages can contain unlabelled parameter
    # values that a key-name-based redactor cannot identify safely.
    logger.error("Execution %s failed during %s: %s", execution_id, operation, type(error).__name__)


def _execution_task_done(task: asyncio.Task) -> None:
    _execution_tasks.discard(task)
    if not task.cancelled():
        error = task.exception()  # Retrieve failures even when the caller disconnected.
        if error is not None:
            logger.error("Execution task %s ended with %s", task.get_name(), type(error).__name__)


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
            start_time=datetime.now(UTC).replace(tzinfo=None),
        )

        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)

        return execution

    async def get_execution(self, execution_id: str, user_id: str) -> Optional[Execution]:
        """获取属于指定用户的执行记录。"""
        query = select(Execution).where(
            Execution.id == execution_id,
            Execution.user_id == user_id,
        )

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_authorized_execution(self, execution_id: str, user_id: str) -> Optional[Execution]:
        execution = await self.get_execution(execution_id, user_id)
        if execution is None or execution.version is None or execution.version < 1:
            return None
        try:
            # Ordinary publication does not revoke an already accepted execution.
            # Ownership, deletion and the external-access switch still apply.
            await WorkflowService(self.db).get_external_workflow(execution.project_id, user_id)
        except WorkflowAccessError:
            return None
        return execution

    async def get_execution_internal(self, execution_id: str) -> Optional[Execution]:
        """供后台执行流程按 ID 获取记录，不作为外部授权边界。"""
        query = select(Execution).where(Execution.id == execution_id)

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
        # Match detail visibility: current owner, external access and release.
        visible = (
            select(Execution)
            .join(Workflow, Workflow.project_id == Execution.project_id)
            .where(
                Execution.user_id == user_id,
                Workflow.user_id == user_id,
                Workflow.status == 1,
                Workflow.version >= 1,
                Execution.version >= 1,
            )
        )
        total = (await self.db.execute(select(func.count()).select_from(visible.subquery()))).scalar_one()
        result = await self.db.execute(visible.order_by(Execution.start_time.desc()).offset(skip).limit(pageSize))
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
            allowed = ["PENDING", "UNKNOWN"] if status == "PENDING" else ["PENDING", "RUNNING", "UNKNOWN"]
            update_stmt = update(Execution).where(Execution.id == execution_id, Execution.status.in_(allowed))

            update_data = {Execution.status: status}
            if result is not None:
                update_data[Execution.result] = json.dumps(result, ensure_ascii=False, allow_nan=False)
            if error is not None:
                update_data[Execution.error] = error
            if status in [
                ExecutionStatus.COMPLETED.value,
                ExecutionStatus.FAILED.value,
                ExecutionStatus.CANCELLED.value,
                ExecutionStatus.TIMEOUT.value,
            ]:
                update_data[Execution.end_time] = datetime.now(UTC).replace(tzinfo=None)
                update_data[Execution.dispatch_state] = "DONE"
                record = await self.get_execution_internal(execution_id)
                if record is not None and record.protocol == 1 and record.secret_fields:
                    params = record.get_parameters_as_dict()
                    for key in json.loads(record.secret_fields):
                        if key in params:
                            params[key] = "[REDACTED]"
                    update_data[Execution.parameters] = json.dumps(params, allow_nan=False)

            update_stmt = update_stmt.values(update_data)
            await self.db.execute(update_stmt)
            await self.db.commit()

            # 返回更新后的执行记录
            return await self.get_execution_internal(execution_id)
        except Exception as exc:
            # 如果更新失败，回滚事务并记录错误
            try:
                await self.db.rollback()
            except:
                pass  # 如果回滚失败，忽略错误
            _log_execution_error("status update", execution_id, exc)
            return None

    async def execute_authorized_workflow(
        self,
        execution_data: ExecutionCreate,
        user_id: str,
        wait: bool = True,
        workflow_timeout: int = 36000,
        *,
        transport: str = "rest",
    ) -> Optional[Execution]:
        if execution_data.phone_number is not None or execution_data.exec_position != "EXECUTOR":
            raise WorkflowAccessError(
                "EXECUTION_NOT_ALLOWED", "Delegated identity and unpublished execution are not allowed"
            )
        key_hash = management.digest(execution_data.idempotency_key) if execution_data.idempotency_key else None
        try:
            request = execution_data.model_dump(exclude={"idempotency_key", "profile_revision", "capability_class"})
            # Keep the digest of pre-framework requests unchanged across upgrades.
            if execution_data.profile_revision is not None:
                request["profile_revision"] = execution_data.profile_revision
            if execution_data.capability_class is not None:
                request["capability_class"] = execution_data.capability_class
            request_hash = management.digest(request)
        except (ValueError, TypeError):
            raise WorkflowAccessError("INVALID_ARGUMENTS", "Inputs must be finite JSON values") from None

        async def previous():
            if key_hash is None:
                return None
            result = await self.db.execute(
                select(Execution).where(Execution.user_id == user_id, Execution.idempotency_key_hash == key_hash)
            )
            record = result.scalars().first()
            if record is None:
                return None
            if await self.get_authorized_execution(record.id, user_id) is None:
                raise WorkflowAccessError("WORKFLOW_NOT_FOUND", "Workflow not found or access is disabled")
            if record.request_hash != request_hash:
                raise WorkflowAccessError("IDEMPOTENCY_CONFLICT", "This idempotency key belongs to another request")
            return record

        existing = await previous()
        if existing is not None:
            return existing
        workflow = await WorkflowService(self.db).get_external_workflow(
            execution_data.project_id, user_id, execution_data.version, allow_example_alias=True
        )
        schema = workflow_input_schema(workflow)
        params = bind_arguments(execution_data.params or {}, schema)
        profile = require_admission(
            workflow, user_id, execution_data.profile_revision, params=params, transport=transport
        )
        requested_class = execution_data.capability_class
        if requested_class is not None and profile["capabilityClass"] != requested_class:
            raise WorkflowAccessError("CAPABILITY_NOT_ALLOWED", "Workflow is not admitted for the requested capability")
        bounded_json = profile["capabilityClass"] in {"json-data", *SERVICE_READ_CLASSES}
        if bounded_json:
            # Bound the raw request before defaults, then again after binding.
            validate_json_value(execution_data.params or {}, require_object=True)
        data_contract = None
        if bounded_json:
            validate_json_value(params, require_object=True)
            data_contract = json.dumps(
                {
                    "version": 1,
                    "profileRevision": profile["revision"],
                    "inputSchemaHash": profile["inputSchemaHash"],
                    "outputSchema": profile["outputSchema"],
                    "limits": JSON_LIMITS,
                },
                allow_nan=False,
            )
        authorized = execution_data.model_copy(
            update={"project_id": workflow.project_id, "version": workflow.version, "params": params}
        )
        secrets = workflow_secret_fields(workflow, schema)
        requires_managed = bool(
            bounded_json
            or key_hash is not None
            or execution_data.execution_timeout is not None
            or secrets
            or any(type(value) not in (str, int, float) for value in params.values())
        )
        capability = await management.capabilities(user_id, required=requires_managed)
        if not capability and requires_managed:
            raise WorkflowAccessError(
                "CLIENT_PROTOCOL_UNSUPPORTED", "These options or inputs require an execution-management Client"
            )
        metadata = {
            "idempotency_key_hash": key_hash,
            "request_hash": request_hash,
            "execution_timeout": execution_data.execution_timeout,
            "secret_fields": json.dumps(secrets) if secrets else None,
            "data_contract": data_contract,
        }
        if capability:
            metadata.update(
                protocol=1,
                client_id=capability["clientId"],
                dispatch_state="NEW",
                cancel_supported=capability.get("supportsCancel") is True,
            )
        try:
            return await self.execute_workflow(
                authorized, user_id, wait=wait, workflow_timeout=workflow_timeout, metadata=metadata
            )
        except IntegrityError:
            # The unique constraint arbitrates across concurrent requests/processes.
            await self.db.rollback()
            existing = await previous()
            if existing is not None:
                return existing
            raise

    async def execute_workflow(
        self,
        execution_data: ExecutionCreate,
        user_id: str,
        wait: bool = True,
        workflow_timeout: int = 36000,
        metadata: dict | None = None,
    ) -> Optional[Execution]:
        """执行工作流"""
        # 创建执行记录
        execution = await self.create_execution(execution_data, user_id)
        for key, value in (metadata or {}).items():
            setattr(execution, key, value)

        # 确保执行记录已经提交到数据库
        await self.db.commit()
        logger.info(
            "Created execution %s for authenticated user %s and committed to database",
            execution.id,
            execution.user_id,
        )

        # 保存 execution_id，后续需要用
        execution_id = execution.id

        # The commit above has completed. Take ownership before another await,
        # so request cancellation cannot abandon already committed work.
        runner = self._run_workflow_with_new_session_sync if wait else self._run_workflow_with_new_session
        task = asyncio.create_task(runner(execution_id, workflow_timeout), name=f"execution-{execution_id}")
        _execution_tasks.add(task)
        task.add_done_callback(_execution_task_done)

        if wait:
            # 同步执行模式 - 使用新的数据库会话，避免长时间占用连接
            await asyncio.shield(task)

            # 使用原会话重新获取最新状态
            await self.db.refresh(execution)

        return execution

    async def _run_workflow(self, execution_id: str, workflow_timeout: int = 36000) -> None:
        """运行工作流执行逻辑"""
        execution = None
        try:
            # 重新读取已提交的执行记录。此处的 user_id 是派发目标的唯一可信来源，
            # 避免调用方另传身份而造成审计记录与实际执行主体不一致。
            execution = await self.get_execution_internal(execution_id)
            if not execution:
                logger.info("Execution not found for execution_id: %s", execution_id)
                raise Exception(f"Execution not found for execution_id: {execution_id}")
            # 设置超时
            await asyncio.wait_for(
                self._execute_workflow_logic(execution),
                timeout=workflow_timeout,
            )
        except TimeoutError:
            # Losing the result does not establish that the desktop task is
            # running, failed, or stopped. Keep this distinct from a terminal state.
            await self.update_execution_status(
                execution_id,
                ExecutionStatus.UNKNOWN.value,
                error="Execution result timed out; the client may still be running",
            )
            raise
        except Exception as e:
            await self.update_execution_status(
                execution_id,
                ExecutionStatus.UNKNOWN.value
                if execution and execution.protocol == 1
                else ExecutionStatus.FAILED.value,
                error="EXECUTION_OBSERVATION_FAILED" if execution and execution.protocol == 1 else str(e),
            )

    async def _run_workflow_with_new_session_sync(self, execution_id: str, workflow_timeout: int) -> None:
        """使用新的数据库会话运行工作流（同步版本，会抛出异常）"""
        async with AsyncSessionLocal() as db:
            execution_service = ExecutionService(db, self.redis)
            logger.info("Running workflow execution %s", execution_id)
            await execution_service._run_workflow(execution_id, workflow_timeout)

    async def _run_workflow_with_new_session(self, execution_id: str, workflow_timeout: int) -> None:
        """使用新的数据库会话运行工作流（异步版本，不抛出异常）"""
        async with AsyncSessionLocal() as db:
            try:
                execution_service = ExecutionService(db, self.redis)
                logger.info("Running background workflow execution %s", execution_id)
                await execution_service._run_workflow(execution_id, workflow_timeout)
            except TimeoutError:
                # _run_workflow already persisted UNKNOWN. Do not overwrite it
                # with FAILED merely because this asynchronous observer expired.
                return
            except Exception as e:
                # 记录错误日志
                _log_execution_error("background execution", execution_id, e)

                # 更新执行状态为失败，确保用户能看到错误
                try:
                    # 使用新的会话来更新状态，避免会话问题
                    async with AsyncSessionLocal() as update_db:
                        update_service = ExecutionService(update_db, self.redis)
                        record = await update_service.get_execution_internal(execution_id)
                        managed = record is not None and record.protocol == 1
                        await update_service.update_execution_status(
                            execution_id,
                            ExecutionStatus.UNKNOWN.value if managed else ExecutionStatus.FAILED.value,
                            error="EXECUTION_OBSERVATION_FAILED" if managed else str(e),
                        )
                except Exception as exc:
                    _log_execution_error("background status update", execution_id, exc)

    async def _execute_workflow_logic(self, execution: Execution) -> None:
        """
        实现工作流执行的实际逻辑
        这里是一个示例，实际项目中需要根据不同工作流实现不同的逻辑
        """
        if execution.protocol == 1:
            await management.run_managed(self, execution)
            return

        import json

        logger.info("Starting workflow execution logic for execution %s", execution.id)

        try:
            # 模拟异步工作流执行
            # 实际项目中可能涉及调用外部系统、处理数据等操作
            # 回调事件
            from app.dependencies import get_ws_service

            websocket_service = await get_ws_service()
            logger.info("Got websocket service for execution %s", execution.id)

            if not execution.user_id:
                raise ValueError(f"Execution {execution.id} has no authenticated user identity")
            if str(execution.user_id) not in websocket_service.ws_manager.conns:
                raise ConnectionError("RPA client is offline or disconnected")
            logger.info(
                "Dispatching execution %s for recorded user %s",
                execution.id,
                execution.user_id,
            )

            wait = asyncio.Event()
            res = {}
            res_e = None

            def callback(watch_msg: BaseMsg | None = None, e: Exception | None = None):
                nonlocal wait, res, res_e
                if watch_msg:
                    res = watch_msg.data
                    logger.info("Received response for execution %s", execution.id)
                    # Received response for execution 71e3147f-55cd-43f5-b7a8-b734d1075618:
                    # {'code': '5001', 'msg': '', 'data': None}
                if e:
                    res_e = e
                    _log_execution_error("client response", execution.id, e)
                wait.set()

            # 解析参数，确保是字典格式
            if execution.parameters is None:
                parameters_dict = {}
            elif isinstance(execution.parameters, str):
                try:
                    parameters_dict = json.loads(execution.parameters)
                except json.JSONDecodeError as exc:
                    _log_execution_error("parameter decoding", execution.id, exc)
                    parameters_dict = {}
            else:
                parameters_dict = execution.parameters

            run_param = []
            for key, value in parameters_dict.items():
                logger.debug("Preparing workflow parameter: %s", key)
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
                send_uuid=str(execution.user_id),
                need_reply=True,
                data=executor_data,
            ).init()

            logger.info("Sending WebSocket message for execution %s", execution.id)
            await websocket_service.ws_manager.send_reply(base_msg, 10 * 3600, callback)

            # 等待
            logger.info("Waiting for response for execution %s", execution.id)
            await wait.wait()
            logger.info("Received response for execution %s", execution.id)

            if res_e:
                raise RuntimeError(f"WebSocket execution failed: {res_e}")

            # rpawebsocket may deserialize the reply envelope while leaving its
            # data field as a JSON string. Normalize both wire representations
            # before classifying the client result.
            if isinstance(res, str):
                try:
                    res = json.loads(res)
                except json.JSONDecodeError as exc:
                    raise ValueError("Client returned invalid serialized execution data") from exc
            if not isinstance(res, dict):
                raise TypeError(f"Client returned unsupported execution data type: {type(res).__name__}")

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
            else:
                error = f"Client returned unexpected execution code: {res.get('code')!r}"
                await self.update_execution_status(
                    execution.id,
                    ExecutionStatus.FAILED.value,
                    result=res,
                    error=error,
                )
                logger.info("Updated execution %s status to FAILED: unexpected client code", execution.id)

        except Exception as exc:
            _log_execution_error("workflow execution", execution.id, exc)
            raise

    async def request_cancellation(self, execution_id: str, user_id: str) -> Execution:
        execution = await self.get_authorized_execution(execution_id, user_id)
        if execution is None:
            raise WorkflowAccessError("EXECUTION_NOT_FOUND", "Execution not found or access is disabled")
        if execution.status in management.TERMINAL and execution.protocol == 1:
            return execution
        if execution.protocol != 1 or not execution.cancel_supported:
            raise WorkflowAccessError("CANCEL_UNSUPPORTED", "Client cannot confirm cancellation of this execution")
        await self.db.execute(
            update(Execution)
            .where(Execution.id == execution_id, Execution.status.not_in(management.TERMINAL))
            .values(cancel_requested=True)
        )
        await self.db.commit()
        await self.db.refresh(execution)
        # Persist intent. The dispatcher queries and cancels the exact bound run.
        # A cancelled tool request cannot erase this intent or forge stopped status.
        return execution

    async def cancel_execution(self, execution_id: str, user_id: str) -> bool:
        try:
            execution = await self.request_cancellation(execution_id, user_id)
            return execution.status == "CANCELLED"
        except WorkflowAccessError:
            return False
