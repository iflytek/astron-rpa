from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models.point import PointAllocation, PointTransaction, PointTransactionType
from app.routers import nlp as nlp_router
from app.schemas.nlp import (
    TextCorrectionResponseBody,
    TextCorrectionResponseHeader,
    TextModerationCategory,
    TextModerationData,
    TextModerationDetail,
    TextModerationResponseBody,
    TextModerationResult,
    TranslationDecodedResult,
    TranslationDecodedResultData,
    TranslationResponseBody,
    TranslationResponseData,
)
from app.utils.nlp import TextCorrectionError, TextModerationError, TranslationError


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
async def test_text_correction_success_deducts_points(client, test_get_db):
    user_id = "nlp-success-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_correct_text(text: str, uid: str | None = None, res_id: str | None = None):
        assert uid is None
        assert res_id is None
        return TextCorrectionResponseBody(
            header=TextCorrectionResponseHeader(code=0, message="success", sid="sid-1"),
            result={"char": [], "word": []},
        )

    original = nlp_router.correct_text
    nlp_router.correct_text = fake_correct_text
    try:
        response = await client.post(
            "/nlp/text-correction",
            headers={"X-User-Id": user_id},
            json={"text": "需要纠错的文本"},
        )
    finally:
        nlp_router.correct_text = original

    after = await _xfyun_cost_count(test_get_db, user_id)
    assert response.status_code == 200
    assert "payload" not in response.json()
    assert response.json()["result"]["char"] == []
    assert after == before + 1


@pytest.mark.asyncio
async def test_text_correction_business_error_does_not_deduct_points(client, test_get_db):
    user_id = "nlp-error-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_correct_text(text: str, uid: str | None = None, res_id: str | None = None):
        raise TextCorrectionError("illegal parameter")

    original = nlp_router.correct_text
    nlp_router.correct_text = fake_correct_text
    try:
        response = await client.post(
            "/nlp/text-correction",
            headers={"X-User-Id": user_id},
            json={"text": "需要纠错的文本"},
        )
    finally:
        nlp_router.correct_text = original

    after = await _xfyun_cost_count(test_get_db, user_id)
    assert response.status_code == 400
    assert response.json()["detail"] == "illegal parameter"
    assert after == before


@pytest.mark.asyncio
async def test_text_moderation_success_deducts_points(client, test_get_db):
    user_id = "nlp-moderation-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_moderate_text(content: str, is_match_all: int = 0, categories=None, lib_ids=None):
        return TextModerationResponseBody(
            code="000000",
            desc="成功",
            sid="sid-moderation",
            data=TextModerationData(
                request_id="req-1",
                result=TextModerationResult(
                    suggest="pass",
                    detail=TextModerationDetail(
                        content=content,
                        category_list=[
                            TextModerationCategory(
                                confidence=0,
                                category="political",
                                suggest="pass",
                                category_description="涉政",
                                word_list=[],
                                word_infos=[],
                            )
                        ],
                    ),
                ),
            ),
        )

    original = nlp_router.moderate_text
    nlp_router.moderate_text = fake_moderate_text
    try:
        response = await client.post(
            "/nlp/text-moderation",
            headers={"X-User-Id": user_id},
            json={"content": "测试文本"},
        )
    finally:
        nlp_router.moderate_text = original

    after = await _xfyun_cost_count(test_get_db, user_id)
    assert response.status_code == 200
    assert response.json()["code"] == "000000"
    assert after == before + 1


@pytest.mark.asyncio
async def test_text_moderation_business_error_does_not_deduct_points(client, test_get_db):
    user_id = "nlp-moderation-error-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_moderate_text(content: str, is_match_all: int = 0, categories=None, lib_ids=None):
        raise TextModerationError("moderation failed")

    original = nlp_router.moderate_text
    nlp_router.moderate_text = fake_moderate_text
    try:
        response = await client.post(
            "/nlp/text-moderation",
            headers={"X-User-Id": user_id},
            json={"content": "测试文本"},
        )
    finally:
        nlp_router.moderate_text = original

    after = await _xfyun_cost_count(test_get_db, user_id)
    assert response.status_code == 400
    assert response.json()["detail"] == "moderation failed"
    assert after == before


@pytest.mark.asyncio
async def test_translation_success_deducts_points(client, test_get_db):
    user_id = "nlp-translation-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_translate_text(text: str, from_lang: str, to: str):
        return TranslationResponseBody(
            code=0,
            message="success",
            sid="sid-translation",
            data=TranslationResponseData(
                result=TranslationDecodedResult(
                    **{
                        "from": from_lang,
                        "to": to,
                        "trans_result": TranslationDecodedResultData(src=text, dst="Hello World"),
                    }
                )
            ),
        )

    original = nlp_router.translate_text
    nlp_router.translate_text = fake_translate_text
    try:
        response = await client.post(
            "/nlp/translate",
            headers={"X-User-Id": user_id},
            json={"text": "你好世界", "from": "cn", "to": "en"},
        )
    finally:
        nlp_router.translate_text = original

    after = await _xfyun_cost_count(test_get_db, user_id)
    assert response.status_code == 200
    assert response.json()["data"]["result"]["trans_result"]["dst"] == "Hello World"
    assert after == before + 1


@pytest.mark.asyncio
async def test_translation_business_error_does_not_deduct_points(client, test_get_db):
    user_id = "nlp-translation-error-user"
    await _seed_monthly_grant(test_get_db, user_id)
    before = await _xfyun_cost_count(test_get_db, user_id)

    async def fake_translate_text(text: str, from_lang: str, to: str):
        raise TranslationError("translation failed")

    original = nlp_router.translate_text
    nlp_router.translate_text = fake_translate_text
    try:
        response = await client.post(
            "/nlp/translate",
            headers={"X-User-Id": user_id},
            json={"text": "你好世界", "from": "cn", "to": "en"},
        )
    finally:
        nlp_router.translate_text = original

    after = await _xfyun_cost_count(test_get_db, user_id)
    assert response.status_code == 400
    assert response.json()["detail"] == "translation failed"
    assert after == before


@pytest.mark.asyncio
async def test_text_correction_requires_user_header(client):
    response = await client.post("/nlp/text-correction", json={"text": "需要纠错的文本"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-User-Id or user_id header."
