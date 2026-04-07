"""Base client for XunFei OCR APIs."""

import ssl
from typing import Any

import httpx

from app.logger import get_logger
from app.utils.ocr.auth import AuthStrategy, HmacSHA256Auth, MD5Auth, MD5HmacSHA1Auth
from app.utils.ocr.config import OCRConfig

logger = get_logger(__name__)


class OCRError(Exception):
    """Custom exception for OCR-related errors."""

    def __init__(
        self,
        msg: str,
        *,
        code: str | int | None = None,
        should_deduct_points: bool = False,
        status_code: int = 400,
        category: str | None = None,
    ):
        self.message = msg
        self.code = code
        self.should_deduct_points = should_deduct_points
        self.status_code = status_code
        self.category = category
        super().__init__(msg)


class XFYunOCRClient:
    """Base client for XunFei OCR APIs with configurable authentication and request modes."""

    def __init__(self, config: OCRConfig):
        self.config = config
        self.auth_strategy = self._create_auth_strategy()

    def _create_auth_strategy(self) -> AuthStrategy:
        """根据配置创建认证策略."""
        if self.config.auth_type == "hmac_sha256":
            return HmacSHA256Auth()
        elif self.config.auth_type == "md5_hmac_sha1":
            return MD5HmacSHA1Auth()
        elif self.config.auth_type == "md5":
            return MD5Auth()
        else:
            raise ValueError(f"Unknown auth type: {self.config.auth_type}")

    async def _make_request(
        self, method: str, url: str, headers: dict[str, Any] | None = None, **kwargs
    ) -> httpx.Response:
        """发起 HTTP 请求."""
        # 构建认证 URL 和请求头
        auth_url = self.auth_strategy.build_auth_url(url)
        auth_headers = self.auth_strategy.build_auth_headers()

        # 合并请求头
        final_headers = {**auth_headers, **(headers or {})}

        logger.debug(f"Making {method} request to {auth_url}")

        # 创建自定义SSL上下文以兼容Python 3.13
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        # 设置更宽松的密码套件和协议
        ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")
        # 允许TLSv1.2
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

        async with httpx.AsyncClient(timeout=self.config.timeout, verify=ssl_context) as client:
            response = await client.request(method, auth_url, headers=final_headers, **kwargs)

            # 如果是错误响应，记录详细信息
            if response.status_code >= 400:
                logger.error(f"Request failed with status {response.status_code}")
                logger.error(f"Response body: {response.text}")

            response.raise_for_status()
            return response
