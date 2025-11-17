from sqlalchemy import Column, String, Integer, DateTime, func
from app.database import Base


class User(Base):
    """用户数据库模型"""

    __tablename__ = "openapi_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    default_api_key = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
