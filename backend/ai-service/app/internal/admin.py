from fastapi import APIRouter, Depends
from app.dependencies import get_user_point_service
from app.services.point import UserPointService, PointTransactionType

router = APIRouter()


@router.post("")
async def update_admin():
    return {"message": "Admin getting schwifty"}


@router.get("/user/points")
async def get_user_points(
    user_id: str,
    user_point_service: UserPointService = Depends(get_user_point_service),
):
    user_point = await user_point_service.get_cached_points(user_id)
    return {"user_point": user_point}


@router.post("/user/points")
async def add_user_points(
    user_id: str,
    amount: int,
    user_point_service: UserPointService = Depends(get_user_point_service),
):
    """
    Add points to a user.
    """
    user_point = await user_point_service.manual_add_points(
        user_id=user_id,
        amount=amount,
    )
    return {
        "message": f"Added {amount} points to user {user_id}",
        "user_point": user_point,
    }


@router.post("/user/points/deduct")
async def deduct_user_points(
    user_id: str,
    amount: int,
    user_point_service: UserPointService = Depends(get_user_point_service),
):
    """
    Deduct points from a user.
    """
    user_point = await user_point_service.deduct_points(
        user_id=user_id,
        amount=amount,
        transaction_type=PointTransactionType.MANUAL_DEDUCT,
    )
    return {
        "message": f"Deducted {amount} points from user {user_id}",
        "user_point": user_point,
    }
