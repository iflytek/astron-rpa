from fastapi import APIRouter, Depends, status

from app.dependencies import check_user_id_equality, get_user_id_from_api_key
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse

logger = get_logger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get(
    "/local-check",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="本地健康检查",
    description="调用本地路由，检查本地路由带的user_id跟API_KEY是否匹配",
)
async def local_check(
    equality: bool = Depends(check_user_id_equality),
):
    """健康检查接口"""
    if equality:
        logger.info("本地RPA正常启动")

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="本地RPA正常启动",
            data={"equality": equality},
        )
    else:
        return StandardResponse(
            code=ResCode.ERR,
            msg="本地RPA启动账号与Agent账号不匹配",
            data={"equality": equality},
        )


@router.get(
    "/remote-check",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="远端健康检查",
    description="检查API_KEY对应的user是否客户端在线",
)
async def remote_check(
    user_id: str = Depends(get_user_id_from_api_key),
):
    """健康检查接口"""

    from app.dependencies import get_ws_service

    websocket_service = await get_ws_service()
    if user_id not in websocket_service.ws_manager.conns:
        return StandardResponse(
            code=ResCode.ERR,
            msg="该用户客户端未启动！",
            data=False,
        )
    else:
        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="该用户客户端正常启动！",
            data=True,
        )
