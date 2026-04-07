import json

import requests
from astronverse.actionlib.atomic import atomicMg

from astronverse.openapi.error import AI_REQ_ERROR_FORMAT, AI_SERVER_ERROR, BizException, format_error


class GatewayClient:
    @staticmethod
    def _gateway_port() -> str:
        port = atomicMg.cfg().get("GATEWAY_PORT")
        return str(port) if port else "13159"

    @staticmethod
    def _gateway_base_url() -> str:
        return f"http://127.0.0.1:{GatewayClient._gateway_port()}/api/rpa-ai-service"

    @staticmethod
    def _post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
        request_headers = {"content-type": "application/json"}
        if headers:
            request_headers.update(headers)
        try:
            response = requests.request(
                "POST",
                url,
                data=json.dumps(payload),
                headers=request_headers,
                timeout=180,
            )
        except requests.RequestException as exc:
            raise BizException(format_error(AI_REQ_ERROR_FORMAT, exc), f"gateway request failed: {exc}") from exc
        if response.status_code != 200:
            raise BizException(AI_SERVER_ERROR, f"ai服务器无响应或错误: {response.text}")
        return response.json()

    @staticmethod
    def post(path: str, payload: dict) -> dict:
        return GatewayClient._post_json(f"{GatewayClient._gateway_base_url()}{path}", payload)

    @staticmethod
    def post_multipart(path: str, file_bytes: bytes, filename: str, extra_fields: dict | None = None) -> dict:
        url = f"{GatewayClient._gateway_base_url()}{path}"
        files = {"file": (filename, file_bytes)}
        data = extra_fields or {}
        try:
            response = requests.post(url, files=files, data=data, timeout=180)
        except requests.RequestException as exc:
            raise BizException(
                format_error(AI_REQ_ERROR_FORMAT, exc), f"gateway multipart request failed: {exc}"
            ) from exc
        if response.status_code != 200:
            raise BizException(AI_SERVER_ERROR, f"ai服务器无响应或错误: {response.text}")
        return response.json()
