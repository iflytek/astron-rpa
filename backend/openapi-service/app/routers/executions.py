from fastapi import APIRouter, Depends, Path, Query

from app.dependencies import get_execution_service, get_user_id_from_api_key
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse
from app.services.execution import ExecutionService

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
        executions_dict = [execution.to_dict() for execution in executions]

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
        logger.error(f"Error getting executions for user {user_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to get executions", data=None)


@router.get(
    "/{execution_id}",
    response_model=StandardResponse,
    summary="查询异步执行的进度和结果",
    description="查询工作流执行的状态和结果",
)
async def get_execution(
    execution_id: str = Path(..., description="执行记录ID"),
    user_id: str = Depends(get_user_id_from_api_key),
    service: ExecutionService = Depends(get_execution_service),
):
    """获取执行记录"""
    try:
        execution = await service.get_execution(execution_id, user_id)
        if not execution:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"Execution with ID {execution_id} not found",
                data=None,
            )

        return StandardResponse(code=ResCode.SUCCESS, msg="", data={"execution": execution.to_dict()})
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to get execution", data=None)
