from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service, verify_getkey_bearer_token, verify_register_bearer_token
from app.logger import get_logger
from app.schemas import ResCode, StandardResponse
from app.schemas.user import UserAPIKeyResponse, UserRegisterRequest
from app.services.user import UserService

logger = get_logger(__name__)


router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.post(
    "/register",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="用户注册",
    description="根据手机号进行用户注册，返回api_key、密码和下载链接",
)
async def register_user(
    request: UserRegisterRequest,
    service: UserService = Depends(get_user_service),
    token: str = Depends(verify_register_bearer_token),
):
    """获取API_KEY接口"""
    try:
        phone = request.phone
        logger.info(f"用户获取API_KEY接口请求，phone: {phone}")

        # 调用服务层进行获取
        result = await service.get_user_info(phone)

        if not result:
            logger.error(f"用户获取API_KEY失败，phone: {phone}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未注册",
            )

        # 构建返回数据
        response_data = UserAPIKeyResponse(user_id=result.get("user_id") or "", api_key=result.get("api_key") or "")

        logger.info(f"用户注册成功，phone: {phone}, user_id: {result.get('user_id')}")

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="获取API_KEY成功",
            data=response_data.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户获取API_KEY过程中出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误",
        )


@router.post(
    "/get-key",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="用户获取API_KEY",
    description="根据手机号获取API_KEY",
)
async def get_user_api_key(
    request: UserRegisterRequest,
    service: UserService = Depends(get_user_service),
    token: str = Depends(verify_getkey_bearer_token),
):
    """获取API_KEY接口"""
    try:
        phone = request.phone
        logger.info(f"用户获取API_KEY接口请求，phone: {phone}")

        # 调用服务层进行获取
        result = await service.get_user_info(phone)

        if not result:
            logger.error(f"用户获取API_KEY失败，phone: {phone}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未注册",
            )

        # 构建返回数据
        response_data = UserAPIKeyResponse(user_id=result.get("user_id") or "", api_key=result.get("api_key") or "")

        logger.info(f"用户获取API_KEY成功，phone: {phone}, user_id: {result.get('user_id')}")

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="获取API_KEY成功",
            data=response_data.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户获取API_KEY过程中出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误",
        )
