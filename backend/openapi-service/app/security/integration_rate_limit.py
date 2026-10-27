"""Optional per-authenticated-owner limit shared across MCP/REST and replicas."""

import asyncio
import hashlib

from fastapi import HTTPException
from redis.asyncio import Redis

from app.config import get_settings
from app.services.observability import increment

_WINDOW = """
local n = redis.call('incr', KEYS[1])
if n == 1 then redis.call('expire', KEYS[1], 60) end
return {n, redis.call('ttl', KEYS[1])}
"""


async def enforce_rate_limit(owner):
    limit = get_settings().INTEGRATION_RATE_PER_MINUTE
    if limit <= 0:
        return
    from app import redis as redis_module

    if redis_module.redis_pool is None:
        raise HTTPException(503, {"code": "RATE_LIMIT_UNAVAILABLE"})
    client = Redis(connection_pool=redis_module.redis_pool)
    key = "astron:rate:v1:" + hashlib.sha256(str(owner).encode()).hexdigest()
    try:
        async with asyncio.timeout(2):
            count, ttl = await client.eval(_WINDOW, 1, key)
    except Exception:
        raise HTTPException(503, {"code": "RATE_LIMIT_UNAVAILABLE"}) from None
    if count > limit:
        increment("astron_rate_limited_total")
        raise HTTPException(429, {"code": "RATE_LIMITED"}, headers={"Retry-After": str(max(1, ttl))})
