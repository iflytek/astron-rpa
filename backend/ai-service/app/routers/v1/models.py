from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.dependencies import get_user_id_from_header
from app.logger import get_logger
from app.config import get_settings
from urllib.parse import urljoin

API_KEY = get_settings().AICHAT_API_KEY
API_ENDPOINT = urljoin(get_settings().AICHAT_BASE_URL, "models")

logger = get_logger(__name__)

router = APIRouter(
    prefix="/models",
    tags=["统一大模型接口"],
    # dependencies=[
    #     Depends(get_user_id_from_header),
    # ],
)


@router.get("")
@router.get("/")
async def list_models(
    current_user_id: str = Depends(get_user_id_from_header)
):
    """
    List available models.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_ENDPOINT, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{model_id}")
async def get_model(
    model_id: str,
    current_user_id: str = Depends(get_user_id_from_header)
):
    """
    Get details of a specific model.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_ENDPOINT}/{model_id}", headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
