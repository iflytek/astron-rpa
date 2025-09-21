from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.services.execution import ExecutionService
from app.dependencies import get_user_id_from_api_key, get_execution_service
from app.logger import get_logger
from app.schemas import StandardResponse, ResCode

logger = get_logger(__name__)

router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.get(
    "/{execution_id}",
    response_model=StandardResponse,
    summary="查询异步执行的进度和结果",
    description="查询工作流执行的状态和结果"
)
async def get_execution(
    execution_id: str = Path(..., description="执行记录ID"),
    user_id: str = Depends(get_user_id_from_api_key),
    service: ExecutionService = Depends(get_execution_service)
):
    """获取执行记录"""
    try:
        execution = await service.get_execution(execution_id, user_id)
        if not execution:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"Execution with ID {execution_id} not found",
                data=None
            )
        
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"execution": execution.to_dict()}
        )
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {str(e)}")
        return StandardResponse(
            code=ResCode.ERR,
            msg="Failed to get execution",
            data=None
        )
