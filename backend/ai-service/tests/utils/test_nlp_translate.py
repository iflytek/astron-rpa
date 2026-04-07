import base64
import hashlib
import json

from app.utils.nlp import _build_translation_headers, _build_translation_payload


class _FakeAuth:
    app_id = "app-id"
    api_key = "api-key"
    api_secret = "api-secret"


def test_build_translation_payload_matches_niutrans_contract():
    payload = _build_translation_payload("你好世界", "cn", "en", _FakeAuth())

    assert payload["common"]["app_id"] == "app-id"
    assert payload["business"] == {"from": "cn", "to": "en"}
    assert base64.b64decode(payload["data"]["text"]).decode("utf-8") == "你好世界"


def test_build_translation_headers_include_digest_and_authorization():
    body = json.dumps(_build_translation_payload("hello", "en", "cn", _FakeAuth())).encode("utf-8")

    headers = _build_translation_headers(_FakeAuth(), body)

    expected_digest = "SHA-256=" + base64.b64encode(hashlib.sha256(body).digest()).decode("utf-8")
    assert headers["Host"] == "ntrans.xfyun.cn"
    assert headers["Accept"] == "application/json,version=1.0"
    assert headers["Digest"] == expected_digest
    assert 'api_key="api-key"' in headers["Authorization"]
    assert 'headers="host date request-line digest"' in headers["Authorization"]
