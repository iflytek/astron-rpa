from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_api_key_service, get_user_id_from_header
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse
from app.schemas.api_key import ApiKeyCreate, ApiKeyDelete
from app.services.api_key import ApiKeyService

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
    description="获取当前用户的所有 API Key 列表",
)
async def get_api_keys(
    pageNo: int = Query(1, ge=1, description="获取哪一页"),
    pageSize: int = Query(100, ge=1, le=50, description="一页有多少条记录"),
    user_id: str = Depends(get_user_id_from_header),
    service: ApiKeyService = Depends(get_api_key_service),
):
    """获取 API Key 列表"""
    try:
        api_keys = await service.get_api_keys(user_id, pageNo, pageSize)
        return StandardResponse(code=ResCode.SUCCESS, msg="", data={"total": len(api_keys), "records": api_keys})
    except Exception as e:
        logger.error(f"Error getting API keys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get API keys",
        )


@router.post(
    "/create",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新的 API Key",
    description="为当前用户创建新的 API Key",
)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    user_id: str = Depends(get_user_id_from_header),
    service: ApiKeyService = Depends(get_api_key_service),
):
    """创建 API Key"""
    try:
        api_key = await service.create_api_key(api_key_data, user_id)
        return StandardResponse(code=ResCode.SUCCESS, msg="", data={"api_key": api_key})
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )


@router.post(
    "/remove",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="删除指定 API Key",
    description="删除指定的 API Key",
)
async def delete_api_key(
    request: ApiKeyDelete,
    user_id: str = Depends(get_user_id_from_header),
    service: ApiKeyService = Depends(get_api_key_service),
):
    """删除 API Key"""
    try:
        api_key_id = int(request.id)  # 转换为 int 类型
        success = await service.delete_api_key(str(api_key_id), user_id)
        if not success:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"API key with ID {api_key_id} not found",
                data=None,
            )

        return StandardResponse(code=ResCode.SUCCESS, msg="", data=None)
    except Exception as e:
        logger.error(f"Error deleting API key {api_key_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to delete API key", data=None)


@router.post(
    "/create-astron",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建星辰Agent",
    description="为当前用户创建星辰Agent",
)
async def create_astron_agent(
    astron_agent_data: AstronAgentCreate,
    user_id: str = Depends(get_user_id_from_header),
    service: AstronApiKeyService = Depends(get_astron_api_key_service),
):
    """创建星辰Agent"""
    try:
        # 验证数据
        if not astron_agent_data.api_key or not astron_agent_data.api_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="api_key 和 api_secret 不能为空",
            )

        # GET http://dev-agent.xfyun.cn/xingchen-api/manage/workflow/get_info
        # X-Consumer-Username [appId]
        # Authorization [Bearer api_key:api_secret]

        # 调用服务层创建星辰Agent
        astron_auth = await service.create_astron_agent(astron_agent_data, user_id)

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="星辰Agent授权创建成功",
            data={
                "id": astron_auth.id,
                "created_at": astron_auth.created_at,
                "updated_at": astron_auth.updated_at,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating AstronAgent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建星辰Agent认证失败",
        )


@router.get(
    "/get-astron",
    response_model=StandardResponse,
    summary="获取所有星辰Agent",
    description="获取当前用户的所有星辰Agent列表",
)
async def get_astron_agents(
    pageNo: int = Query(1, ge=1, description="获取哪一页"),
    pageSize: int = Query(10, ge=1, le=50, description="一页有多少条记录"),
    user_id: str = Depends(get_user_id_from_header),
    service: AstronApiKeyService = Depends(get_astron_api_key_service),
):
    """获取星辰Agent列表"""
    try:
        astron_agents = await service.get_astron_agents(user_id, pageNo, pageSize)
        return StandardResponse(
            code=ResCode.SUCCESS, msg="获取成功", data={"total": len(astron_agents), "records": astron_agents}
        )
    except Exception as e:
        logger.error(f"Error getting AstronAgents: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get AstronAgents")


@router.get(
    "/get-astron-by-id",
    response_model=StandardResponse,
    summary="根据ID获取星辰Agent",
    description="根据ID获取指定的星辰Agent信息",
)
async def get_astron_agent_by_id(
    id: int = Query(..., description="星辰Agent的ID"),
    user_id: str = Depends(get_user_id_from_header),
    service: AstronApiKeyService = Depends(get_astron_api_key_service),
):
    """根据ID获取星辰Agent"""
    try:
        astron_agent = await service.get_astron_agent_by_id(id, user_id)
        if astron_agent is None:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"星辰Agent with ID {id} not found",
                data=None,
            )

        return StandardResponse(code=ResCode.SUCCESS, msg="获取成功", data=astron_agent)
    except Exception as e:
        logger.error(f"Error getting AstronAgent by id {id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get AstronAgent")


@router.post(
    "/remove-astron",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="删除指定星辰Agent",
    description="删除指定的星辰Agent",
)
async def delete_astron_agent(
    request: AstronAgentDelete,
    user_id: str = Depends(get_user_id_from_header),
    service: AstronApiKeyService = Depends(get_astron_api_key_service),
):
    """删除星辰Agent"""
    try:
        astron_agent_id = str(request.id)  # 转换为字符串类型
        success = await service.delete_astron_agent(astron_agent_id, user_id)
        if not success:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"AstronAgent with ID {astron_agent_id} not found",
                data=None,
            )

        return StandardResponse(code=ResCode.SUCCESS, msg="删除成功", data=None)
    except Exception as e:
        logger.error(f"Error deleting AstronAgent {astron_agent_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to delete AstronAgent", data=None)


@router.post(
    "/update-astron",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="更新指定星辰Agent",
    description="更新指定的星辰Agent信息",
)
async def update_astron_agent(
    request: AstronAgentUpdate,
    user_id: str = Depends(get_user_id_from_header),
    service: AstronApiKeyService = Depends(get_astron_api_key_service),
):
    """更新星辰Agent"""
    astron_agent_id = str(request.id)  # 转换为字符串类型
    try:
        success = await service.update_astron_agent(astron_agent_id, user_id, request)
        if not success:
            return StandardResponse(
                code=ResCode.ERR,
                msg=f"AstronAgent with ID {astron_agent_id} not found",
                data=None,
            )

        return StandardResponse(code=ResCode.SUCCESS, msg="更新成功", data=None)
    except Exception as e:
        logger.error(f"Error updating AstronAgent {astron_agent_id}: {str(e)}")
        return StandardResponse(code=ResCode.ERR, msg="Failed to update AstronAgent", data=None)
