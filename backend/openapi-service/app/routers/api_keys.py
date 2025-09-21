from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from app.services.api_key import ApiKeyService
from app.schemas.api_key import ApiKeyCreate, ApiKeyDelete
from app.dependencies import get_user_id_from_header, get_api_key_service
from app.logger import get_logger
from app.schemas import StandardResponse, ResCode

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api-keys",
    tags=["api-key"],
    dependencies=[Depends(get_user_id_from_header)],
)


@router.get(
    "/get",
    response_model=StandardResponse,
    summary="获取所有 API Key",
    description="获取当前用户的所有 API Key 列表"
)
async def get_api_keys(
    pageNo: int = Query(1, ge=1, description="获取哪一页"),
    pageSize: int = Query(100, ge=1, le=50, description="一页有多少条记录"),
    user_id: str = Depends(get_user_id_from_header),
    service: ApiKeyService = Depends(get_api_key_service)
):
    """获取 API Key 列表"""
    try:
        api_keys = await service.get_api_keys(user_id, pageNo, pageSize)
        return StandardResponse(
                code=ResCode.SUCCESS,
                msg="",
                data={"total": len(api_keys), "records": api_keys}
            )
    except Exception as e:
        logger.error(f"Error getting API keys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API keys"
        )


@router.post(
    "/create",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新的 API Key",
    description="为当前用户创建新的 API Key"
)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    user_id: str = Depends(get_user_id_from_header),
    service: ApiKeyService = Depends(get_api_key_service)
):
    """创建 API Key"""
    try:
        api_key = await service.create_api_key(api_key_data, user_id)
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data={"api_key": api_key}
        )
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key"
        )


@router.post(
    "/remove",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="删除指定 API Key",
    description="删除指定的 API Key"
)
async def delete_api_key(
    request: ApiKeyDelete,
    user_id: str = Depends(get_user_id_from_header),
    service: ApiKeyService = Depends(get_api_key_service)
):
    """删除 API Key"""
    try:
        api_key_id = int(request.id)  # 转换为 int 类型
        success = await service.delete_api_key(str(api_key_id), user_id)
        if not success:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"API key with ID {api_key_id} not found",
                data=None
            )
        
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="",
            data=None
        )
    except Exception as e:
        logger.error(f"Error deleting API key {api_key_id}: {str(e)}")
        return StandardResponse(
            code=ResCode.ERR,
            msg="Failed to delete API key",
            data=None
        )
