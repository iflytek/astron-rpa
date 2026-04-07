"""Authentication strategies for XunFei OCR APIs."""

import base64
import hashlib
import hmac
from abc import ABC, abstractmethod
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

from app.config import get_settings
from app.logger import get_logger

logger = get_logger(__name__)


class AuthStrategy(ABC):
    """Abstract base class for authentication strategies."""

    def __init__(self):
        self.app_id = get_settings().XFYUN_APP_ID
        self.api_key = get_settings().XFYUN_API_KEY
        self.intsig_api_key = get_settings().XFYUN_INTSIG_API_KEY or self.api_key
        self.api_secret = get_settings().XFYUN_API_SECRET

    @abstractmethod
    def build_auth_url(self, url: str) -> str:
        """构建带认证参数的 URL."""
        pass

    @abstractmethod
    def build_auth_headers(self) -> dict:
        """构建认证请求头."""
        pass


class HmacSHA256Auth(AuthStrategy):
    """HMAC-SHA256 authentication strategy for sync OCR APIs."""

    def build_auth_url(self, url: str) -> str:
        """构建带 HMAC-SHA256 签名的 URL."""
        # 解析 URL
        stidx = url.index("://")
        host = url[stidx + 3 :]
        schema = url[: stidx + 3]
        edidx = host.index("/")
        path = host[edidx:]
        host = host[:edidx]

        # 生成时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 构建签名原文
        signature_origin = f"host: {host}\ndate: {date}\nPOST {path} HTTP/1.1"

        # 生成签名
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"), signature_origin.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode("utf-8")

        # 构建 authorization
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")

        # 构建最终 URL
        values = {"host": host, "date": date, "authorization": authorization}
        return url + "?" + urlencode(values)

    def build_auth_headers(self) -> dict:
        """构建认证请求头."""
        # 从 base_url 中提取 host
        # 例如: https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm
        # 提取: cbm01.cn-huabei-1.xf-yun.com
        return {
            "content-type": "application/json",
            "app_id": self.app_id,
        }


class MD5HmacSHA1Auth(AuthStrategy):
    """MD5 + HmacSHA1 authentication strategy for PDF OCR API."""

    def build_auth_url(self, url: str) -> str:
        """PDF OCR 不需要在 URL 中添加认证参数."""
        return url

    def build_auth_headers(self) -> dict:
        """构建 MD5 + HmacSHA1 认证请求头."""
        # 生成时间戳（秒，不是毫秒）
        import time

        timestamp = str(int(time.time()))

        # 第一步：MD5(appId + timestamp)
        md5_input = self.app_id + timestamp
        md5_hash = hashlib.md5(md5_input.encode("utf-8")).hexdigest()

        # 第二步：HmacSHA1(md5_hash, api_secret) 并 Base64 编码
        signature_bytes = hmac.new(
            self.api_secret.encode("utf-8"), md5_hash.encode("utf-8"), digestmod=hashlib.sha1
        ).digest()
        signature = base64.b64encode(signature_bytes).decode("utf-8")

        return {"appId": self.app_id, "timestamp": timestamp, "signature": signature}


class MD5Auth(AuthStrategy):
    """MD5 authentication strategy for webapi OCR APIs (bankcard, idcard, etc)."""

    def build_auth_url(self, url: str) -> str:
        """这些接口不需要在 URL 中添加认证参数."""
        return url

    def build_auth_headers(self) -> dict:
        """构建 MD5 认证请求头."""
        import json
        import time

        # 生成时间戳（秒）
        cur_time = str(int(time.time()))

        # 构建 X-Param（业务参数，Base64编码的JSON）
        param = {"language": "zh_cn", "location": "true"}
        param_base64 = base64.b64encode(json.dumps(param).encode("utf-8")).decode("utf-8")

        # 计算 X-CheckSum: MD5(APIKey + X-CurTime + X-Param)
        checksum_input = self.intsig_api_key + cur_time + param_base64
        checksum = hashlib.md5(checksum_input.encode("utf-8")).hexdigest()

        return {
            "X-Appid": self.app_id,
            "X-CurTime": cur_time,
            "X-Param": param_base64,
            "X-CheckSum": checksum,
        }
