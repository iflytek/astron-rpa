import json
from importlib import resources
from typing import List

from fastapi import APIRouter

import app.services.smart_component.prompts as prompts_package
from app.schemas.chat import ChatCompletionParam
from app.services.chat import chat_completions
from app.services.smart_component.models.chat import ChatRequest, ElementInfo, ChatResponse

router = APIRouter(
    prefix="/smart",
    tags=["智能组件服务"],
)

prompt_map = {
    "smart_web_auto": "web_auto_prompt.md",
    "smart_data_process": "data_process_prompt.md",
    "smart_optimize_input": "optimize_input_prompt.md"
}


def build_messages(request: ChatRequest) -> List[dict]:
    def format_elements(elements: List[ElementInfo]) -> str:
        if not elements:
            return ""
        template = """\n
`{name}` 的 元素ID 为 `{elementId}`
`{name}` 的 XPath 为 `{XPath}`
`{name}` 的 截图 为 `{imageUrl}`
`{name}` 的 outerHTML 为\n```\n{outerHTML}\n```"""
        formatted = []
        for element in elements:
            formatted.append(template.format(
                name=element.name,
                elementId=element.elementId,
                XPath=element.xpath,
                imageUrl=element.imageUrl,
                outerHTML=element.outerHtml
            ))
        return "".join(formatted)

    prompt = resources.read_text(prompts_package, prompt_map.get(request.sceneCode))

    messages = [
        {
            "role": "system",
            "content": prompt,
        }
    ]

    # 处理新的历史会话格式
    for history in (request.chatHistory or []):
        # 构建消息内容
        if history.content.smartCode is not None and history.content.smartCode != "":
            content_text = f"""```smart_code\n{history.content.smartCode}\n```\n{history.content.text}
            """
        else:
            content_text = history.content.text or ""
        
        # 如果有元素信息，添加到内容中
        if history.content.elements:
            content_text += format_elements(history.content.elements)
        
        messages.append({
            "role": history.role,
            "content": content_text
        })
    
    # 处理当前用户消息以及异常修复消息
    if request.needFix:
        current_content = f"请根据代码运行的错误堆栈对当前代码进行修复\n{request.fixInfo.traceback if request.fixInfo is not None else ""}\n### 当前代码\n{request.currentCode}"
    else:
        current_content = request.user or ""
    if request.elements:
        current_content += format_elements(request.elements)
    
    messages.append({
        "role": "user",
        "content": current_content
    })
    return messages


@router.post("/chat/stream")
async def smart_chat_stream(request: ChatRequest):

    llm_params = ChatCompletionParam(
        model='deepseek-v3-2-251201',
        stream=True,
        temperature=0.15,
        max_tokens=8192,
        messages=build_messages(request),
    )

    return await chat_completions(llm_params)

@router.post("/chat", response_model=ChatResponse)
async def smart_chat(request: ChatRequest):
    llm_params = ChatCompletionParam(
        model='deepseek-v3-2-251201',
        stream=False,
        temperature=0.15,
        max_tokens=8192,
        messages=build_messages(request),
    )

    chat_result = await chat_completions(llm_params)

    return ChatResponse(
        data=json.loads(chat_result.body),
        code=200,
        success=True
    )