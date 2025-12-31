from typing import List, Any, Optional, Union, Literal

from pydantic import BaseModel


# 元素基本信息
class ElementInfo(BaseModel):
    name: Optional[str] = None
    imageUrl: Optional[str] = None
    xpath: Optional[str] = None
    outerHtml: Optional[str] = None
    elementId: Optional[str] = None

# 会话内容结构
class ChatContent(BaseModel):
    smartCode: Optional[str] = None
    text: Optional[str] = None
    status: Optional[str] = None  # 'generating', 'completed', 'error' 等
    elements: Optional[List[ElementInfo]] = None
    tip: Optional[str] = None
    # 可以添加更多字段
    metadata: Optional[dict] = None

# 历史会话记录 - 新格式
class ChatHistoryItem(BaseModel):
    role: Optional[str] = None
    content: Optional[ChatContent] = None

# 异常修复信息
class FixInfo(BaseModel):
    traceback: Optional[str] = None
    consoleLog: Optional[str] = None

# 会话请求参数
class ChatRequest(BaseModel):
    sceneCode: Optional[str] = None
    user: Optional[str] = None
    needFix: Optional[bool] = None
    fixInfo: Optional[FixInfo] = None
    currentCode: Optional[str] = None
    elements: Optional[List[ElementInfo]] = None
    chatHistory: Optional[List[ChatHistoryItem]] = None

class ChatResponse(BaseModel):
    data: Optional[Any] = None
    code: Optional[int] = None
    success: Optional[bool] = None
