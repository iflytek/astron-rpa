"""LLM API client helpers: streaming and normal chat plus prompt interface."""

import json
from typing import Any

import requests
import sseclient
from astronverse.actionlib.atomic import atomicMg
from astronverse.ai.error import BizException, LLM_NO_RESPONSE_ERROR_FORMAT, UNKNOWN_RESPONSE_ERROR
from astronverse.baseline.logger.logger import logger

API_URL = "http://127.0.0.1:{}/api/rpa-ai-service/v1/chat/completions".format(
    atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
)
PROMPT_URL = "http://127.0.0.1:{}/api/rpa-ai-service/v1/chat/prompt".format(
    atomicMg.cfg().get("GATEWAY_PORT") if atomicMg.cfg().get("GATEWAY_PORT") else "13159"
)
DEFAULT_MODEL = "xopdeepseekv32"


def chat_streamable(messages: Any, model: str = DEFAULT_MODEL):
    """
    调用远端大模型

    :param
    messages: 历史问题
    model: 模型id
    """
    chat_json = {"messages": messages, "model": model, "stream": True}

    response = requests.post(API_URL, json=chat_json)
    if response.status_code == 200:
        client = sseclient.SSEClient(response)  # type: ignore
        for event in client.events():
            if event.data and event.data != "[DONE]":
                response_json = json.loads(event.data)
                if response_json.get("choices"):
                    choice = response_json["choices"][0] or {}
                    delta = choice.get("delta") or {}
                    content = delta.get("content")
                    if content is not None:
                        yield content
    else:
        raise BizException(LLM_NO_RESPONSE_ERROR_FORMAT.format(response), "error: {}".format(response))


def chat_normal(user_input, system_input="", model=DEFAULT_MODEL):
    """构建请求的 payload"""
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input},
        ],
        "stream": False,
    }

    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        response_json = response.json()

        if "data" in response_json and "choices" in response_json["data"]:
            return response_json["data"]["choices"][0]["message"]["content"]
        if "choices" in response_json:
            return response_json["choices"][0]["message"]["content"]
        raise BizException(UNKNOWN_RESPONSE_ERROR, "未知的响应格式")
    except Exception as e:
        logger.error("响应格式不正确 {}".format(e))
        return None


def chat_prompt(prompt_type, params, model=DEFAULT_MODEL):
    """chat_prompt"""
    data = {
        "model": model,
        "prompt_type": prompt_type,
        "params": params,
    }

    try:
        response = requests.post(PROMPT_URL, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json["data"]
    except Exception as e:
        logger.error("响应格式不正确 {}".format(e))
        return None
