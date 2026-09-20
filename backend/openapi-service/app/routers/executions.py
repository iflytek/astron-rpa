from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.dependencies import get_execution_service, get_user_id_from_api_key
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse
from app.security.workflow_authorization import WorkflowAccessError, external_execution_dict
from app.services.execution import ExecutionService
from app.services.workflow_control import WorkflowControlService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.get(
    "/get",
    response_model=StandardResponse,
    summary="获取执行记录列表（分页）",
    description="根据API_KEY获取用户ID，然后分页获取该用户的所有执行记录",
)
async def get_executions(
    pageNo: int = Query(1, ge=1, description="获取哪一页"),
    pageSize: int = Query(10, ge=1, le=100, description="一页有多少条记录"),
    user_id: str = Depends(get_user_id_from_api_key),
    service: ExecutionService = Depends(get_execution_service),
):
    """分页获取执行记录列表"""
    try:
        executions, total = await service.get_executions_by_user(user_id, pageNo, pageSize)
        executions_dict = [external_execution_dict(execution) for execution in executions]

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={
                "executions": executions_dict,
                "total": total,
                "pageNo": pageNo,
                "pageSize": pageSize,
                "total_pages": (total + pageSize - 1) // pageSize,  # 向上取整计算总页数
            },
        )
    except Exception as e:
        logger.error("Request failed: %s", type(e).__name__)  # noqa: TRY400 -- omit sensitive exception text
        return StandardResponse(code=ResCode.ERR, msg="Failed to get executions", data=None)


@router.get(
    "/{execution_id}",
    response_model=StandardResponse,
    summary="查询异步执行的进度和结果",
    description="查询工作流执行的状态和结果",
)
async def get_execution(
    response: Response,
    contract: Literal["1"] | None = Query(None),
    execution_id: str = Path(..., description="执行记录ID"),
    user_id: str = Depends(get_user_id_from_api_key),
    service: ExecutionService = Depends(get_execution_service),
):
    """获取执行记录"""
    try:
        execution = await service.get_authorized_execution(execution_id, user_id)
        if not execution:
            if contract == "1":
                raise HTTPException(404, detail={"code": "EXECUTION_NOT_FOUND"})
            response.status_code = status.HTTP_404_NOT_FOUND
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"Execution with ID {execution_id} not found",
                data=None,
            )

        data = {"execution": external_execution_dict(execution)}
        if contract == "1":
            data = {"snapshot": WorkflowControlService.execution_result(execution)}
        return StandardResponse(code=ResCode.SUCCESS, msg="", data=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Request failed: %s", type(e).__name__)  # noqa: TRY400 -- omit sensitive exception text
        return StandardResponse(code=ResCode.ERR, msg="Failed to get execution", data=None)


@router.post("/{execution_id}/cancel", response_model=StandardResponse)
async def cancel_execution(
    execution_id: str,
    user_id: Annotated[str, Depends(get_user_id_from_api_key)],
    service: Annotated[ExecutionService, Depends(get_execution_service)],
):
    try:
        execution = await service.request_cancellation(execution_id, user_id)
        return StandardResponse(
            code=ResCode.SUCCESS, msg="", data={"snapshot": WorkflowControlService.execution_result(execution)}
        )
    except WorkflowAccessError as exc:
        raise HTTPException(404 if exc.code == "EXECUTION_NOT_FOUND" else 403, detail={"code": exc.code}) from None
