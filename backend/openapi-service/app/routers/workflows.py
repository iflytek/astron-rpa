from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.services.websocket import WsManagerService
from app.services.workflow import WorkflowService
from app.services.execution import ExecutionService
from app.schemas.workflow import (
    WorkflowBase, WorkflowResponse, WorkflowListResponse,
    ExecutionCreate, ExecutionStatus
)
from app.dependencies import get_user_id_from_api_key, get_user_id_with_fallback, get_workflow_service, get_execution_service, get_user_id_from_header, get_ws_service
from app.logger import get_logger
from app.schemas import StandardResponse, ResCode

logger = get_logger(__name__)

router = APIRouter(
    prefix="/workflows",
    tags=["workflow"],
    # dependencies=[Depends(get_user_id_from_api_key)], 拆到后面
)


@router.post(
    "/upsert",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="创建或修改工作流",
    description="如果 project_id 不存在则创建新工作流，如果存在则更新现有工作流"
)
async def create_or_update_workflow(
    workflow_data: WorkflowBase,
    user_id: str = Depends(get_user_id_from_header),
    service: WorkflowService = Depends(get_workflow_service)
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
                    data=None
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
            data={"workflow": workflow_dict, "action": action}
        )
    except Exception as e:
        logger.error(f"Error creating/updating workflow: {str(e)}")
        return StandardResponse(
            code=ResCode.ERR,
            msg="Failed to create or update workflow",
            data=None
        )


@router.get(
    "/get",
    response_model=StandardResponse,
    summary="获取所有工作流",
    description="获取当前用户的所有工作流列表"
)
async def get_workflows(
    pageNo: int = Query(1, ge=1, description="获取哪一页"),
    pageSize: int = Query(100, ge=1, le=100, description="一页有多少条记录"),
    user_id: str = Depends(get_user_id_with_fallback),
    service: WorkflowService = Depends(get_workflow_service)
):
    """获取工作流列表"""
    try:
        skip = (pageNo - 1) * pageSize
        workflows = await service.get_workflows(user_id, skip, pageSize)
        workflow_dicts = []
        for workflow in workflows:
            workflow_dicts.append(workflow.to_dict())

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"total": len(workflow_dicts), "records": workflow_dicts}
        )
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflows"
        )


@router.get(
    "/get/{project_id}",
    response_model=StandardResponse,
    summary="获取指定工作流详情",
    description="获取指定project_id的工作流详细信息"
)
async def get_workflow(
    project_id: str = Path(..., description="项目ID"),
    service: WorkflowService = Depends(get_workflow_service)
):
    """获取工作流详情"""
    try:
        workflow = await service.get_workflow(project_id, None)
        if not workflow:
            # 改成成功返回code，前端处理
            return StandardResponse(
                code=ResCode.SUCCESS,
                msg=f"Workflow with project_id {project_id} not found",
                data=None
            )
        workflow_dict = workflow.to_dict()
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"workflow": workflow_dict}
        )
    except Exception as e:
        logger.error(f"Error getting workflow {project_id}: {str(e)}")
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="Failed to get workflow",
            data=None
        )


@router.post(
    "/execute",
    response_model=StandardResponse,
    summary="同步执行工作流（等待结果）",
    description="同步执行指定的工作流，等待执行结果。如果执行时间过长，会返回202状态码，建议使用异步接口"
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
                data=None
            )
        
        # 执行工作流，设置300秒超时，因为是同步所以设置长一点
        execution = await execution_service.execute_workflow(
            execution_data=execution_data, 
            user_id=user_id,
            wait=True,
            timeout=300
        )
        
        # 如果执行中途没有完成（状态仍为RUNNING），返回202
        if execution.status == ExecutionStatus.RUNNING.value:
            return StandardResponse(
                code=ResCode.SUCCESS,
                msg="Execution is still in progress, please check status using execution ID",
                data={"execution": execution.to_dict()}
            )
        
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"execution": execution.to_dict()}
        )
    except Exception as e:
        logger.error(f"Error executing workflow {execution_data.project_id}: {str(e)}")
        return StandardResponse(
            code=ResCode.ERR,
            msg="Failed to execute workflow",
            data=None
        )


@router.post(
    "/execute-async",
    response_model=StandardResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="异步执行工作流（立即返回任务ID）",
    description="异步执行指定的工作流，立即返回执行ID，可通过执行ID查询执行状态"
)
async def execute_workflow_async(
    execution_data: ExecutionCreate,
    user_id: str = Depends(get_user_id_from_api_key),
    workflow_service: WorkflowService = Depends(get_workflow_service),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    """异步执行工作流"""
    try:
        # 检查工作流是否存在
        workflow = await workflow_service.get_workflow(execution_data.project_id, user_id)
        if not workflow:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"Workflow with project_id {execution_data.project_id} not found",
                data=None
            )
        
        # 执行工作流，不等待结果
        execution = await execution_service.execute_workflow(
            execution_data=execution_data, 
            user_id=user_id,
            wait=False,
            timeout=60
        )
        
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"executionId": execution.id}
        )
    except Exception as e:
        logger.error(f"Error executing workflow async {execution_data.project_id}: {str(e)}")
        return StandardResponse(
            code=ResCode.ERR,
            msg="Failed to execute workflow asynchronously",
            data=None
        )


@router.get(
    "/../executions/{execution_id}",
    response_model=StandardResponse,
    summary="查询异步执行的进度和结果",
    description="查询工作流执行的状态和结果"
)
async def get_execution(
    execution_id: str = Path(..., description="执行记录ID"),
    user_id: str = Depends(get_user_id_from_api_key),
    execution_service: ExecutionService = Depends(get_execution_service)
):
    """获取执行记录"""
    try:
        execution = await execution_service.get_execution(execution_id, user_id)
        if not execution:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"Execution with ID {execution_id} not found",
                data=None
            )
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"execution": execution}
        )
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {str(e)}")
        return StandardResponse(
            code=ResCode.ERR,
            msg="Failed to get execution",
            data=None
        )
