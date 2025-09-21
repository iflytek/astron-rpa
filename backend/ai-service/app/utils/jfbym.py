import json
import httpx

from app.config import get_settings
from app.logger import get_logger
from app.schemas.jfbym import JFBYMGeneralResponseBody

API_ENDPOINT = get_settings().JFBYM_ENDPOINT
API_TOKEN = get_settings().JFBYM_API_TOKEN

logger = get_logger(__name__)


class CaptchaVerificationError(Exception):
    """Exception raised for errors in the CAPTCHA verification process."""

    pass


async def verify_captcha(
    type: str, image: str
) -> JFBYMGeneralResponseBody:
    """Verify a CAPTCHA image using the JFBYM service.

    Args:
        type: Type ID of the CAPTCHA verification
        image: Base64-encoded string of the CAPTCHA image

    Returns:
        Dictionary containing the verification result
    """
    payload = {
        "token": API_TOKEN,
        "type": type,
        "image": image,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_ENDPOINT, json=payload, timeout=30.0)
            response.raise_for_status()
            logger.info(f"JFBYM response: {response.json()}")
            model = JFBYMGeneralResponseBody.model_validate(response.json())
            return model

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during OCR request: {e}")
            raise  # Re-raise httpx.HTTPError instead of wrapping it
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise CaptchaVerificationError("Invalid response format") from e
        except Exception as e:
            logger.error(f"Unexpected error during : {e}")
            raise CaptchaVerificationError(f"Unexpected error: {str(e)}")
