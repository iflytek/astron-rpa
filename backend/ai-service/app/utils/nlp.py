import base64
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime
from urllib.parse import quote, urlparse

import httpx

from app.logger import get_logger
from app.schemas.nlp import (
    TextCorrectionDecodedResult,
    TextCorrectionResponseBody,
    TextCorrectionUpstreamResponseBody,
    TextModerationResponseBody,
    TranslationResponseBody,
)
from app.utils.ocr.auth import HmacSHA256Auth

TEXT_CORRECTION_URL = "https://api.xf-yun.com/v1/private/s9a87e3ec"
TEXT_CORRECTION_SERVICE_ID = "s9a87e3ec"
TEXT_MODERATION_URL = "https://audit.iflyaisol.com/audit/v2/syncText"
TRANSLATION_NIUTRANS_URL = "https://ntrans.xfyun.cn/v2/ots"

logger = get_logger(__name__)


class TextCorrectionError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TextModerationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TranslationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _build_text_correction_payload(text: str, uid: str | None = None, res_id: str | None = None) -> dict:
    payload = {
        "header": {
            "app_id": HmacSHA256Auth().app_id,
            "status": 3,
        },
        "parameter": {
            TEXT_CORRECTION_SERVICE_ID: {
                "result": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "json",
                }
            }
        },
        "payload": {
            "input": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "json",
                "status": 3,
                "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
            }
        },
    }
    if uid:
        payload["header"]["uid"] = uid
    if res_id:
        payload["parameter"][TEXT_CORRECTION_SERVICE_ID]["res_id"] = res_id
    return payload


def _decode_result_text(encoded_text: str) -> TextCorrectionDecodedResult:
    try:
        decoded = base64.b64decode(encoded_text).decode("utf-8")
        return TextCorrectionDecodedResult.model_validate(json.loads(decoded))
    except Exception as exc:
        raise TextCorrectionError("Failed to decode text correction result.", status_code=500) from exc


def _ensure_text_correction_business_success(decoded_result: TextCorrectionDecodedResult) -> None:
    ret = decoded_result.ret
    if ret in (None, 0, "0"):
        return
    message = decoded_result.desc or decoded_result.message or f"Text correction failed with ret={ret}."
    raise TextCorrectionError(message)


def _extract_text_correction_upstream_error(response_text: str) -> tuple[str, int | None] | None:
    try:
        payload = json.loads(response_text)
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    header = payload.get("header")
    if not isinstance(header, dict):
        return None

    code = header.get("code")
    message = header.get("message")
    if message:
        return str(message), code if isinstance(code, int) else None
    return None


async def correct_text(text: str, uid: str | None = None, res_id: str | None = None) -> TextCorrectionResponseBody:
    auth_strategy = HmacSHA256Auth()
    request_url = auth_strategy.build_auth_url(TEXT_CORRECTION_URL)
    parsed_url = urlparse(TEXT_CORRECTION_URL)
    payload = _build_text_correction_payload(text, uid, res_id)
    headers = {
        **auth_strategy.build_auth_headers(),
        "host": parsed_url.netloc,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(request_url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        upstream_body = exc.response.text if exc.response is not None else ""
        logger.error(
            "Text correction upstream status error: status=%s body=%s request_meta=%s",
            exc.response.status_code if exc.response is not None else "unknown",
            upstream_body,
            {
                "text_length": len(text),
                "text_bytes": len(text.encode("utf-8")),
                "uid": uid,
                "res_id": res_id,
            },
        )
        parsed_error = _extract_text_correction_upstream_error(upstream_body)
        if parsed_error is not None:
            message, code = parsed_error
            detail = f"Text correction upstream error: {message}"
            if code is not None:
                detail = f"{detail} (code: {code})"
            raise TextCorrectionError(detail, status_code=502) from exc
        raise

    upstream_model = TextCorrectionUpstreamResponseBody.model_validate(response.json())
    if upstream_model.header.code != 0:
        raise TextCorrectionError(upstream_model.header.message or "Text correction request failed.")
    if not upstream_model.payload or not upstream_model.payload.result.text:
        raise TextCorrectionError("Text correction response payload is empty.", status_code=500)

    decoded_result = _decode_result_text(upstream_model.payload.result.text)
    logger.info("Text correction result: %s", decoded_result.model_dump())
    _ensure_text_correction_business_success(decoded_result)
    return TextCorrectionResponseBody(header=upstream_model.header, result=decoded_result)


def _build_text_moderation_payload(
    content: str, is_match_all: int = 0, categories: list[str] | None = None, lib_ids: list[str] | None = None
) -> dict:
    payload = {
        "content": content,
        "is_match_all": is_match_all,
    }
    if categories:
        payload["categories"] = categories
    if lib_ids:
        payload["lib_ids"] = lib_ids
    return payload


def _build_iflyaisol_query_params(auth: HmacSHA256Auth) -> dict[str, str]:
    utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S+0000")
    request_uuid = str(uuid.uuid4())
    params = {
        "accessKeyId": auth.api_key,
        "accessKeySecret": auth.api_secret,
        "appId": auth.app_id,
        "utc": utc,
        "uuid": request_uuid,
    }
    base_items = []
    for key in sorted(params.keys()):
        value = params[key]
        if value:
            base_items.append(f"{key}={quote(str(value), safe='')}")
    base_string = "&".join(base_items)
    signature = base64.b64encode(
        hmac.new(auth.api_secret.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha1).digest()
    ).decode("utf-8")
    params["signature"] = signature
    return params


async def moderate_text(
    content: str, is_match_all: int = 0, categories: list[str] | None = None, lib_ids: list[str] | None = None
) -> TextModerationResponseBody:
    auth = HmacSHA256Auth()
    params = _build_iflyaisol_query_params(auth)
    payload = _build_text_moderation_payload(content, is_match_all, categories, lib_ids)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(TEXT_MODERATION_URL, params=params, json=payload)
        response.raise_for_status()

    model = TextModerationResponseBody.model_validate(response.json())
    if model.code != "000000":
        raise TextModerationError(model.desc or "Text moderation request failed.")
    return model


def _build_translation_payload(text: str, from_lang: str, to: str, auth: HmacSHA256Auth) -> dict:
    return {
        "common": {
            "app_id": auth.app_id,
        },
        "business": {
            "from": from_lang,
            "to": to,
        },
        "data": {
            "text": base64.b64encode(text.encode("utf-8")).decode("utf-8"),
        },
    }


def _build_translation_headers(auth: HmacSHA256Auth, body: bytes) -> dict[str, str]:
    parsed_url = urlparse(TRANSLATION_NIUTRANS_URL)
    host = parsed_url.netloc
    request_path = parsed_url.path
    request_line = f"POST {request_path} HTTP/1.1"
    date = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")
    digest = "SHA-256=" + base64.b64encode(hashlib.sha256(body).digest()).decode("utf-8")
    signature_origin = f"host: {host}\ndate: {date}\n{request_line}\ndigest: {digest}"
    signature = base64.b64encode(
        hmac.new(auth.api_secret.encode("utf-8"), signature_origin.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")
    authorization = (
        f'api_key="{auth.api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line digest", signature="{signature}"'
    )
    return {
        "Content-Type": "application/json",
        "Accept": "application/json,version=1.0",
        "Host": host,
        "Date": date,
        "Digest": digest,
        "Authorization": authorization,
    }


async def translate_text(text: str, from_lang: str, to: str) -> TranslationResponseBody:
    auth = HmacSHA256Auth()
    payload = _build_translation_payload(text, from_lang, to, auth)
    body = json.dumps(payload).encode("utf-8")
    headers = _build_translation_headers(auth, body)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(TRANSLATION_NIUTRANS_URL, content=body, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        upstream_body = exc.response.text if exc.response is not None else ""
        logger.error(
            "Translation upstream status error: status=%s body=%s request_meta=%s",
            exc.response.status_code if exc.response is not None else "unknown",
            upstream_body,
            {
                "text_length": len(text),
                "text_bytes": len(text.encode("utf-8")),
                "from_lang": from_lang,
                "to": to,
            },
        )
        raise
    except httpx.HTTPError as exc:
        logger.error(
            "Translation upstream network error: %s request_meta=%s",
            exc,
            {
                "text_length": len(text),
                "text_bytes": len(text.encode("utf-8")),
                "from_lang": from_lang,
                "to": to,
            },
        )
        raise

    model = TranslationResponseBody.model_validate(response.json())
    if model.code != 0:
        raise TranslationError(model.message or "Translation request failed.")
    if not model.data or not model.data.result.trans_result.dst:
        raise TranslationError("Translation response payload is empty.", status_code=500)

    return model
