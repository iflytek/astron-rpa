from typing import Any, Optional

from pydantic import BaseModel


# 元素基本信息
class SmartElementInfo(BaseModel):
    name: Optional[str] = None
    imageUrl: Optional[str] = None
    xpath: Optional[str] = None
    outerHtml: Optional[str] = None
    elementId: Optional[str] = None


# 会话内容结构
class SmartChatContent(BaseModel):
    smartCode: Optional[str] = None
    user: Optional[str] = None
    text: Optional[str] = None
    status: Optional[str] = None  # 'generating', 'completed', 'error' 等
    elements: Optional[list[SmartElementInfo]] = None
    tip: Optional[str] = None
    # 可以添加更多字段
    metadata: Optional[dict] = None


# 历史会话记录 - 新格式
class SmartChatHistoryItem(BaseModel):
    role: Optional[str] = None
    content: Optional[SmartChatContent] = None


# 异常修复信息
class SmartFixInfo(BaseModel):
    traceback: Optional[str] = None
    consoleLog: Optional[str] = None


# 会话请求参数
class SmartChatRequest(BaseModel):
    sceneCode: Optional[str] = None
    user: Optional[str] = None
    needFix: Optional[bool] = None
    fixInfo: Optional[SmartFixInfo] = None
    currentCode: Optional[str] = None
    elements: Optional[list[SmartElementInfo]] = None
    chatHistory: Optional[list[SmartChatHistoryItem]] = None


class SmartChatResponse(BaseModel):
    data: Optional[Any] = None
    code: Optional[int] = None
    success: Optional[bool] = None
