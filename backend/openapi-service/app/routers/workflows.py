import json

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.dependencies import (
    get_astron_api_key_service,
    get_execution_service,
    get_user_id_from_api_key,
    get_user_id_from_header,
    get_user_id_with_fallback,
    get_user_service,
    get_workflow_service,
)
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse
from app.schemas.workflow import (
    ExecutionCreate,
    ExecutionStatus,
    WorkflowBase,
    WorkflowCopyRequest,
)
from app.services.api_key import AstronApiKeyService
from app.services.execution import ExecutionService
from app.services.user import UserService
from app.services.workflow import WorkflowService

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflow"])


@router.post(
    "/upsert",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="创建或修改工作流",
    description="如果 project_id 不存在则创建新工作流，如果存在则更新现有工作流",
)
async def create_or_update_workflow(
    workflow_data: WorkflowBase,
    user_id: str = Depends(get_user_id_from_header),
    service: WorkflowService = Depends(get_workflow_service),
):
    """创建或修改工作流"""
    try:
        # 先检查是否已存在相同 project_id 的工作流
        existing_workflow = await service.get_workflow(str(workflow_data.project_id))

        if existing_workflow:
            # 如果存在，检查是否属于当前用户
            if existing_workflow.user_id != user_id:
                return StandardResponse(
                    code=ResCode.ERR,
                    msg=f"Project ID '{workflow_data.project_id}' already exists and belongs to another user",
                    data=None,
                )

            workflow = await service.update_workflow(workflow_data, user_id)
            action = "updated"
        else:
            # 创建新工作流
            workflow = await service.create_workflow(workflow_data, user_id)
            action = "created"

        # 转换为可序列化的字典
        workflow_dict = workflow.to_dict()

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg=f"Workflow {action} successfully",
            data={"workflow": workflow_dict, "action": action},
        )
    except Exception as e:
        logger.error(f"Error creating/updating workflow: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to create or update workflow", data=None)


@router.get(
    "/get",
    response_model=StandardResponse,
    summary="获取所有工作流",
    description="获取当前用户的所有工作流列表",
)
async def get_workflows(
    pageNo: int = Query(1, ge=1, description="获取哪一页"),
    pageSize: int = Query(100, ge=1, le=100, description="一页有多少条记录"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WorkflowService = Depends(get_workflow_service),
):
    """获取工作流列表"""
    try:
        skip = (pageNo - 1) * pageSize
        workflows = await service.get_workflows(user_id, skip, pageSize)
        workflow_dicts = []
        personal_total = 0
        public_total = 0
        for workflow in workflows:
            workflow_dicts.append(workflow.to_dict())
            if not workflow.example_project_id:
                personal_total += 1
            else:
                public_total += 1

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={
                "total": len(workflow_dicts),
                "personal_total": personal_total,
                "public_total": public_total,
                "records": workflow_dicts,
            },
        )
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflows",
        )


@router.get(
    "/get/{project_id}",
    response_model=StandardResponse,
    summary="获取指定工作流详情",
    description="获取指定project_id的工作流详细信息",
)
async def get_workflow(
    project_id: str = Path(..., description="项目ID"),
    service: WorkflowService = Depends(get_workflow_service),
):
    """获取工作流详情"""
    try:
        workflow = await service.get_workflow(project_id, None)
        if not workflow:
            # 改成成功返回code，前端处理
            return StandardResponse(
                code=ResCode.SUCCESS,
                msg=f"Workflow with project_id {project_id} not found",
                data=None,
            )
        workflow_dict = workflow.to_dict()
        return StandardResponse(code=ResCode.SUCCESS, msg="", data={"workflow": workflow_dict})
    except Exception as e:
        logger.error(f"Error getting workflow {project_id}: {str(e)}")
        return StandardResponse(code=ResCode.SUCCESS, msg="Failed to get workflow", data=None)


@router.post(
    "/execute",
    response_model=StandardResponse,
    summary="同步执行工作流（等待结果）",
    description="同步执行指定的工作流，等待执行结果。如果执行时间过长，会返回202状态码，建议使用异步接口",
)
async def execute_workflow(
    execution_data: ExecutionCreate,
    user_id: str = Depends(get_user_id_from_api_key),
    workflow_service: WorkflowService = Depends(get_workflow_service),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """同步执行工作流"""
    try:
        # 检查工作流是否存在
        workflow = await workflow_service.get_workflow(execution_data.project_id, user_id)
        if not workflow:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"Workflow with project_id {execution_data.project_id} not found",
                data=None,
            )
        execution_data.project_id = workflow.project_id
        logger.info(f"[execute_workflow] project_id: {execution_data.project_id}")
        # 使用workflow默认version
        if not execution_data.version:
            execution_data.version = workflow.version

        # 执行工作流，设置超时参数
        execution = await execution_service.execute_workflow(
            execution_data=execution_data,
            user_id=user_id,
            wait=True,
            workflow_timeout=600,  # 工作流执行超时10分钟（同步执行）
        )

        # 如果执行中途没有完成（状态仍为RUNNING），返回202
        if execution.status == ExecutionStatus.RUNNING.value:
            return StandardResponse(
                code=ResCode.SUCCESS,
                msg="Execution is still in progress, please check status using execution ID",
                data={"execution": execution.to_dict()},
            )

        return StandardResponse(code=ResCode.SUCCESS, msg="", data={"execution": execution.to_dict()})
    except Exception as e:
        logger.error(f"Error executing workflow {execution_data.project_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to execute workflow", data=None)


@router.post(
    "/execute-async",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="异步执行工作流（立即返回任务ID）",
    description="异步执行指定的工作流，立即返回执行ID，可通过执行ID查询执行状态",
)
async def execute_workflow_async(
    execution_data: ExecutionCreate,
    user_id: str = Depends(get_user_id_from_api_key),
    user_service: UserService = Depends(get_user_service),
    workflow_service: WorkflowService = Depends(get_workflow_service),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """异步执行工作流"""
    try:
        if execution_data.phone_number:
            # Agent复制逻辑
            # 调用外部服务获取user_id
            user_info = await user_service.get_user_info(execution_data.phone_number)
            if not user_info:
                logger.error(f"用户获取API_KEY失败，phone: {execution_data.phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户获取API_KEY失败",
                )

            # 复制到 sub_user_id
            sub_user_id = user_info.get("user_id")

            # 调用外部服务进行复制
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://robot-service:8004/api/robot/astron-agent/copy-robot",
                    json={
                        "robotId": str(execution_data.project_id),
                        "version": execution_data.version,
                        "targetPhone": execution_data.phone_number,
                    },
                    headers={"X-API-Key": "zyzhou666!"},
                )
                if response.status_code == 200:
                    result = response.json().get("data")
                    logger.info(f"复制工作流结果: {result}")
                    if not result:
                        return StandardResponse(
                            code=ResCode.ERR,
                            msg=response.json().get("message"),
                            data=None,
                        )
                else:
                    logger.error(f"Failed to copy workflow: HTTP {response.status_code}, {response.text}")
                    return StandardResponse(code=ResCode.ERR, msg="请求后端拷贝工作流接口失败", data=None)

            workflow_data = WorkflowBase(
                project_id=result.get("robotId"),
                version=result.get("version"),
                name=result.get("name", ""),
                english_name=result.get("english_name", ""),
                description=result.get("description", ""),
                status=result.get("status", 1),
                parameters=json.dumps(result.get("parameters", []), ensure_ascii=False),
            )

            # 先检查是否已存在相同 project_id 的工作流
            existing_workflow = await workflow_service.get_workflow(workflow_data.project_id)

            if existing_workflow:
                # 如果存在，检查是否属于当前用户
                if existing_workflow.user_id != sub_user_id:
                    return StandardResponse(
                        code=ResCode.ERR,
                        msg=f"Project ID '{workflow_data.project_id}' already exists and belongs to another user",
                        data=None,
                    )

                workflow = await workflow_service.update_workflow(workflow_data, sub_user_id)
            else:
                # 创建新工作流
                workflow = await workflow_service.create_workflow(workflow_data, sub_user_id)

            user_id = sub_user_id
            execution_data.project_id = workflow.project_id
            # 复制的不指定version，指定了下发到执行器运行时会报错
            execution_data.version = None

        else:
            # 检查工作流是否存在
            workflow = await workflow_service.get_workflow(execution_data.project_id, user_id)
            if not workflow:
                return StandardResponse(
                    code=ResCode.ERR,
                    msg=f"Workflow with project_id {execution_data.project_id} not found",
                    data=None,
                )

            if not execution_data.version:
                execution_data.version = workflow.version

            execution_data.project_id = workflow.project_id
            logger.info(f"[execute_workflow_async] project_id: {execution_data.project_id}")

        # 执行工作流，不等待结果
        execution = await execution_service.execute_workflow(
            execution_data=execution_data,
            user_id=user_id,
            wait=False,
            workflow_timeout=36000,  # 工作流执行超时10小时
        )

        return StandardResponse(code=ResCode.SUCCESS, msg="", data={"executionId": execution.id})
    except Exception as e:
        logger.error(f"Error executing workflow async {execution_data.project_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to execute workflow asynchronously", data=None)


@router.post(
    "/stop-current",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="停止当前工作流",
    description="停止当前工作流",
)
async def stop_current_workflow(user_id: str = Depends(get_user_id_from_api_key)):
    """停止当前工作流"""
    import asyncio

    from rpawebsocket.ws import BaseMsg

    from app.dependencies import get_ws_service

    try:
        # 模拟异步工作流执行
        # 实际项目中可能涉及调用外部系统、处理数据等操作
        # 回调事件
        websocket_service = await get_ws_service()
        logger.info("input user_id: %s", user_id)

        wait = asyncio.Event()
        res = {}
        res_e = None

        def callback(watch_msg: BaseMsg | None = None, e: Exception | None = None):
            nonlocal wait, res, res_e
            if watch_msg:
                res = watch_msg.data
                logger.info("Received response for stop_current: %s", res)
            if e:
                res_e = e
                logger.error("Received error for stop_current: %s", e)
            wait.set()

        base_msg = BaseMsg(
            channel="remote",
            key="stop_current",
            uuid="$root$",
            send_uuid=f"{user_id}",
            need_reply=True,
            data={},
        ).init()

        await websocket_service.ws_manager.send_reply(base_msg, 10 * 3600, callback)

        # 等待
        await wait.wait()

        # 假设工作流执行成功
        if res.get("code") == "0000":
            return StandardResponse(code=ResCode.SUCCESS, msg="停止成功", data={})
        elif res.get("code") == "5001":
            return StandardResponse(code=ResCode.ERR, msg="停止失败或没有正在运行的机器人", data=res_e)

    except Exception as e:
        logger.exception("Error in stop_current for %s", e)
        raise


@router.get(
    "/get-astron",
    response_model=StandardResponse,
    summary="获取星辰Agent所有工作流",
    description="获取绑定了的星辰Agent的所有工作流列表",
)
async def get_astron_workflows(
    user_id: str = Depends(get_user_id_from_header),
    api_key_service: AstronApiKeyService = Depends(get_astron_api_key_service),
    workflow_service: WorkflowService = Depends(get_workflow_service),
):
    """获取星辰Agent所有工作流"""
    try:
        astron_auths = await api_key_service.get_all_astron_agents(user_id)
        total_workflows = []
        for astron_record in astron_auths:
            auth_id = astron_record.get("id")
            app_id = astron_record.get("app_id")
            api_key = astron_record.get("api_key")
            api_secret = astron_record.get("api_secret")
            workflows = await workflow_service.get_astron_workflows(auth_id, app_id, api_key, api_secret)
            total_workflows.extend(workflows)

        return StandardResponse(
            code=ResCode.SUCCESS, msg="获取成功", data={"total": len(total_workflows), "records": total_workflows}
        )
    except Exception as e:
        logger.error(f"Error getting Astron workflows: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to get Astron workflows", data=None)


@router.post(
    "/copy-workflow",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="复制工作流",
    description="复制指定的工作流到目标手机号码",
)
async def copy_workflow(
    copy_data: WorkflowCopyRequest,
    user_id: str = Depends(get_user_id_from_api_key),
):
    """复制工作流"""
    try:
        # 调用外部服务进行复制
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://robot-service:8004/api/astron-agent/copy-robot",
                json={
                    "robotId": str(copy_data.project_id),
                    "version": copy_data.version,
                    "targetPhone": copy_data.phone_number,
                },
            )

            if response.status_code == 200:
                result = response.json()
                return StandardResponse(code=ResCode.SUCCESS, msg="工作流复制成功", data=result)
            else:
                logger.error(f"Failed to copy workflow: HTTP {response.status_code}, {response.text}")
                return StandardResponse(code=ResCode.ERR, msg=f"复制失败: HTTP {response.status_code}", data=None)

    except httpx.RequestError as e:
        logger.error(f"Request error copying workflow: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="网络请求失败", data=None)
    except Exception as e:
        logger.error(f"Error copying workflow: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="复制工作流失败", data=None)
