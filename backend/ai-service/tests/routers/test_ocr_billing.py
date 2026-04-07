from datetime import UTC, datetime, timedelta
import base64

import pytest
from sqlalchemy import select

from app.models.point import PointAllocation, PointTransaction, PointTransactionType
from app.routers import ocr as ocr_router
from app.schemas.ocr import (
    OCRGeneralDecodedResponseBody,
    OCRGeneralResponseInnerHeader,
    DocumentOCRResponse,
    DocumentOCRResponseHeader,
    DocumentOCRResponsePayload,
    DocumentOCRResponseResult,
    PDFOCRResponsePayload,
)
from app.utils.ocr.base import OCRError


async def _seed_monthly_grant(session, user_id: str, amount: int = 1000):
    allocation = PointAllocation(
        user_id=user_id,
        initial_amount=amount,
        remaining_amount=amount,
        allocation_type=PointTransactionType.MONTHLY_GRANT.value,
        priority=50,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        description="test monthly grant",
    )
    session.add(allocation)
    await session.flush()


async def _xfyun_cost_count(session, user_id: str) -> int:
    result = await session.execute(
        select(PointTransaction).where(
            PointTransaction.user_id == user_id,
            PointTransaction.transaction_type == PointTransactionType.XFYUN_COST.value,
        )
    )
    return len(result.scalars().all())


@pytest.mark.asyncio
async def test_bank_card_billable_failure_deducts_points(client, test_get_db):
    user_id = "ocr-billable-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(self, file):
        raise OCRError("fail to recognize", should_deduct_points=True, status_code=400, code="101")

    original = ocr_router.BankCardOCRClient.recognize
    ocr_router.BankCardOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/bank-card",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.BankCardOCRClient.recognize = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 400
    assert after == before + 1


@pytest.mark.asyncio
async def test_vat_invoice_non_billable_failure_does_not_deduct_points(client, test_get_db):
    user_id = "ocr-non-billable-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(self, file):
        raise OCRError("illegal image format", should_deduct_points=False, status_code=400, code="40204")

    original = ocr_router.VATInvoiceOCRClient.recognize
    ocr_router.VATInvoiceOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/vat-invoice",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.VATInvoiceOCRClient.recognize = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 400
    assert after == before


@pytest.mark.asyncio
async def test_document_success_deducts_points(client, test_get_db):
    user_id = "ocr-success-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(self, image_base64, encoding="jpg", output_level=1, output_format="markdown"):
        return DocumentOCRResponse(
            header=DocumentOCRResponseHeader(code=0, message="success", sid="test-sid"),
            payload=DocumentOCRResponsePayload(
                result=DocumentOCRResponseResult(
                    compress="raw",
                    encoding="utf8",
                    format="plain",
                    text="dGVzdA==",
                )
            ),
        )

    original = ocr_router.DocumentOCRClient.recognize
    ocr_router.DocumentOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/document",
            headers={"X-User-Id": user_id},
            json={"image": "dGVzdA==", "encoding": "jpg", "output_level": 1, "output_format": "json"},
        )
    finally:
        ocr_router.DocumentOCRClient.recognize = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 200
    assert after == before + 1


@pytest.mark.asyncio
async def test_general_ocr_returns_decoded_data(client, test_get_db):
    user_id = "ocr-general-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_recognize(image_base64, image_encoding="jpg", status=3, timeout=30.0):
        return OCRGeneralDecodedResponseBody(
            header=OCRGeneralResponseInnerHeader(code=0, message="success", sid="general-sid"),
            data={"text": "hello", "blocks": [{"content": "hello"}]},
        )

    original = ocr_router.recognize_text_from_image
    ocr_router.recognize_text_from_image = fake_recognize
    try:
        response = await client.post(
            "/ocr/general",
            headers={"X-User-Id": user_id},
            json={"image": base64.b64encode(b"fake-image").decode("utf-8"), "encoding": "jpg", "status": 3},
        )
    finally:
        ocr_router.recognize_text_from_image = original

    after = await _xfyun_cost_count(test_get_db, user_id)

    assert response.status_code == 200
    assert response.json() == {
        "header": {
            "code": 0,
            "message": "success",
            "sid": "general-sid",
        },
        "data": {
            "text": "hello",
            "blocks": [{"content": "hello"}],
        },
    }
    assert after == before + 1


@pytest.mark.asyncio
async def test_id_card_success_passthrough_response(client, test_get_db):
    user_id = "ocr-id-card-user"
    await _seed_monthly_grant(test_get_db, user_id)

    async def fake_recognize(self, file):
        return {
            "name": "Alice",
            "id_number": "1234567890",
            "birthday": "2019年06月07日",
            "error_code": 0,
            "error_msg": "OK",
            "time_cost": {"preprocess": 35, "recognize": 142},
        }

    original = ocr_router.IDCardOCRClient.recognize
    ocr_router.IDCardOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/id-card",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.IDCardOCRClient.recognize = original

    assert response.status_code == 200
    assert response.json() == {
        "code": "0",
        "desc": "success",
        "data": {
            "name": "Alice",
            "id_number": "1234567890",
            "birthday": "2019年06月07日",
            "error_code": 0,
            "error_msg": "OK",
            "time_cost": {"preprocess": 35, "recognize": 142},
        },
        "sid": None,
    }


@pytest.mark.asyncio
async def test_bank_card_success_passthrough_response(client, test_get_db):
    user_id = "ocr-bank-card-user"
    await _seed_monthly_grant(test_get_db, user_id)

    async def fake_recognize(self, file):
        return {
            "bank_name": "招商银行",
            "card_no": "6222021234567890",
            "card_type": "debit",
        }

    original = ocr_router.BankCardOCRClient.recognize
    ocr_router.BankCardOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/bank-card",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.BankCardOCRClient.recognize = original

    assert response.status_code == 200
    assert response.json() == {
        "code": "0",
        "desc": "success",
        "data": {
            "bank_name": "招商银行",
            "card_no": "6222021234567890",
            "card_type": "debit",
        },
        "sid": None,
    }


@pytest.mark.asyncio
async def test_business_card_success_passthrough_response(client, test_get_db):
    user_id = "ocr-business-card-user"
    await _seed_monthly_grant(test_get_db, user_id)

    async def fake_recognize(self, file):
        return {
            "address": [
                {
                    "item": {"street": "Dale Ol Birth", "type": ["work"]},
                    "position": "298,272,378,272,379,288,298,288",
                }
            ],
            "nickname": [
                {
                    "item": "ZHENGJ I AN,YANGBEN",
                    "position": "72,345,349,345,349,368,72,368",
                }
            ],
            "organization": [
                {
                    "item": {"unit": "加拿大/CAN"},
                    "position": "72,175,207,174,208,198,72,198",
                }
            ],
            "telephone": [
                {
                    "item": {"number": "19810803", "type": ["work", "voice"]},
                    "position": "227,242,341,241,341,260,227,260",
                }
            ],
        }

    original = ocr_router.BusinessCardOCRClient.recognize
    ocr_router.BusinessCardOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/business-card",
            headers={"X-User-Id": user_id},
            files={"file": ("test.jpg", b"fake-image", "image/jpeg")},
        )
    finally:
        ocr_router.BusinessCardOCRClient.recognize = original

    assert response.status_code == 200
    assert response.json() == {
        "code": "0",
        "desc": "success",
        "data": {
            "address": [
                {
                    "item": {"street": "Dale Ol Birth", "type": ["work"]},
                    "position": "298,272,378,272,379,288,298,288",
                }
            ],
            "nickname": [
                {
                    "item": "ZHENGJ I AN,YANGBEN",
                    "position": "72,345,349,345,349,368,72,368",
                }
            ],
            "organization": [
                {
                    "item": {"unit": "加拿大/CAN"},
                    "position": "72,175,207,174,208,198,72,198",
                }
            ],
            "telephone": [
                {
                    "item": {"number": "19810803", "type": ["work", "voice"]},
                    "position": "227,242,341,241,341,260,227,260",
                }
            ],
        },
        "sid": None,
    }


@pytest.mark.asyncio
async def test_pdf_url_json_request_is_accepted(client, test_get_db):
    user_id = "ocr-pdf-url-user"
    await _seed_monthly_grant(test_get_db, user_id)

    async def fake_recognize(self, file=None, pdf_url=None, export_format="json"):
        assert file is None
        assert pdf_url == "https://example.com/test.pdf"
        assert export_format == "markdown"
        return PDFOCRResponsePayload(
            task_no="task-123",
            status="FINISH",
            page_count=2,
            result_url="https://example.com/result.md",
        )

    original = ocr_router.PDFOCRClient.recognize
    ocr_router.PDFOCRClient.recognize = fake_recognize
    try:
        response = await client.post(
            "/ocr/pdf",
            headers={"X-User-Id": user_id},
            json={"pdf_url": "https://example.com/test.pdf", "export_format": "markdown"},
        )
    finally:
        ocr_router.PDFOCRClient.recognize = original

    assert response.status_code == 200
    assert response.json() == {
        "payload": {
            "task_no": "task-123",
            "status": "FINISH",
            "page_count": 2,
            "result_url": "https://example.com/result.md",
        }
    }
