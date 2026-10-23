"""Bounded AI HTTP responses; provider text and credentials are never errors."""

import json

import requests

MAX_RESPONSE_BYTES = 1024 * 1024


class AIRequestError(RuntimeError):
    """Expected HTTP/response failure without provider text or credentials."""

    def __init__(self):
        super().__init__("AI_REQUEST_FAILED")


def request_json(method, url, **kwargs):
    try:
        with requests.request(method, url, timeout=(5, 35), allow_redirects=False, stream=True, **kwargs) as response:
            if not 200 <= response.status_code < 300:
                raise ValueError("AI_REQUEST_FAILED")
            content = bytearray()
            for chunk in response.iter_content(16384):
                if len(content) + len(chunk) > MAX_RESPONSE_BYTES:
                    raise ValueError("AI_RESPONSE_TOO_LARGE")
                content.extend(chunk)
            return json.loads(content)
    except (requests.RequestException, ValueError, TypeError):
        raise AIRequestError() from None
