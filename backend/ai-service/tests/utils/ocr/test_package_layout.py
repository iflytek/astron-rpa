"""Regression tests for OCR package layout and route naming."""

import importlib


def test_ocr_package_exports_general_and_specialized_clients():
    module = importlib.import_module("app.utils.ocr")

    assert hasattr(module, "OCRError")
    assert hasattr(module, "recognize_text_from_image")
    assert hasattr(module, "DocumentOCRClient")
    assert hasattr(module, "PDFOCRClient")
    assert hasattr(module, "TicketOCRClient")
    assert hasattr(module, "BusinessCardOCRClient")
    assert hasattr(module, "IDCardOCRClient")
    assert hasattr(module, "BankCardOCRClient")
    assert hasattr(module, "BusinessLicenseOCRClient")
    assert hasattr(module, "VATInvoiceOCRClient")


def test_ocr_router_keeps_legacy_general_route_and_uses_canonical_new_routes(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql+aiomysql://user:pass@localhost:3306/test_db")
    config_module = importlib.import_module("app.config")
    config_module.get_settings.cache_clear()
    module = importlib.import_module("app.routers.ocr")
    route_paths = {route.path for route in module.router.routes}

    assert "/ocr/general" in route_paths
    assert "/ocr/document" in route_paths
    assert "/ocr/pdf" in route_paths
    assert "/ocr/ticket" in route_paths
    assert "/ocr/business-card" in route_paths
    assert "/ocr/id-card" in route_paths
    assert "/ocr/bank-card" in route_paths
    assert "/ocr/business-license" in route_paths
    assert "/ocr/vat-invoice" in route_paths
