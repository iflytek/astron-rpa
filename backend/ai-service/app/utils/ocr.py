"""
Universal OCR (Optical Character Recognition) service using Xunfei API.

This module provides functionality to perform OCR on images using Xunfei's
universal character recognition API.

Requirements:
- Image data must be base64 encoded and not exceed 10MB
- Supports Chinese and English text
- Supports both handwritten and printed text
- Improved performance on tilted text and some rare characters

API Documentation: https://www.xfyun.cn/doc/words/universal_character_recognition/API.html
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime
from time import mktime
from typing import Any
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import httpx

from app.config import get_settings
from app.logger import get_logger
from app.schemas.ocr import OCRGeneralResponseBody

logger = get_logger(__name__)

# Configuration
APP_ID = get_settings().XFYUN_APP_ID
API_SECRET = get_settings().XFYUN_API_SECRET
API_KEY = get_settings().XFYUN_API_KEY

# API Constants - single source of truth
BASE_URL = "https://api.xf-yun.com/v1/private/sf8e6aca1"
SERVICE_ID = "sf8e6aca1"


class OCRError(Exception):
    """Custom exception for OCR-related errors."""
    def __init__(self, msg):
        self.message = msg


class URLComponents:
    """URL components for Xunfei API authentication."""

    def __init__(self, host: str, path: str, scheme: str):
        self.host = host
        self.path = path
        self.scheme = scheme

class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema
        pass

# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest

def parse_url(request_url):
    stidx = request_url.index("://")
    host = request_url[stidx + 3:]
    schema = request_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise OCRError("invalid request url:" + request_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u

# build websocket auth request url
def assemble_ws_auth_url(request_url, method="POST", api_key=API_KEY, api_secret=API_SECRET):
    u = parse_url(request_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    logger.info("date信息: %s", date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    logger.info("signature_origin信息: %s", signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    logger.info("authorization_origin信息: %s", authorization_origin)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return request_url + "?" + urlencode(values)


def _build_request_payload(
    image_base64: str, encoding: str = "jpg", status: int = 3
) -> dict[str, Any]:
    """Build the request payload for OCR API."""
    return {
        "header": {"app_id": APP_ID, "status": status},
        "parameter": {
            SERVICE_ID: {
                "category": "ch_en_public_cloud",
                "result": {"encoding": "utf8", "compress": "raw", "format": "json"},
            }
        },
        "payload": {
            f"{SERVICE_ID}_data_1": {
                "encoding": encoding,
                "image": image_base64,
                "status": status,
            }
        },
    }


async def recognize_text_from_image(
    image_base64: str,
    image_encoding: str = "jpg",
    status: int = 3,
    timeout: float = 30.0,
) -> OCRGeneralResponseBody:
    """
    Perform OCR on base64 encoded image using Xunfei API.

    Args:
        image_base64: Base64 encoded image string
        image_encoding: Image format (jpg, png, etc.)
        status: Processing status (3 for complete processing)
        timeout: Request timeout in seconds

    Returns:
        Dict containing the OCR results from the API

    Raises:
        OCRError: If the request fails or returns an error
    """
    try:
        # Build request components
        request_payload = _build_request_payload(image_base64, image_encoding, status)

        authenticated_url = assemble_ws_auth_url(BASE_URL)
        logger.debug(f"OCR request URL: {authenticated_url}")

        headers = {
            "content-type": "application/json",
            "host": 'api.xf-yun.com',
            "app_id": APP_ID,
        }

        # Make async request
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                authenticated_url, data=json.dumps(request_payload), headers=headers
            )

        response.raise_for_status()
        result = response.json()
        model = OCRGeneralResponseBody.model_validate(result)

        # Check for API-level errors
        if model.header.code != 0:
            error_message = model.header.msg or "Unknown API error"
            raise OCRError(f"API returned error: {error_message}")

        logger.info("OCR processing completed successfully")
        return model

    except httpx.HTTPError as e:
        logger.error(f"HTTP error during OCR request: {e}")
        raise  # Re-raise httpx.HTTPError instead of wrapping it
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        raise OCRError("Invalid response format") from e
    except Exception as e:
        logger.error(f"Unexpected error during OCR: {e}")
        raise OCRError(f"OCR processing failed: {str(e)}") from e
