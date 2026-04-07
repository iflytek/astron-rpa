"""Unit tests for OCR authentication strategies."""

import base64
import hashlib
from unittest.mock import patch

from app.config import get_settings
from app.utils.ocr.auth import HmacSHA256Auth, MD5Auth, MD5HmacSHA1Auth


class TestHmacSHA256Auth:
    """Test HMAC-SHA256 authentication strategy."""

    def test_build_auth_url(self):
        """Test building authenticated URL."""
        auth = HmacSHA256Auth()
        url = "https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm"

        auth_url = auth.build_auth_url(url)

        # Check that URL contains required parameters
        assert "host=" in auth_url
        assert "date=" in auth_url
        assert "authorization=" in auth_url
        assert url in auth_url

    def test_build_auth_headers(self):
        """Test building authentication headers."""
        auth = HmacSHA256Auth()

        headers = auth.build_auth_headers()

        assert "content-type" in headers
        assert headers["content-type"] == "application/json"
        assert "app_id" in headers


class TestMD5HmacSHA1Auth:
    """Test MD5 + HmacSHA1 authentication strategy."""

    def test_build_auth_url(self):
        """Test that URL is returned unchanged."""
        auth = MD5HmacSHA1Auth()
        url = "https://iocr.xfyun.cn/ocrzdq/v1/pdfOcr/start"

        auth_url = auth.build_auth_url(url)

        # URL should be unchanged for this auth type
        assert auth_url == url

    def test_build_auth_headers(self):
        """Test building authentication headers."""
        auth = MD5HmacSHA1Auth()

        headers = auth.build_auth_headers()

        # Check required headers
        assert "appId" in headers
        assert "timestamp" in headers
        assert "signature" in headers

        # Timestamp should be numeric
        assert headers["timestamp"].isdigit()

        # Signature is a Base64-encoded HMAC-SHA1 digest
        assert len(headers["signature"]) == 28
        assert base64.b64decode(headers["signature"])


class TestMD5Auth:
    """Test MD5 authentication strategy for specialized OCR APIs."""

    def test_build_auth_headers_uses_intsig_api_key_for_checksum(self, monkeypatch):
        monkeypatch.setenv("XFYUN_APP_ID", "demo-app-id")
        monkeypatch.setenv("XFYUN_API_KEY", "general-api-key")
        monkeypatch.setenv("XFYUN_INTSIG_API_KEY", "intsig-api-key")
        get_settings.cache_clear()

        auth = MD5Auth()

        with patch("time.time", return_value=1700000000):
            headers = auth.build_auth_headers()

        expected_checksum = hashlib.md5(
            f"intsig-api-key{headers['X-CurTime']}{headers['X-Param']}".encode("utf-8")
        ).hexdigest()

        assert headers["X-CheckSum"] == expected_checksum
