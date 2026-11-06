from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.dependencies import check_user_id_equality, get_user_id_from_api_key
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse

logger = get_logger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


def monitoring_authorized(authorization: str | None = Header(default=None)):
    import secrets

    from app.config import get_settings

    token = get_settings().MONITORING_TOKEN
    if (
        not token
        or len(token) < 32
        or not secrets.compare_digest((authorization or "").encode(), ("Bearer " + token).encode())
    ):
        raise HTTPException(404, "Not found")


@router.get("/metrics", dependencies=[Depends(monitoring_authorized)])
async def metrics():
    from app.dependencies import get_ws_service
    from app.services.observability import render_metrics

    manager = (await get_ws_service()).ws_manager
    online = len(manager.router.local) if manager.router else sum(bool(items) for items in manager.conns.values())
    healthy = True
    try:
        await ready()
    except HTTPException:
        healthy = False
    return PlainTextResponse(render_metrics(online, healthy), media_type="text/plain; version=0.0.4")


@router.get("/ready", dependencies=[Depends(monitoring_authorized)])
async def ready():
    import asyncio

    from redis.asyncio import Redis
    from sqlalchemy import text

    from app import redis as redis_module
    from app.database import AsyncSessionLocal
    from app.dependencies import get_ws_service

    try:
        async with asyncio.timeout(3):
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1"))
            if redis_module.redis_pool is None:
                raise RuntimeError
            await Redis(connection_pool=redis_module.redis_pool).ping()
            manager = (await get_ws_service()).ws_manager
            if manager.router and not manager.router.ready:
                raise RuntimeError
    except Exception:
        raise HTTPException(503, {"code": "SERVICE_NOT_READY"}) from None
    return {"ready": True}


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
    if not await websocket_service.ws_manager.online(user_id):
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
