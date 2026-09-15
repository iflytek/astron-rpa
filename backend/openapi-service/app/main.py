import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.dependencies import get_ws_service
from app.internal import admin
from app.logger import get_logger
from app.middlewares.tracing import RequestTracingMiddleware
from app.redis import close_redis_pool, init_redis_pool
from app.routers import api_keys, executions, healthcheck, user, websocket, workflows
from app.routers.streamable_mcp import (
    handle_streamable_http,
    session_manager,
    tools_config,
)
from app.services.execution_management import recover_executions

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
        recovery = asyncio.create_task(recover_executions(), name="execution-recovery")
        logger.info("Application started with StreamableHTTP session manager!")
        try:
            yield
        finally:
            recovery.cancel()
            await asyncio.gather(recovery, return_exceptions=True)
            logger.info("Application shutting down...")

            # 清理 tools_config 连接
            await tools_config.cleanup_connections()
            logger.info("Tools config connections cleaned up")

            await close_redis_pool()
            logger.info(f"Worker {worker_id} shutting down")


app = FastAPI(title="RPA OpenAPI", version="1.2.0", lifespan=lifespan)

app.include_router(admin.router, prefix="/admin", tags=["admin"])

app.include_router(workflows.router)
app.include_router(executions.router)
app.include_router(api_keys.router)
app.include_router(healthcheck.router)
app.include_router(user.router)
app.include_router(websocket.router)
app.mount("/mcp", handle_streamable_http)  # APISIX增加路由，解决307重定向问题

app.add_middleware(RequestTracingMiddleware)


@app.exception_handler(RequestValidationError)
async def safe_request_validation_error(request, exc):
    # FastAPI otherwise includes rejected inputs in errors (including API keys,
    # passwords and workflow arguments). Keep locations/types for diagnostics.
    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {"loc": error["loc"], "type": error["type"], "msg": "Invalid request value"} for error in exc.errors()
            ]
        },
    )


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
