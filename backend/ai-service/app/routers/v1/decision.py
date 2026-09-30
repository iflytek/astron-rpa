import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import Settings, get_settings
from app.dependencies.points import PointChecker, PointsContext
from app.schemas.decision import ChoiceRequest, ChoiceResponse
from app.services.decision import choose
from app.services.point import PointTransactionType

router = APIRouter(prefix="/decision", tags=["Semantic choice"])
choice_points_checker = PointChecker(
    get_settings().JEV_POINTS_COST, PointTransactionType.AICHAT_COST
)


def get_choice_client(
    request: Request, settings: Settings = Depends(get_settings)
) -> httpx.AsyncClient:
    if not settings.JEV_API_KEY.get_secret_value().strip():
        raise HTTPException(status_code=503, detail="Semantic choice is not configured")
    return request.app.state.jev_http_client


@router.post("/choice", response_model=ChoiceResponse)
async def semantic_choice(
    params: ChoiceRequest,
    client: httpx.AsyncClient = Depends(get_choice_client),
    points: PointsContext = Depends(choice_points_checker),
    settings: Settings = Depends(get_settings),
):
    result = await choose(params, client, settings)
    # A valid abstention is also a completed inference; failures are not charged.
    await points.deduct_points()
    return result
