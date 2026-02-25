from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config import get_settings
from app.database import create_db_and_tables
from app.internal import admin
from app.logger import get_logger
from app.middlewares.tracing import RequestTracingMiddleware
from app.redis_op import close_redis_pool, init_redis_pool
from app.routers import computer_use, jfbym, ocr, smart_component
from app.routers.v1 import chat, models

# Ensure configuration is loaded
settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize connections
    await create_db_and_tables()
    await init_redis_pool()

    yield

    # Cleanup connections
    await close_redis_pool()


app = FastAPI(lifespan=lifespan)

app.include_router(admin.router, prefix="/admin", tags=["admin"])

app.include_router(ocr.router)
app.include_router(chat.router, prefix="/v1")
app.include_router(models.router, prefix="/v1")
app.include_router(jfbym.router)
app.include_router(smart_component.router)
app.include_router(computer_use.router)

app.add_middleware(RequestTracingMiddleware)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed!")
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8010,
        proxy_headers=True,
    )
