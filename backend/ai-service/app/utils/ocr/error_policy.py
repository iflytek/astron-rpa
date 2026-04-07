"""Centralized OCR error classification policy."""

from dataclasses import dataclass
from enum import Enum


class OCRFailureCategory(str, Enum):
    BILLABLE_FAILURE = "billable_failure"
    NON_BILLABLE_FAILURE = "non_billable_failure"
    UPSTREAM_UNAVAILABLE = "upstream_unavailable"


@dataclass(frozen=True)
class OCRFailureDecision:
    category: OCRFailureCategory
    should_deduct_points: bool
    http_status: int


_NON_BILLABLE_KEYWORDS = (
    "illegal",
    "invalid",
    "parameter",
    "format",
    "checksum",
    "signature",
    "appid",
    "auth",
    "unauthorized",
    "permission",
    "forbidden",
    "quota",
)

_BILLABLE_KEYWORDS = (
    "fail to recognize",
    "recognize failed",
    "识别失败",
)


def classify_ocr_failure(code: str | int | None, message: str | None) -> OCRFailureDecision:
    text = (message or "").lower()

    if any(keyword in text for keyword in _NON_BILLABLE_KEYWORDS):
        return OCRFailureDecision(
            category=OCRFailureCategory.NON_BILLABLE_FAILURE,
            should_deduct_points=False,
            http_status=400,
        )

    if any(keyword in text for keyword in _BILLABLE_KEYWORDS):
        return OCRFailureDecision(
            category=OCRFailureCategory.BILLABLE_FAILURE,
            should_deduct_points=True,
            http_status=400,
        )

    if code not in (None, 0, "0"):
        return OCRFailureDecision(
            category=OCRFailureCategory.BILLABLE_FAILURE,
            should_deduct_points=True,
            http_status=400,
        )

    return OCRFailureDecision(
        category=OCRFailureCategory.NON_BILLABLE_FAILURE,
        should_deduct_points=False,
        http_status=400,
    )
