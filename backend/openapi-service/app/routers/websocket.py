import asyncio
from app.dependencies import get_ws_service
from app.logger import get_logger
from app.schemas import StandardResponse, ResCode
from fastapi import APIRouter, Depends, WebSocket
from rpawebsocket.ws import Conn, IWebSocket, BaseMsg
from app.services.websocket import WsManagerService, WsService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

@router.websocket("")
async def websocket_endpoint(ws: WebSocket, ws_mg_service: WsManagerService = Depends(get_ws_service)):
    logger.info("ws endpoint called!!!!")
    headers = ws.headers
    user_id = headers.get("user_id")  # 或 headers.get("user_id")，取决于实际请求头字段名
    logger.info("user_id: {}".format(user_id))
    if not user_id:
        await ws.close(code=1008, reason="Missing 'user_id' in headers")
        return
    await ws.accept()
    ws_mg = ws_mg_service.ws_manager
    await asyncio.gather(
        ws_mg.listen(user_id, Conn(ws=WsService(ws))),
        ws_mg.start_ping(),
        ws_mg.clear_watch()
    )