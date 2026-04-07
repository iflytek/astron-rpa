import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.config import get_settings
from app.dependencies.points import PointChecker, PointsContext
from app.logger import get_logger
from app.schemas.nlp import (
    TextCorrectionRequestBody,
    TextCorrectionResponseBody,
    TextModerationRequestBody,
    TextModerationResponseBody,
    TranslationRequestBody,
    TranslationResponseBody,
)
from app.services.point import PointTransactionType
from app.utils.nlp import (
    TextCorrectionError,
    TextModerationError,
    TranslationError,
    correct_text,
    moderate_text,
    translate_text,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/nlp", tags=["开放平台NLP"])


@router.post("/text-correction", response_model=TextCorrectionResponseBody)
async def text_correction(
    params: TextCorrectionRequestBody,
    points_context: PointsContext = Depends(
        PointChecker(get_settings().XFYUN_TEXT_CORRECTION_POINTS_COST, PointTransactionType.XFYUN_COST),
    ),
):
    try:
        result = await correct_text(params.text, uid=params.uid, res_id=params.res_id)
        await points_context.deduct_points()
        logger.info("Text correction successful, points deducted")
        return result
    except TextCorrectionError as exc:
        logger.error(f"Text correction business error: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except httpx.HTTPError as exc:
        logger.error(f"Text correction upstream network error: {exc}")
        raise HTTPException(status_code=503, detail="Text correction service is temporarily unavailable.")
    except Exception as exc:
        logger.error(f"Unexpected error in text correction: {exc}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during text correction.")


@router.post("/text-moderation", response_model=TextModerationResponseBody)
async def text_moderation(
    params: TextModerationRequestBody,
    points_context: PointsContext = Depends(
        PointChecker(get_settings().XFYUN_TEXT_MODERATION_POINTS_COST, PointTransactionType.XFYUN_COST),
    ),
):
    try:
        result = await moderate_text(
            params.content,
            is_match_all=params.is_match_all,
            categories=params.categories,
            lib_ids=params.lib_ids,
        )
        await points_context.deduct_points()
        logger.info("Text moderation successful, points deducted")
        return result
    except TextModerationError as exc:
        logger.error(f"Text moderation business error: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except httpx.HTTPError as exc:
        logger.error(f"Text moderation upstream network error: {exc}")
        raise HTTPException(status_code=503, detail="Text moderation service is temporarily unavailable.")
    except Exception as exc:
        logger.error(f"Unexpected error in text moderation: {exc}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during text moderation.")


@router.post("/translate", response_model=TranslationResponseBody)
async def translation(
    params: TranslationRequestBody,
    points_context: PointsContext = Depends(
        PointChecker(get_settings().XFYUN_TRANSLATION_POINTS_COST, PointTransactionType.XFYUN_COST),
    ),
):
    try:
        result = await translate_text(params.text, from_lang=params.from_lang, to=params.to)
        await points_context.deduct_points()
        logger.info("Translation successful, points deducted")
        return result
    except TranslationError as exc:
        logger.error(f"Translation business error: {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except httpx.HTTPError as exc:
        logger.error(f"Translation upstream network error: {exc}")
        raise HTTPException(status_code=503, detail="Translation service is temporarily unavailable.")
    except Exception as exc:
        logger.error(f"Unexpected error in translation: {exc}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during translation.")
