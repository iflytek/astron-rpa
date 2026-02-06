import json
from urllib.parse import urljoin

from fastapi import APIRouter, Body

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


@router.post("/chat/stream")
async def cua_chat_stream(messages: list[dict] = Body(...)):
    llm_params = ChatCompletionParam(
        model="doubao-seed-1-8-251228",
        stream=True,
        temperature=0,
        max_tokens=8192,
        messages=messages,
    )

    return await chat_completions(llm_params, CUA_KEY, CUA_ENDPOINT)


@router.post("/chat", response_model=SmartChatResponse)
async def cua_chat(messages: list[dict] = Body(...)):
    llm_params = ChatCompletionParam(
        model="doubao-seed-1-8-251228",
        stream=False,
        temperature=0,
        max_tokens=8192,
        messages=messages,
    )

    chat_result = await chat_completions(llm_params, CUA_KEY, CUA_ENDPOINT)

    return SmartChatResponse(data=json.loads(chat_result.body), code=200, success=True)
