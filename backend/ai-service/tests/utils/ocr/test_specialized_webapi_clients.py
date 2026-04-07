"""Tests for specialized webapi OCR client request formatting."""

import pytest

from app.utils.ocr.vat_invoice_ocr import VATInvoiceOCRClient


class _FakeUploadFile:
    def __init__(self, content: bytes):
        self.content = content

    async def read(self) -> bytes:
        return self.content


class _FakeResponse:
    def json(self):
        return {"code": "0", "desc": "success", "data": {}}


@pytest.mark.asyncio
async def test_vat_invoice_client_uses_http_endpoint_and_raw_base64(monkeypatch):
    client = VATInvoiceOCRClient()
    captured = {}

    async def fake_make_request(method, url, headers=None, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["data"] = kwargs["data"]
        return _FakeResponse()

    monkeypatch.setattr(client, "_make_request", fake_make_request)

    await client.recognize(_FakeUploadFile(b"\xfb\xff"))

    assert captured["method"] == "POST"
    assert captured["url"].startswith("http://webapi.xfyun.cn/")
    assert captured["data"]["image"] == "+/8="
