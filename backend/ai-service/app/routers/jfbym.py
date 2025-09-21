from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.logger import get_logger
from app.schemas.jfbym import JFBYMGeneralRequestBody, JFBYMGeneralResponseBody
from app.utils.jfbym import verify_captcha, CaptchaVerificationError
from app.services.point import PointTransactionType
from app.dependencies.points import PointChecker, PointsContext
from app.config import get_settings


logger = get_logger(__name__)

router = APIRouter(
    prefix="/jfbym",
    tags=["云码验证码"],
)


@router.post("/customApi", response_model=JFBYMGeneralResponseBody)
async def general(
    params: JFBYMGeneralRequestBody,
    points_context: PointsContext = Depends(
        PointChecker(get_settings().JFBYM_POINTS_COST, PointTransactionType.JFBYM_COST),
    ),
):
    try:
        result = await verify_captcha(params.type, params.image)
        if result.code == 10000 and result.data.code == 0:
            # 成功时才扣除积分
            await points_context.deduct_points()
            logger.info("JFBYM processing successful, points deducted for user")
        else:
            # API返回错误，不扣除积分
            error_message = result.get("message", "Unknown API error")
            logger.warning(f"JFBYM API returned error: {error_message}")
        return result

    except CaptchaVerificationError as e:
        # 业务逻辑错误 - 返回错误信息
        logger.error(f"JFBYM business logic error: {e.message}")
        return JFBYMGeneralResponseBody(
            code=400,
            message=f"云码验证码处理失败: {e.message}",
            data=None
        )

    except httpx.HTTPError as e:
        # 网络错误 - 返回错误信息
        logger.error(f"JFBYM service network error: {e}")
        return JFBYMGeneralResponseBody(
            code=503,
            message="云码验证码服务暂时不可用，请稍后重试",
            data=None
        )

    except Exception as e:
        # 其他未预期的错误 - 返回错误信息
        logger.error(f"Unexpected error in JFBYM processing: {e}")
        return JFBYMGeneralResponseBody(
            code=500,
            message="云码验证码处理过程中发生未知错误",
            data=None
        )
