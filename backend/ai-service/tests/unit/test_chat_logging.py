"""Chat logs must not retain prompts or upstream diagnostics containing secrets."""

import json
import logging
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from fastapi.responses import Response

MARKER = "private-input-key-and-provider-body-48d2"


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["status", "timeout", "network"])
async def test_completion_failure_logs_are_sanitized(monkeypatch, caplog, failure):
    from app.schemas.chat import ChatCompletionParam
    from app.services import chat

    request = httpx.Request("POST", f"https://model.invalid/v1?key={MARKER}")
    errors = {
        "status": httpx.HTTPStatusError(
            MARKER,
            request=request,
            response=httpx.Response(401, request=request, text=MARKER),
        ),
        "timeout": httpx.ReadTimeout(MARKER, request=request),
        "network": httpx.ConnectError(MARKER, request=request),
    }

    async def fail_post(*args, **kwargs):
        assert kwargs["headers"]["Authorization"] == f"Bearer {MARKER}"
        assert kwargs["json"]["messages"][0]["content"] == MARKER
        raise errors[failure]

    monkeypatch.setattr(httpx.AsyncClient, "post", fail_post)
    params = ChatCompletionParam(
        model="synthetic", stream=False, messages=[{"role": "user", "content": MARKER}]
    )
    with caplog.at_level(logging.INFO), pytest.raises(HTTPException) as caught:
        await chat.chat_completions(params, key=MARKER, endpoint=str(request.url))
    assert (
        caught.value.status_code
        == {"status": 401, "timeout": 504, "network": 500}[failure]
    )
    assert MARKER not in caplog.text
    assert all(record.exc_info is None for record in caplog.records)


@pytest.mark.asyncio
async def test_prompt_logs_omit_formatted_input_and_result(monkeypatch, caplog):
    from app.routers.v1 import chat
    from app.schemas.chat import ChatPromptParam

    provider = AsyncMock(
        return_value=Response(
            json.dumps({"choices": [{"message": {"content": MARKER}}]}),
            media_type="application/json",
        )
    )
    monkeypatch.setattr(chat, "format_prompt", lambda *_: MARKER)
    monkeypatch.setattr(chat, "chat_completions", provider)
    points = AsyncMock()
    with caplog.at_level(logging.INFO):
        result = await chat.chat_prompt(
            ChatPromptParam(
                prompt_type="translate", params={"text": MARKER}, stream=False
            ),
            points_context=points,
        )
    assert result.data == MARKER
    assert provider.call_args.args[0].messages[0]["content"] == MARKER
    points.deduct_points.assert_awaited_once()
    assert MARKER not in caplog.text
