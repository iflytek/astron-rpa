import json
from urllib.parse import urljoin

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import get_settings
from app.models.smart_component import SmartChatResponse
from app.schemas.chat import ChatCompletionParam
from app.services.chat import chat_completions

router = APIRouter(
    prefix="/cua",
    tags=["计算机使用代理"],
)
CUA_KEY = get_settings().CUA_API_KEY
CUA_ENDPOINT = urljoin(get_settings().CUA_BASE_URL, "chat/completions")


class CUAChatRequest(BaseModel):
    messages: list[dict] = Field(..., min_length=1)
    model: str = Field(default="", examples=["doubao-seed-1-8-251228"])


@router.post("/chat/stream")
async def cua_chat_stream(request: CUAChatRequest):
    llm_params = ChatCompletionParam(
        model=request.model,
        stream=True,
        temperature=0,
        max_tokens=8192,
        messages=request.messages,
    )

    return await chat_completions(llm_params, CUA_KEY, CUA_ENDPOINT)


@router.post("/chat", response_model=SmartChatResponse)
async def cua_chat(request: CUAChatRequest):
    # 添加日志，查看接收到的请求
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[CUA Chat] 接收到请求 - model: {request.model}, messages数量: {len(request.messages)}")

    llm_params = ChatCompletionParam(
        model=request.model,
        stream=False,
        temperature=0,
        max_tokens=8192,
        messages=request.messages,
    )

    chat_result = await chat_completions(llm_params, CUA_KEY, CUA_ENDPOINT)

    return SmartChatResponse(data=json.loads(chat_result.body), code=200, success=True)
