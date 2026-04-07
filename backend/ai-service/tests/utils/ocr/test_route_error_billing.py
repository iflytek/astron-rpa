"""Tests for OCR route error billing behavior."""

import importlib

import pytest
from fastapi import HTTPException

from app.config import get_settings
from app.utils.ocr.base import OCRError


class _FakePointsContext:
    def __init__(self):
        self.deduct_called = False

    async def deduct_points(self):
        self.deduct_called = True


@pytest.mark.asyncio
async def test_route_error_handler_deducts_points_for_billable_failure(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/test_db")
    get_settings.cache_clear()
    module = importlib.import_module("app.routers.ocr")
    points_context = _FakePointsContext()

    with pytest.raises(HTTPException) as exc_info:
        await module._raise_ocr_http_error(
            "Bank card OCR",
            OCRError("fail to recognize", should_deduct_points=True, status_code=400),
            points_context,
        )

    assert points_context.deduct_called is True
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_route_error_handler_skips_points_for_non_billable_failure(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/test_db")
    get_settings.cache_clear()
    module = importlib.import_module("app.routers.ocr")
    points_context = _FakePointsContext()

    with pytest.raises(HTTPException) as exc_info:
        await module._raise_ocr_http_error(
            "VAT invoice OCR",
            OCRError("illegal image format", should_deduct_points=False, status_code=400),
            points_context,
        )

    assert points_context.deduct_called is False
    assert exc_info.value.status_code == 400
