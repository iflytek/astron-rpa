from fastapi import Depends, Header, HTTPException, Security, status # Added status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.services.websocket import WsManagerService, WsService
from app.services.workflow import WorkflowService
from app.services.execution import ExecutionService
from app.services.api_key import ApiKeyService
from app.database import get_db
from app.redis import get_redis
from app.models.api_key import OpenAPIDB
from app.utils.api_key import APIKeyUtils
from sqlalchemy.future import select
from typing import Dict, List, Optional
from datetime import datetime
import os

# 全局 WsManagerService 单例实例
_ws_manager_service: WsManagerService | None = None


def get_user_id_from_header(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    user_id: str | None = Header(default=None, alias="user_id"),
) -> str:
    """
    从请求头中获取用户ID，优先解析 X-User-Id，如果不存在则解析 user_id
    """
    header_user_id = x_user_id or user_id

    if header_user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Missing X-User-Id or user_id header.",
        )
    return header_user_id


API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)

def extract_api_key_from_request(ctx) -> Optional[str]:
    """从请求上下文中提取API_KEY"""

    # 尝试多种方式获取查询参数
    query_params = ctx.request.query_params

    if query_params:
        # 如果是字典类型
        if isinstance(query_params, dict):
            return query_params.get('key')

        # 如果是QueryParams对象（Starlette）
        if hasattr(query_params, 'get'):
            return query_params.get('key')

        # 如果是字符串类型的查询字符串
        if isinstance(query_params, str):
            from urllib.parse import parse_qs
            parsed = parse_qs(query_params)
            key_values = parsed.get('key', [])
            return key_values[0] if key_values else None
    return None


async def get_user_id_from_api_key(
    api_key_header: str = Security(API_KEY_HEADER),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    从 Authorization 请求头中获取 API Key，查询数据库得到 user_id
    """
    if api_key_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = api_key_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = parts[1]

    # 使用前缀匹配和哈希验证
    keys = await db.execute(
        select(OpenAPIDB).where(
            OpenAPIDB.prefix == api_key[:8], 
            OpenAPIDB.is_active == 1
        )
    )
    api_keys = keys.scalars().all()
    
    for key in api_keys:
        hashed_key = key.api_key
        if APIKeyUtils.verify_api_key(api_key, hashed_key):
            return str(key.user_id)
    
    # 如果没有找到匹配的API key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or inactive API key",
        headers={"WWW-Authenticate": "Bearer"},
    )


# 注意：get_uid_from_raw_key 函数已经被移动到 app.services.streamable_mcp.ToolsConfig 类中
# 以避免创建多个数据库连接实例


async def get_workflow_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> WorkflowService:
    """提供WorkflowService实例的依赖项"""
    return WorkflowService(db, redis)


async def get_execution_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> ExecutionService:
    """提供ExecutionService实例的依赖项"""
    return ExecutionService(db, redis)


async def get_api_key_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> ApiKeyService:
    """提供ApiKeyService实例的依赖项"""
    return ApiKeyService(db, redis)

async def get_ws_service() -> WsManagerService:
    """提供 WsManagerService 单例实例的依赖项"""
    global _ws_manager_service
    if _ws_manager_service is None:
        # 在多worker环境下，每个进程都有自己的实例
        # 这是正常的，因为WebSocket连接是进程级别的
        worker_id = os.getpid()
        _ws_manager_service = WsManagerService()
        # 可以在这里添加worker标识，便于调试
        _ws_manager_service.worker_id = worker_id
    return _ws_manager_service


async def get_user_id_with_fallback(
    api_key_header: str = Security(API_KEY_HEADER),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    user_id: str | None = Header(default=None, alias="user_id"),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    按优先级获取用户ID：
    1. 首先尝试从Authorization Bearer token中获取API key并验证
    2. 如果没有API key，则从X-User-Id或user_id header中获取
    3. 如果都没有，则抛出401错误
    
    使用示例：
    @router.get("/example")
    async def example_endpoint(
        user_id: str = Depends(get_user_id_with_fallback)
    ):
        return {"user_id": user_id}
    """
    # 首先尝试从API key获取用户ID
    if api_key_header:
        try:
            parts = api_key_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                api_key = parts[1]
                
                # 使用前缀匹配和哈希验证
                keys = await db.execute(
                    select(OpenAPIDB).where(
                        OpenAPIDB.prefix == api_key[:8], 
                        OpenAPIDB.is_active == 1
                    )
                )
                api_keys = keys.scalars().all()
                
                for key in api_keys:
                    hashed_key = key.api_key
                    if APIKeyUtils.verify_api_key(api_key, hashed_key):
                        return str(key.user_id)
        except Exception as e:
            # 如果API key验证失败，继续尝试header方式
            pass
    
    # 如果API key验证失败或不存在，尝试从header获取
    header_user_id = x_user_id or user_id
    if header_user_id:
        return header_user_id
    
    # 如果都没有，抛出401错误
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please provide either a valid API key in Authorization header or user_id in X-User-Id/user_id header.",
        headers={"WWW-Authenticate": "Bearer"},
    )
