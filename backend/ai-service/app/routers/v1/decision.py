import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import Settings, get_settings
from app.dependencies.points import PointChecker, PointsContext
from app.schemas.decision import ChoiceCapabilities, ChoiceRequest, ChoiceResponse
from app.services.decision import capabilities, choose
from app.services.point import PointTransactionType

router = APIRouter(prefix="/decision", tags=["Semantic choice"])
choice_points_checker = PointChecker(
    get_settings().SEMANTIC_CHOICE_POINTS_COST,
    PointTransactionType.SEMANTIC_CHOICE_COST,
)


def get_choice_client(
    request: Request, settings: Settings = Depends(get_settings)
) -> httpx.AsyncClient:
    readiness = capabilities(settings)
    if not readiness.enabled:
        raise HTTPException(status_code=503, detail=readiness.reason)
    return request.app.state.decision_http_client


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


@router.get("/capabilities", response_model=ChoiceCapabilities)
def semantic_choice_capabilities(
    settings: Settings = Depends(get_settings),
):
    return capabilities(settings)
