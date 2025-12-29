from urllib.parse import urljoin

from fastapi import HTTPException

from app.config import get_settings
from app.logger import get_logger
from app.routers.v1.chat import handle_stream_request, handle_non_stream_request
from app.schemas.chat import ChatCompletionParam

API_KEY = get_settings().AICHAT_API_KEY
API_ENDPOINT = urljoin(get_settings().AICHAT_BASE_URL, "chat/completions")

logger = get_logger(__name__)


async def chat_completions(
    params: ChatCompletionParam,
):
    logger.info("Processing chat completion request...")
    logger.info(f"Request params: {params}")
    # 构造请求参数
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = params.model_dump(exclude_none=True)

    logger.info(f"Request params.stream: {params.stream}")
    # 处理请求
    try:
        if params.stream:
            response = await handle_stream_request(headers, data)
        else:
            response = await handle_non_stream_request(headers, data)

        return response
    except HTTPException as e:
        logger.warning(f"HTTP error: {e.detail}")
        raise e
    except Exception:
        logger.error("Internal server error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")