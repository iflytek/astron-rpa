"""Tests for OCR error classification policy."""

from app.utils.ocr.error_policy import OCRFailureCategory, classify_ocr_failure


def test_fail_to_recognize_is_billable_failure():
    decision = classify_ocr_failure(code="101", message="fail to recognize")

    assert decision.category is OCRFailureCategory.BILLABLE_FAILURE
    assert decision.should_deduct_points is True
    assert decision.http_status == 400


def test_illegal_image_format_is_non_billable_failure():
    decision = classify_ocr_failure(code="40204", message="illegal parameter|illegal image format")

    assert decision.category is OCRFailureCategory.NON_BILLABLE_FAILURE
    assert decision.should_deduct_points is False
    assert decision.http_status == 400


def test_illegal_checksum_is_non_billable_failure():
    decision = classify_ocr_failure(code="40203", message="illegal access|illegal X-CheckSum")

    assert decision.category is OCRFailureCategory.NON_BILLABLE_FAILURE
    assert decision.should_deduct_points is False
    assert decision.http_status == 400
