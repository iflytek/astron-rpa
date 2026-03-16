"""LLM API client helpers: streaming and normal chat plus prompt interface."""

import json
from typing import Any

import requests
import sseclient
from astronverse.actionlib.atomic import atomicMg
from astronverse.ai.error import BizException, LLM_NO_RESPONSE_ERROR_FORMAT, ERROR_FORMAT, UNKNOWN_RESPONSE_ERROR
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

    - example
        inputs = [
            {"role": "assistant", "content": "请模仿李白的口吻"},
            {"role": "user", "content": "写一首咏鹅诗"}
        ]

        outputs = {"content":"笔","reasoning_content":null}

    """
    chat_json = {"messages": messages, "model": model, "stream": True}

    response = requests.post(API_URL, json=chat_json)
    if response.status_code == 200:
        client = sseclient.SSEClient(response)  # type: ignore
        for event in client.events():
            if event.data and event.data != "[DONE]":
                response_json = json.loads(event.data)
                if response_json.get("choices"):
                    yield response_json["choices"][0]["delta"]["content"]
    else:
        raise BizException(LLM_NO_RESPONSE_ERROR_FORMAT.format(response), "error: {}".format(response))


def chat_normal(user_input, system_input="", model=DEFAULT_MODEL):
    """构建请求的 payload"""
    data = {
        "model": model,  # 选择大模型，替换为实际模型标识
        "messages": [
            {"role": "system", "content": system_input},
            {"role": "user", "content": user_input},
        ],
        "stream": False,
    }

    try:
        # 发送 API 请求
        response = requests.post(API_URL, json=data)
        response.raise_for_status()  # 检查请求是否成功

        # 返回模型生成的回复
        response_json = response.json()

        # 兼容两种响应格式
        if "data" in response_json and "choices" in response_json["data"]:
            # 新格式
            return response_json["data"]["choices"][0]["message"]["content"]
        elif "choices" in response_json:
            # 原格式
            return response_json["choices"][0]["message"]["content"]
        else:
            raise BizException(UNKNOWN_RESPONSE_ERROR, "未知的响应格式")
    except Exception as e:
        logger.error("响应格式不正确 {}".format(e))
        return None


def chat_prompt(prompt_type, params, model=DEFAULT_MODEL):
    """chat_prompt"""
    data = {
        "model": model,  # 选择大模型，替换为实际模型标识
        "prompt_type": prompt_type,
        "params": params,
    }

    try:
        # 发送 API 请求
        response = requests.post(PROMPT_URL, json=data)
        response.raise_for_status()  # 检查请求是否成功

        # 返回模型生成的回复
        response_json = response.json()
        return response_json["data"]
    except Exception as e:
        logger.error("响应格式不正确 {}".format(e))
        return None
