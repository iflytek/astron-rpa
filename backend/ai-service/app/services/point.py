from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from redis.asyncio import Redis
from app.logger import get_logger
from app.models.point import (
    PointAllocation,
    PointConsumption,
    PointTransaction,
    PointTransactionType,
    PointExpirationPolicy,
    calculate_expiration_date,
)
from app.config import get_settings

logger = get_logger(__name__)

class UserPointService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis

    async def get_cached_points(self, user_id: str) -> int:
        try:
            cached_points = await self.redis.get(f"user_points:{user_id}")
            if cached_points is not None:
                return int(cached_points)
        except Exception as e:
            # Log the error if needed
            logger.error(f"Error fetching cached points for user {user_id}: {e}")

        # Fallback to database if cache miss
        user_point = await self._calculate_user_points(user_id)
        await self._set_cached_points(user_id, user_point)

        return user_point

    async def _set_cached_points(self, user_id: str, points: int):
        try:
            await self.redis.set(f"user_points:{user_id}", points, ex=3600)
        except Exception as e:
            # Log the error if needed
            logger.error(f"Error setting cached points for user {user_id}: {e}")
            pass

    async def _clear_cached_points(self, user_id: str):
        try:
            await self.redis.delete(f"user_points:{user_id}")
        except Exception as e:
            # Log the error if needed
            logger.error(f"Error clearing cached points for user {user_id}: {e}")
            pass

    async def _get_available_allocations(self, user_id: str):
        current_time = datetime.now(timezone.utc)
        query = (
            select(PointAllocation)
            .where(
                PointAllocation.user_id == user_id,
                PointAllocation.remaining_amount > 0,
                PointAllocation.expires_at > current_time,
            )
            .order_by(PointAllocation.priority.desc(), PointAllocation.expires_at.asc())
        )
        result = await self.db.execute(query)
        allocations = result.scalars().all()
        return allocations

    async def _calculate_user_points(self, user_id: str):
        allocations = await self._get_available_allocations(user_id)
        total_points = sum(allocation.remaining_amount for allocation in allocations)
        return total_points

    def _get_priority_for_type(self, allocation_type: PointTransactionType) -> int:
        """根据积分类型设置优先级"""
        if allocation_type == PointTransactionType.MONTHLY_GRANT:
            return 50
        elif allocation_type == PointTransactionType.MANUAL_ADD:
            return 10
        else:
            return 20

    async def create_point_allocation(
        self,
        user_id: str,
        amount: int,
        allocation_type: PointTransactionType,
        description: str = None,
        expiration_policy: PointExpirationPolicy = None,
        fixed_expiry_date: datetime = None,
    ):
        """Create a new point allocation with expiration based on policy"""

        # Calculate expiration date
        if fixed_expiry_date and expiration_policy == PointExpirationPolicy.FIXED_DATE:
            expires_at = fixed_expiry_date
        else:
            expires_at = calculate_expiration_date(allocation_type, expiration_policy)

        # Create the allocation
        allocation = PointAllocation(
            user_id=user_id,
            initial_amount=amount,
            remaining_amount=amount,
            allocation_type=allocation_type.value,
            expires_at=expires_at,
            description=description,
            # Set priority based on type or other rules
            priority=self._get_priority_for_type(allocation_type),
        )
        self.db.add(allocation)
        await self.db.flush()

        # Create the transaction
        transaction = PointTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=allocation_type.value,
            related_entity_type="PointAllocation",
            related_entity_id=allocation.id,
            description=description,
        )
        self.db.add(transaction)

        # Clear the user's cached balance
        await self._clear_cached_points(user_id)

        await self.db.flush()
        return allocation

    async def grant_monthly_points(self, user_id: str):
        # Check if user already received monthly points this month
        current_time = datetime.now(timezone.utc)
        redis_key = f"points_monthly_grant:{user_id}:{current_time.year}-{current_time.month}"

        try:
            already_granted = await self.redis.get(redis_key)
            if already_granted:
                return None
        except Exception as e:
            # Log the error if needed
            logger.error(f"Error checking Redis for monthly grant: {e}")

        month_start = current_time.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(
            seconds=1
        )

        # Query for existing monthly grant in current month
        existing_grant = await self.db.execute(
            select(PointAllocation).where(
                PointAllocation.user_id == user_id,
                PointAllocation.allocation_type == PointTransactionType.MONTHLY_GRANT.value,
                PointAllocation.created_at.between(month_start, month_end),
            )
        )
        existing_grant = existing_grant.scalar_one_or_none()
        if existing_grant:
            try:
                await self.redis.set(redis_key, "1", ex=3600 * 24 * 32)  # 32 days
            except Exception as e:
                # Log the error if needed
                logger.error(f"Error setting Redis key for monthly grant: {e}")
            return existing_grant

        # Create a new monthly grant allocation
        allocation = await self.create_point_allocation(
            user_id=user_id,
            amount=get_settings().MONTHLY_GRANT_AMOUNT,
            allocation_type=PointTransactionType.MONTHLY_GRANT,
        )

        # Update Redis to mark as granted for this month
        try:
            await self.redis.set(redis_key, "1", ex=3600 * 24 * 32)  # 32 days
        except Exception as e:
            # Log the error if needed
            logger.error(f"Error setting Redis key for monthly grant: {e}")

        return allocation

    async def manual_add_points(self, user_id: str, amount: int):
        return await self.create_point_allocation(
            user_id=user_id,
            amount=amount,
            allocation_type=PointTransactionType.MANUAL_ADD,
        )

    async def deduct_points(
        self,
        user_id: str,
        amount: int,
        transaction_type: PointTransactionType,
        description: str = None,
        related_entity_type: str = None,
        related_entity_id: int = None,
    ) -> PointTransaction:
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # 1. Get unexpired point allocations ordered by priority (high to low)
        allocations = await self._get_available_allocations(user_id)

        # Calculate total available points
        available_points = sum(
            allocation.remaining_amount for allocation in allocations
        )

        if available_points < amount:
            raise InsufficientPointsError(
                f"User {user_id} has only {available_points} points, but {amount} are required."
            )

        # 2. Create transaction first (we'll link consumptions to it)
        transaction = PointTransaction(
            user_id=user_id,
            amount=-amount,
            transaction_type=transaction_type.value,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            description=description,
        )
        self.db.add(transaction)
        await self.db.flush()

        # 3. Consume points from allocations in priority order
        remaining_to_deduct = amount
        consumptions = []

        for allocation in allocations:
            if remaining_to_deduct <= 0:
                break

            # Determine how much to take from this allocation
            consumption_amount = min(allocation.remaining_amount, remaining_to_deduct)

            # Create consumption record
            consumption = PointConsumption(
                transaction_id=transaction.id,
                allocation_id=allocation.id,
                amount=consumption_amount,
            )
            self.db.add(consumption)
            consumptions.append(consumption)

            # Update the allocation's remaining amount
            allocation.remaining_amount -= consumption_amount

            # Reduce the amount left to deduct
            remaining_to_deduct -= consumption_amount
        await self.db.flush()

        # 4. Update UserPoint cache
        # NOTE: 绝大部分场景都是扣除积分，所以这里直接更新缓存。如果直接清理，则会导致每次重新计算，性能不升反降。
        user_point = await self.get_cached_points(user_id)
        user_point -= amount
        await self._set_cached_points(user_id, user_point)

        await self.db.flush()

        return transaction


class InsufficientPointsError(Exception):
    """自定义异常类，表示积分不足的错误"""

    pass
