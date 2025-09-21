from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings
from urllib.parse import quote

engine = create_async_engine(
    get_settings().DATABASE_URL.replace("{username}",
                                        get_settings().DATABASE_USERNAME).replace("{password}", quote(get_settings().DATABASE_PASSWORD)),
    echo=False,
    future=True,
    # 关键配置：解决连接超时问题
    pool_pre_ping=True,        # 使用前检查连接是否有效，防止使用已断开的连接
    pool_recycle=3600,         # 1小时后回收连接，防止长时间空闲导致服务器断开
    pool_size=5,               # 连接池大小
    max_overflow=10,           # 最大溢出连接数
    pool_timeout=30,           # 获取连接的超时时间
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
