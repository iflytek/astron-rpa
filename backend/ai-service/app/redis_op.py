from redis.asyncio import ConnectionPool, Redis
from typing import AsyncGenerator
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
redis_pool: ConnectionPool = None

async def init_redis_pool():
    global redis_pool
    try:
        redis_pool = ConnectionPool.from_url(
            get_settings().REDIS_URL,
            decode_responses=True,
            encoding="utf-8",
            max_connections=10,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # 测试连接
        redis = Redis(connection_pool=redis_pool)
        await redis.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

async def close_redis_pool():
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None
        logger.info("Redis connection closed")

async def get_redis() -> AsyncGenerator[Redis, None]:
    global redis_pool
    if redis_pool is None:
        raise RuntimeError("Redis pool is not initialized. Call init_redis_pool() first.")
    
    redis = Redis(connection_pool=redis_pool)
    try:
        yield redis
    finally:
        # Connections are returned to pool automatically
        pass