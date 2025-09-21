from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.api_key import OpenAPIDB
from app.schemas.api_key import ApiKeyCreate
from typing import List, Optional
from uuid import uuid4
import secrets
from redis.asyncio import Redis
from datetime import datetime
import pytz
from app.utils.api_key import APIKeyUtils
from app.logger import get_logger

logger = get_logger(__name__)


class ApiKeyService:
    def __init__(self, db: AsyncSession, redis: Redis = None):
        self.db = db
        self.redis = redis
    
    async def _invalidate_api_keys_cache(self, user_id: str) -> None:
        """清除用户API Key缓存"""
        if self.redis:
            # 清除可能的所有分页缓存
            keys = await self.redis.keys(f"api_keys:{user_id}:*")
            if keys:
                await self.redis.delete(*keys)
    
    async def create_api_key(self, api_key_data: ApiKeyCreate, user_id: str) -> OpenAPIDB:
        """创建新API Key"""
        
        # 生成唯一ID和密钥
        api_key = APIKeyUtils.generate_api_key()
        logger.info(f"Generated API key: {api_key}")
        hashed_key = APIKeyUtils.hash_api_key(api_key)
        prefix = api_key[:8]
        name = api_key_data.name
        
        new_api_key = OpenAPIDB(
            user_id=user_id, 
            api_key=hashed_key, #数据库中不存真实API_KEY
            prefix=prefix,
            created_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None), 
            name=name, 
            is_active=1,
            updated_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None)
        )
        
        self.db.add(new_api_key)
        await self.db.flush()
        await self.db.refresh(new_api_key)
        
        # 清除缓存
        await self._invalidate_api_keys_cache(user_id)
        
        return api_key
    
    async def get_api_key(self, api_key_id: str, user_id: str = None) -> Optional[OpenAPIDB]:
        """获取指定API Key"""
        query = select(OpenAPIDB).where(OpenAPIDB.id == api_key_id)
        if user_id is not None:
            query = query.where(OpenAPIDB.user_id == user_id)
        query = query.where(OpenAPIDB.is_active == 1)  # 只返回激活状态的记录
            
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_api_keys(self, user_id: str, page_no: int = 0, page_size: int = 10) -> List[OpenAPIDB]:
        """获取API Key列表"""
        # 生成缓存键
        skip = (page_no - 1) * page_size
        cache_key = f"api_keys:{user_id}:{skip}:{page_size}"
        
        # 如果Redis可用，尝试从缓存获取
        if self.redis:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                # 实际项目中可能需要更复杂的序列化/反序列化方案
                pass
        
        # 构建查询
        query = (
            select(OpenAPIDB)
            .where(OpenAPIDB.user_id == user_id)
            .where(OpenAPIDB.is_active == 1)  # 只返回激活状态的记录
            .order_by(OpenAPIDB.created_at.desc())  # 按创建时间降序排序
            .offset(skip)  # 计算偏移量（从 0 开始）
            .limit(page_size)  # 限制每页数量
        )
        query_result = await self.db.execute(query)
        api_keys = query_result.scalars().all()
        result = []
        for key in api_keys:
            result.append({"id": key.id, "api_key": key.prefix + "******************", "name": key.name,
                        "createTime": key.created_at, "recentTime": key.updated_at})

        # 缓存查询结果
        if self.redis:
            # 由于对象序列化复杂，实际项目中可使用专用库或自定义序列化方法
            pass
            
        return result
    
    async def delete_api_key(self, api_key_id: str, user_id: str) -> bool:
        """软删除API Key"""
        # 检查API Key是否存在且属于当前用户
        api_key = await self.get_api_key(api_key_id, user_id)
        if not api_key:
            return False
            
        # 执行软删除 - 将 is_active 设置为 0
        stmt = update(OpenAPIDB).where(
            OpenAPIDB.id == api_key_id, 
            OpenAPIDB.user_id == user_id
        ).values(is_active=0)
        
        await self.db.execute(stmt)
        
        # 清除缓存
        await self._invalidate_api_keys_cache(user_id)
        
        return True
        
    async def validate_api_key(self, key: str) -> Optional[str]:
        """验证API Key并返回关联的用户ID"""
        query = select(OpenAPIDB).where(OpenAPIDB.key == key)
        query = query.where(OpenAPIDB.is_active == 1)  # 只验证激活状态的记录
        result = await self.db.execute(query)
        api_key = result.scalars().first()
        
        if api_key:
            return str(api_key.user_id)
        return None
