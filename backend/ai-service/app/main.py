from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import create_db_and_tables
from app.redis_op import init_redis_pool, close_redis_pool
from app.internal import admin
from app.routers.v1 import chat
from app.routers.v1 import models
from app.routers import ocr
from app.routers import jfbym
from app.middlewares.tracing import RequestTracingMiddleware
from app.logger import get_logger
import uvicorn

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

app.add_middleware(RequestTracingMiddleware)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed!")
    return {"message": "Hello Bigger Applications!"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=6688,
        proxy_headers=True,
    )
