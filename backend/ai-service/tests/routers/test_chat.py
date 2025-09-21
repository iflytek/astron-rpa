# Mock data
from httpx import AsyncClient
import pytest


VALID_CHAT_REQUEST = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ],
    "temperature": 0.7,
    "max_tokens": 4096,
}

HEADER = {
    "X-User-Id": "2",
}


@pytest.mark.asyncio
async def test_chat_completion_non_stream(client: AsyncClient):
    """Test the non-streaming chat completion endpoint"""
    request_data = VALID_CHAT_REQUEST.copy()
    request_data["stream"] = False

    response = await client.post(
        "/v1/chat/completions", headers=HEADER, json=request_data
    )

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert (
        response.text.find("Paris") != -1
    )  # Check if the response contains the expected answer


@pytest.mark.asyncio
async def test_chat_completion_stream(client: AsyncClient):
    """Test the streaming chat completion endpoint"""
    request_data = VALID_CHAT_REQUEST.copy()
    request_data["stream"] = True

    response = await client.post(
        "/v1/chat/completions", headers=HEADER, json=request_data
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    content = b"".join(chunk for chunk in response.iter_bytes()).decode("utf-8")
    assert content.startswith("data: ")
    assert content.endswith("\n\n")
    assert "Paris" in content  # Check if the response contains the expected answer
