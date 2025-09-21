import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator
from app.routers.streamable_mcp import handle_streamable_http, session_manager, tools_config
from app.redis import init_redis_pool, close_redis_pool
from app.internal import admin
from app.routers import websocket, workflows, executions, api_keys
from app.middlewares.tracing import RequestTracingMiddleware
from app.logger import get_logger
from app.dependencies import get_ws_service
import os

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Context manager for application lifespan."""
    # Initialize connections
    # await create_db_and_tables()

    await init_redis_pool()
    
    # 初始化 WsManagerService 单例实例
    worker_id = os.getpid()
    await get_ws_service()
    logger.info(f"WsManagerService singleton initialized for worker {worker_id}")

    # 使用 async with 管理 session_manager 的生命周期
    async with session_manager.run():
        logger.info("Application started with StreamableHTTP session manager!")
        try:
            yield
        finally:
            logger.info("Application shutting down...")
            
            # 清理 tools_config 连接
            await tools_config.cleanup_connections()
            logger.info("Tools config connections cleaned up")
            
            await close_redis_pool()
            logger.info(f"Worker {worker_id} shutting down")


app = FastAPI(
    title="RPA OpenAPI",
    version="1.2.0",
    lifespan=lifespan
)

app.include_router(admin.router, prefix="/admin", tags=["admin"])

app.include_router(workflows.router)
app.include_router(executions.router)
app.include_router(api_keys.router)
app.include_router(websocket.router)
app.mount("/mcp", handle_streamable_http) #APISIX增加路由，解决307重定向问题

app.add_middleware(RequestTracingMiddleware)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed!")

    return {"message": "Hello Bigger Applications!"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8020,
        proxy_headers=True,
    )
