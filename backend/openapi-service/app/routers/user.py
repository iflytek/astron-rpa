from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.schemas.user import UserRegisterRequest, UserRegisterResponse
from app.dependencies import get_user_service, verify_register_bearer_token
from app.logger import get_logger
from app.schemas import StandardResponse, ResCode

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
    """用户注册接口"""
    try:
        phone = request.phone
        logger.info(f"用户注册请求，phone: {phone}")

        # 调用服务层进行注册
        result = await service.register_user(phone)

        if not result:
            logger.error(f"用户注册失败，phone: {phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户注册失败",
            )

        # 构建返回数据
        response_data = UserRegisterResponse(
            user_id=result.get("user_id") or "",
            api_key=result.get("api_key") or "",
            account=result.get("account") or "",
            password=result.get("password") or "",
            url=result.get("url") or "",
        )

        logger.info(f"用户注册成功，phone: {phone}, user_id: {result.get('user_id')}")

        return StandardResponse(
            code=ResCode.SUCCESS,
            msg="注册成功",
            data=response_data.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册过程中出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误",
        )
