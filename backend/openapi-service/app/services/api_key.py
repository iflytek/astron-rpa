from datetime import datetime
from typing import Optional

import pytz
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import get_logger
from app.models.api_key import AstronAgentDB, OpenAPIDB
from app.schemas.api_key import ApiKeyCreate
from app.utils.api_key import APIKeyUtils

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
        logger.info("Generated API key: %s", api_key)
        hashed_key = APIKeyUtils.hash_api_key(api_key)
        prefix = api_key[:8]
        name = api_key_data.name

        new_api_key = OpenAPIDB(
            user_id=user_id,
            api_key=hashed_key,  # 数据库中不存真实API_KEY
            prefix=prefix,
            created_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
            name=name,
            is_active=1,
            updated_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
        )

        self.db.add(new_api_key)
        await self.db.flush()
        await self.db.refresh(new_api_key)

        # 清除缓存
        await self._invalidate_api_keys_cache(user_id)

        return api_key

    async def get_api_key(self, api_key_id: str, user_id: str | None = None) -> Optional[OpenAPIDB]:
        """获取指定API Key"""
        query = select(OpenAPIDB).where(OpenAPIDB.id == api_key_id)
        if user_id is not None:
            query = query.where(OpenAPIDB.user_id == user_id)
        query = query.where(OpenAPIDB.is_active == 1)  # 只返回激活状态的记录

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_api_keys(self, user_id: str, page_no: int = 0, page_size: int = 10) -> list[OpenAPIDB]:
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
            .where(~OpenAPIDB.name.startswith("default_key_"))  # 排除以 default_key_ 开头的记录
            .order_by(OpenAPIDB.created_at.desc())  # 按创建时间降序排序
            .offset(skip)  # 计算偏移量（从 0 开始）
            .limit(page_size)  # 限制每页数量
        )
        query_result = await self.db.execute(query)
        api_keys = query_result.scalars().all()
        result = []
        for key in api_keys:
            result.append(
                {
                    "id": key.id,
                    "api_key": key.prefix + "******************",
                    "name": key.name,
                    "createTime": key.created_at,
                    "recentTime": key.updated_at,
                }
            )

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
        stmt = update(OpenAPIDB).where(OpenAPIDB.id == api_key_id, OpenAPIDB.user_id == user_id).values(is_active=0)

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


class AstronApiKeyService:
    def __init__(self, db: AsyncSession, redis: Redis = None):
        self.db = db
        self.redis = redis

    async def create_astron_agent(self, astron_agent_data, user_id: str):
        """创建星辰Agent"""

        # 创建新的星辰Agent记录
        new_astron_agent = AstronAgentDB(
            user_id=user_id,
            name=astron_agent_data.name,
            app_id=astron_agent_data.app_id,
            api_key=astron_agent_data.api_key,
            api_secret=astron_agent_data.api_secret,
            created_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
            updated_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None),
            is_active=1,
        )

        self.db.add(new_astron_agent)
        await self.db.flush()
        await self.db.refresh(new_astron_agent)

        logger.info("Created AstronAgent for user %s: %s", user_id, new_astron_agent.id)

        return new_astron_agent

    async def delete_astron_agent(self, astron_agent_id: str, user_id: str) -> bool:
        """软删除星辰Agent（设置is_active为0）"""
        try:
            # 更新指定用户和ID的星辰Agent，将is_active设置为0
            stmt = (
                update(AstronAgentDB)
                .where(AstronAgentDB.id == astron_agent_id, AstronAgentDB.user_id == user_id)
                .values(is_active=0, updated_at=datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None))
            )

            result = await self.db.execute(stmt)
            await self.db.commit()

            # 检查是否实际更新了记录
            if result.rowcount > 0:
                logger.info("Soft deleted AstronAgent %s for user %s", astron_agent_id, user_id)
                return True
            else:
                logger.warning("AstronAgent %s for user %s not found", astron_agent_id, user_id)
                return False

        except Exception as e:
            logger.error("Error soft deleting AstronAgent %s for user %s: %s", astron_agent_id, user_id, str(e))
            await self.db.rollback()
            raise

    async def get_astron_agents(self, user_id: str, pageNo: int = 1, pageSize: int = 10) -> list[dict]:
        """获取星辰Agent列表"""
        try:
            skip = (pageNo - 1) * pageSize

            # 构建查询，只获取活跃的记录
            query = (
                select(AstronAgentDB)
                .where(AstronAgentDB.user_id == user_id)
                .where(AstronAgentDB.is_active == 1)
                .order_by(AstronAgentDB.created_at.desc())
                .offset(skip)
                .limit(pageSize)
            )

            result = await self.db.execute(query)
            astron_agents = result.scalars().all()

            # 格式化返回数据
            formatted_agents = []
            for agent in astron_agents:
                formatted_agents.append(
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "app_id": agent.app_id,
                        "api_key": agent.api_key,
                        "api_secret": agent.api_secret,
                        "createTime": agent.created_at,
                        "recentTime": agent.updated_at,
                    }
                )

            return formatted_agents

        except Exception as e:
            logger.error("Error getting AstronAgents for user %s: %s", user_id, str(e))
            raise

    async def get_all_astron_agents(self, user_id: str) -> list[dict]:
        """获取用户的所有星辰Agent（不分页）"""
        try:
            # 构建查询，只获取活跃的记录
            query = (
                select(AstronAgentDB)
                .where(AstronAgentDB.user_id == user_id)
                .where(AstronAgentDB.is_active == 1)
                .order_by(AstronAgentDB.created_at.desc())
            )

            result = await self.db.execute(query)
            astron_agents = result.scalars().all()

            # 格式化返回数据
            formatted_agents = []
            for agent in astron_agents:
                formatted_agents.append(
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "app_id": agent.app_id,
                        "api_key": agent.api_key,
                        "api_secret": agent.api_secret,
                        "createTime": agent.created_at,
                        "recentTime": agent.updated_at,
                    }
                )

            return formatted_agents

        except Exception as e:
            logger.error("Error getting all AstronAgents for user %s: %s", user_id, str(e))
            raise

    async def update_astron_agent(self, astron_agent_id: str, user_id: str, update_data) -> bool:
        """更新星辰Agent"""
        try:
            # 更新指定用户和ID的星辰Agent
            update_values = {"updated_at": datetime.now(pytz.timezone("Asia/Shanghai")).replace(tzinfo=None)}

            # 只更新提供的字段
            if hasattr(update_data, "name") and update_data.name is not None:
                update_values["name"] = update_data.name
            if hasattr(update_data, "app_id") and update_data.app_id is not None:
                update_values["app_id"] = update_data.app_id
            if hasattr(update_data, "api_key") and update_data.api_key is not None:
                update_values["api_key"] = update_data.api_key
            if hasattr(update_data, "api_secret") and update_data.api_secret is not None:
                update_values["api_secret"] = update_data.api_secret

            stmt = (
                update(AstronAgentDB)
                .where(
                    AstronAgentDB.id == astron_agent_id,
                    AstronAgentDB.user_id == user_id,
                    AstronAgentDB.is_active == 1,  # 只更新活跃的记录
                )
                .values(update_values)
            )

            result = await self.db.execute(stmt)
            await self.db.commit()

            # 检查是否实际更新了记录
            if result.rowcount > 0:
                logger.info("Updated AstronAgent %s for user %s", astron_agent_id, user_id)
                return True
            else:
                logger.warning("AstronAgent %s for user %s not found or not active", astron_agent_id, user_id)
                return False

        except Exception as e:
            logger.error("Error updating AstronAgent %s for user %s: %s", astron_agent_id, user_id, str(e))
            await self.db.rollback()
            raise

    async def get_astron_agent_by_id(self, astron_agent_id: int, user_id: str) -> Optional[dict]:
        """根据ID获取单个星辰Agent"""
        try:
            # 构建查询，只获取活跃的记录
            query = (
                select(AstronAgentDB)
                .where(AstronAgentDB.id == astron_agent_id)
                .where(AstronAgentDB.user_id == user_id)
                .where(AstronAgentDB.is_active == 1)
            )

            result = await self.db.execute(query)
            agent = result.scalars().first()

            if agent:
                # 格式化返回数据
                return {
                    "id": agent.id,
                    "name": agent.name,
                    "app_id": agent.app_id,
                    "api_key": agent.api_key,
                    "api_secret": agent.api_secret,
                    "createTime": agent.created_at,
                    "recentTime": agent.updated_at,
                }

            return None

        except Exception as e:
            logger.error("Error getting AstronAgent %s for user %s: %s", astron_agent_id, user_id, str(e))
            raise
