from redis.asyncio import ConnectionPool, Redis
from typing import AsyncGenerator
from app.config import get_settings

redis_pool: ConnectionPool = None

async def init_redis_pool():
  global redis_pool
  redis_pool = ConnectionPool.from_url(
    get_settings().REDIS_URL,
    decode_responses=True,
    encoding="utf-8",
    max_connections=10,
  )

async def close_redis_pool():
  global redis_pool
  if redis_pool:
    await redis_pool.disconnect()
    redis_pool = None


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