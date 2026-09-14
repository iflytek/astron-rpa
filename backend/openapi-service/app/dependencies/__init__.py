import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.redis import get_redis
from app.security.api_key import APIKeyAuthenticationError, extract_api_key, has_api_key_credential, validate_api_key
from app.services.api_key import ApiKeyService, AstronApiKeyService
from app.services.execution import ExecutionService
from app.services.user import UserService
from app.services.websocket import WsManagerService, WsService
from app.services.workflow import WorkflowService

# 全局 WsManagerService 单例实例
_ws_manager_service: WsManagerService | None = None


def authentication_error() -> HTTPException:
    return HTTPException(401, "Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})


def get_user_id_from_header(
    request: Request,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    user_id: str | None = Header(default=None, alias="user_id"),
) -> str:
    """Identity asserted by the session-authenticating gateway/private services.

    The service port must remain private. The gateway strips caller identity
    headers before authentication and never admits API keys to management routes.
    """
    if has_api_key_credential(request.scope):
        raise authentication_error()
    if x_user_id and user_id and x_user_id != user_id:
        raise authentication_error()
    identity = x_user_id or user_id
    if not identity or not identity.strip():
        raise authentication_error()
    return identity


async def verify_register_bearer_token() -> str:
    # The legacy public token plus phone lookup could issue another user's key.
    # There is no delegated identity/permission model for this entry point.
    raise HTTPException(403, "Legacy key provisioning is disabled; use authenticated API key management")


async def verify_getkey_bearer_token() -> str:
    return await verify_register_bearer_token()


async def get_user_id_from_api_key(request: Request, db: Annotated[AsyncSession, Depends(get_db)]) -> str:
    try:
        raw_key = extract_api_key(request.scope)  # REST never accepts URL keys.
        identity = await validate_api_key(db, raw_key)
    except APIKeyAuthenticationError:
        raise authentication_error() from None
    except Exception:
        # No database exception or credential is returned/logged here.
        raise HTTPException(503, "Authentication service unavailable") from None
    if not identity:
        raise authentication_error()
    return identity


async def get_user_id_with_fallback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    user_id: str | None = Header(default=None, alias="user_id"),
) -> str:
    # An explicit invalid/malformed/conflicting API credential never falls back
    # to a caller-supplied identity, even when a session cookie is also present.
    if has_api_key_credential(request.scope):
        return await get_user_id_from_api_key(request, db)
    return get_user_id_from_header(request, x_user_id, user_id)


async def check_user_id_equality(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: str | None = Header(default=None, alias="user_id"),
) -> bool:
    identity = await get_user_id_from_api_key(request, db)
    if not user_id:
        raise authentication_error()
    # This is a diagnostic comparison, never an authorization identity.
    return identity == user_id


async def get_workflow_service(
    db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> WorkflowService:
    """提供WorkflowService实例的依赖项"""
    return WorkflowService(db, redis)


async def get_execution_service(
    db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> ExecutionService:
    """提供ExecutionService实例的依赖项"""
    return ExecutionService(db, redis)


async def get_api_key_service(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)) -> ApiKeyService:
    """提供ApiKeyService实例的依赖项"""
    return ApiKeyService(db, redis)


async def get_astron_api_key_service(
    db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)
) -> AstronApiKeyService:
    """提供XcApiKeyService实例的依赖项"""
    return AstronApiKeyService(db, redis)


async def get_user_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> UserService:
    """提供UserService实例的依赖项"""
    return UserService(db, redis, api_key_service)


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
