from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings
from urllib.parse import quote
import asyncio
from functools import wraps

engine = create_async_engine(
    get_settings().DATABASE_URL.replace("{username}",
                                        get_settings().DATABASE_USERNAME).replace("{password}", quote(get_settings().DATABASE_PASSWORD)),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=1800,  # 减少到30分钟，避免连接过期
    pool_size=5,        # 减少连接池大小
    max_overflow=10,    # 减少最大溢出连接数
    pool_timeout=30,    # 连接池超时时间
    pool_reset_on_return='commit',  # 返回连接时重置
    connect_args={
        "autocommit": False,
        "charset": "utf8mb4",
        "connect_timeout": 60,  # 连接超时时间
    }
)


class Base(DeclarativeBase):
    pass


AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_db_and_tables():
    """Create the database and tables."""
    from app.models import load_models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def with_db_retry(max_retries=3, delay=1):
    """数据库操作重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if "Lost connection" in str(e) and attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                        continue
                    raise
            raise last_exception
        return wrapper
    return decorator
