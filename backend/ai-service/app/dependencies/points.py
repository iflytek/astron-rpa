from fastapi import Depends, HTTPException

from app.logger import get_logger
from app.services.point import (
    UserPointService,
    PointTransactionType,
    InsufficientPointsError,
)
from app.dependencies import get_user_point_service, get_user_id_from_header
logger = get_logger(__name__)

class PointChecker:
    def __init__(self, points_cost: int, transaction_type: PointTransactionType):
        self.points_cost = points_cost
        self.transaction_type = transaction_type

    async def __call__(
        self,
        current_user_id: str = Depends(get_user_id_from_header),
        userpoints_service: UserPointService = Depends(get_user_point_service),
    ):
        logger.info("Checking points call...")
        try:
            # 先尝试增加积分，内部使用了 Redis，性能开销很小
            await userpoints_service.grant_monthly_points(current_user_id)

            # 检查用户积分
            points = await userpoints_service.get_cached_points(current_user_id)
            if points < self.points_cost:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient points.",
                )

            # 返回包含用户信息和扣除积分方法的对象
            return PointsContext(
                user_id=current_user_id,
                service=userpoints_service,
                points_cost=self.points_cost,
                transaction_type=self.transaction_type,
            )
        except Exception as e:
            logger.error(f"Failed to check points: {str(e)}")
            raise e


class PointsContext:
    def __init__(
        self,
        user_id: str,
        service: UserPointService,
        points_cost: int,
        transaction_type: PointTransactionType,
    ):
        self.user_id = user_id
        self.service = service
        self.points_cost = points_cost
        self.transaction_type = transaction_type

    async def deduct_points(self):
        """扣除积分"""
        try:
            await self.service.deduct_points(
                user_id=self.user_id,
                amount=self.points_cost,
                transaction_type=self.transaction_type,
            )
            return True
        except InsufficientPointsError:
            raise HTTPException(
                status_code=403,
                detail="Insufficient points.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to deduct points: {str(e)}",
            )
