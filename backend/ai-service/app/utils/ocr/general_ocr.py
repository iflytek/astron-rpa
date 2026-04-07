"""
Universal OCR (Optical Character Recognition) service using Xunfei API.

This module provides functionality to perform OCR on images using Xunfei's
universal character recognition API.
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime
from time import mktime
from typing import Any
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import httpx

from app.config import get_settings
from app.logger import get_logger
from app.schemas.ocr import OCRGeneralDecodedResponseBody, OCRGeneralResponseBody
from app.utils.ocr.base import OCRError
from app.utils.ocr.error_policy import classify_ocr_failure

logger = get_logger(__name__)

APP_ID = get_settings().XFYUN_APP_ID
API_SECRET = get_settings().XFYUN_API_SECRET
API_KEY = get_settings().XFYUN_API_KEY

BASE_URL = "https://api.xf-yun.com/v1/private/sf8e6aca1"
SERVICE_ID = "sf8e6aca1"


class Url:
    def __init__(self, host: str, path: str, schema: str):
        self.host = host
        self.path = path
        self.schema = schema


def parse_url(request_url: str) -> Url:
    stidx = request_url.index("://")
    host = request_url[stidx + 3 :]
    schema = request_url[: stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise OCRError(f"invalid request url:{request_url}")
    path = host[edidx:]
    host = host[:edidx]
    return Url(host, path, schema)


def assemble_ws_auth_url(
    request_url: str,
    method: str = "POST",
    api_key: str = API_KEY,
    api_secret: str = API_SECRET,
) -> str:
    url = parse_url(request_url)
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    signature_origin = f"host: {url.host}\ndate: {date}\n{method} {url.path} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
    values = {"host": url.host, "date": date, "authorization": authorization}
    return request_url + "?" + urlencode(values)


def _build_request_payload(image_base64: str, encoding: str = "jpg", status: int = 3) -> dict[str, Any]:
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


def _decode_general_result_text(text_base64: str) -> dict[str, Any]:
    try:
        decoded = base64.b64decode(text_base64).decode("utf-8")
        parsed = json.loads(decoded)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OCRError("Failed to decode OCR general result payload.") from exc

    if not isinstance(parsed, dict):
        raise OCRError("Decoded OCR general result payload must be a JSON object.")
    return parsed


async def recognize_text_from_image(
    image_base64: str,
    image_encoding: str = "jpg",
    status: int = 3,
    timeout: float = 30.0,
) -> OCRGeneralDecodedResponseBody:
    try:
        request_payload = _build_request_payload(image_base64, image_encoding, status)
        authenticated_url = assemble_ws_auth_url(BASE_URL)

        headers = {
            "content-type": "application/json",
            "host": "api.xf-yun.com",
            "app_id": APP_ID,
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(authenticated_url, data=json.dumps(request_payload), headers=headers)

        response.raise_for_status()
        result = response.json()
        model = OCRGeneralResponseBody.model_validate(result)

        if model.header.code != 0:
            error_message = getattr(model.header, "msg", None) or model.header.message or "Unknown API error"
            decision = classify_ocr_failure(model.header.code, error_message)
            raise OCRError(
                error_message,
                code=model.header.code,
                should_deduct_points=decision.should_deduct_points,
                status_code=decision.http_status,
                category=decision.category.value,
            )

        if not model.payload or not model.payload.result.text:
            raise OCRError("OCR general response payload is empty.")

        decoded_result = _decode_general_result_text(model.payload.result.text)
        logger.info("OCR processing completed successfully")
        return OCRGeneralDecodedResponseBody(header=model.header, data=decoded_result)

    except httpx.HTTPError:
        raise
    except json.JSONDecodeError as exc:
        raise OCRError("Invalid response format") from exc
    except OCRError:
        raise
    except Exception as exc:
        raise OCRError(f"OCR processing failed: {str(exc)}") from exc
