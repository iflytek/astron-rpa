import enum
from datetime import datetime, timedelta

import pytz
from sqlalchemy import TIMESTAMP, BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base

# 配置默认时区
DEFAULT_TIMEZONE = pytz.UTC
BUSINESS_TIMEZONE = pytz.timezone("Asia/Shanghai")


class PointTransactionType(enum.Enum):
    MONTHLY_GRANT = "monthly_grant"
    MONTHLY_RESET = "monthly_reset"
    AICHAT_COST = "aichat_cost"
    XFYUN_COST = "xfyun_cost"
    JFBYM_COST = "jfbym_cost"
    MANUAL_ADD = "manual_add"
    MANUAL_DEDUCT = "manual_deduct"
    OTHER = "other"

    def __str__(self):
        return self.value


class PointExpirationPolicy(enum.Enum):
    THIRTY_DAYS = "30_days"
    END_OF_THIS_MONTH = "end_of_this_month"
    FIXED_DATE = "fixed_date"
    NEVER = "never"

    def __str__(self):
        return self.value


POINT_TYPE_EXPIRATION_POLICIES = {
    PointTransactionType.MONTHLY_GRANT: PointExpirationPolicy.END_OF_THIS_MONTH,
    PointTransactionType.MANUAL_ADD: PointExpirationPolicy.NEVER,
    "default": PointExpirationPolicy.THIRTY_DAYS,
}


class PointAllocation(Base):
    __tablename__ = "point_allocations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    initial_amount = Column(Integer, nullable=False)  # Original allocated amount
    remaining_amount = Column(Integer, nullable=False)  # Current remaining amount
    allocation_type = Column(String(100), nullable=False)  # Source of points
    priority = Column(Integer, default=0, nullable=False)  # Higher number = higher priority
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)  # When these points expire
    description = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_user_expiry", user_id, expires_at),  # Composite index for faster queries
    )


class PointConsumption(Base):
    __tablename__ = "point_consumptions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id = Column(BigInteger, ForeignKey("point_transactions.id"), nullable=False)
    allocation_id = Column(BigInteger, ForeignKey("point_allocations.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # How many points were used from this allocation
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # Total transaction amount (positive or negative)
    transaction_type = Column(String(50), nullable=False)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(BigInteger, nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Define relationship to consumptions
    consumptions = relationship("PointConsumption", backref="transaction")


def calculate_expiration_date(allocation_type, policy=None, reference_date=None, target_timezone=None):
    """
    计算过期日期

    Args:
        allocation_type: 分配类型
        policy: 过期策略
        reference_date: 参考日期
        target_timezone: 目标时区，默认使用DEFAULT_TIMEZONE
    """
    if target_timezone is None:
        target_timezone = DEFAULT_TIMEZONE

    # 获取参考日期
    if reference_date is None:
        reference_date = datetime.now(target_timezone)
    else:
        # 确保reference_date有时区信息
        if reference_date.tzinfo is None:
            # 假设naive datetime是业务时区的时间
            reference_date = reference_date.replace(tzinfo=BUSINESS_TIMEZONE)
        # 转换到目标时区
        reference_date = reference_date.astimezone(target_timezone)

    if policy is None:
        policy = POINT_TYPE_EXPIRATION_POLICIES.get(allocation_type, POINT_TYPE_EXPIRATION_POLICIES["default"])
    if policy == PointExpirationPolicy.NEVER:
        return datetime(2099, 12, 31, 23, 59, 59, tzinfo=target_timezone)

    elif policy == PointExpirationPolicy.THIRTY_DAYS:
        return reference_date + timedelta(days=30)

    elif policy == PointExpirationPolicy.END_OF_THIS_MONTH:
        # 在业务时区计算月末
        business_date = reference_date.astimezone(BUSINESS_TIMEZONE)

        if business_date.month == 12:
            next_month = business_date.replace(
                year=business_date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        else:
            next_month = business_date.replace(
                month=business_date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
            )

        # 月末23:59:59
        end_of_month = next_month - timedelta(seconds=1)
        # 转换回目标时区
        return end_of_month.astimezone(target_timezone)

    return reference_date
