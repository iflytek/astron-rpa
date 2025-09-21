import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from redis.asyncio import ConnectionPool, Redis

from app.main import app
from app.database import get_db, Base
from app.redis import get_redis

# 测试环境配置
TEST_MYSQL_URL = "mysql+aiomysql://test_user:test_password@localhost:3307/test_db"
TEST_REDIS_URL = "redis://localhost:6380/0"


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    yield


@pytest.fixture(scope="session")
def test_app():
    """创建测试应用实例"""
    app.router.lifespan_context = test_lifespan
    return app


@pytest_asyncio.fixture(scope="function")
async def test_redis_pool():
    """创建测试 Redis 连接池"""
    pool = ConnectionPool.from_url(TEST_REDIS_URL)
    yield pool
    await pool.disconnect()


@pytest_asyncio.fixture(scope="function")
async def test_get_redis(test_redis_pool):
    """提供干净的 Redis 客户端"""
    redis = Redis(connection_pool=test_redis_pool)

    # 每个测试前清理数据
    await redis.flushdb()

    yield redis

    # 每个测试后清理数据
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_MYSQL_URL,
        echo=False,  # 测试时关闭 SQL 日志
        pool_pre_ping=True,
        pool_recycle=300,
    )

    # 加载模型
    from app.models import load_models  # noqa: F401

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")  # 改为 function 级别确保测试隔离
async def test_get_db(test_db_engine):
    """提供干净的数据库会话"""
    TestingSessionLocal = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with TestingSessionLocal() as session:
        # 开始事务
        transaction = await session.begin()

        yield session

        # 回滚事务确保测试隔离
        await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI, test_get_db, test_get_redis):
    """提供异步测试客户端"""

    async def override_get_db():
        """覆盖 get_db 依赖以使用测试数据库"""
        yield test_get_db

    async def override_get_redis():
        """覆盖 get_redis 依赖以使用测试 Redis"""
        yield test_get_redis

    # 覆盖依赖
    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_redis] = override_get_redis

    # 使用 AsyncClient 进行异步测试
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client

    # 清理依赖覆盖
    test_app.dependency_overrides.clear()


# # 添加便捷的同步客户端（如果需要）
# @pytest.fixture(scope="function")
# def client(async_client):
#     """同步客户端适配器（如果某些测试库需要同步接口）"""
#     return async_client


# 添加测试数据初始化 fixture
# @pytest_asyncio.fixture(scope="function")
# async def sample_data(test_db):
#     """预填充测试数据"""
#     # 在这里添加测试所需的样本数据
#     # 例如：创建测试用户、文章等
#     pass

async def create_api_key(user_id: str, test_get_db, test_get_redis = None):
    """为测试创建临时的 API Key"""
    from app.services.api_key import ApiKeyService
    from app.schemas.api_key import ApiKeyCreate
    import random
    
    # 创建服务实例
    service = ApiKeyService(test_get_db, test_get_redis)
    
    # 创建 API Key
    api_key_data = ApiKeyCreate(name=f"Test API Key {random.randint(1000, 9999)}")
    api_key = await service.create_api_key(api_key_data, user_id)
    
    return {"id": api_key.id, "key": api_key.key}

async def destroy_api_key(user_id: str, key_data: dict, test_get_db, test_get_redis = None):
    """删除测试用的 API Key"""
    from app.services.api_key import ApiKeyService
    
    # 创建服务实例
    service = ApiKeyService(test_get_db, test_get_redis)
    
    # 删除 API Key
    await service.delete_api_key(key_data["id"], user_id)

@pytest_asyncio.fixture(scope="function")
async def api_key_factory(test_get_db, test_get_redis):
    """
    API Key 工厂函数，支持动态 user_id
    """
    created_keys = []
    
    async def _create_api_key(user_id: str = "1234"):
        key_data = await create_api_key(user_id, test_get_db, test_get_redis)
        created_keys.append((user_id, key_data))
        return key_data
    
    yield _create_api_key
    
    # 清理所有创建的 API Key
    for user_id, key_data in created_keys:
        await destroy_api_key(user_id, key_data, test_get_db, test_get_redis)

@pytest_asyncio.fixture(scope="function")
async def api_key(test_get_db, test_get_redis):
    """
    为每个测试用例提供一个临时的 API Key
    返回包含 id 和 key 的字典
    """
    # 默认使用固定的测试用户ID，与 USER_ID_HEADER 保持一致
    user_id = "1234"
    key_data = await create_api_key(user_id, test_get_db, test_get_redis)
    yield key_data
    await destroy_api_key(user_id, key_data, test_get_db, test_get_redis)
