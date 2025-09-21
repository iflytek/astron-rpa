from typing import Optional
from pydantic import BaseModel, Field


class ChatCompletionParam(BaseModel):
    model: str = Field("deepseek-v3-0324", examples=["deepseek-chat"])
    stream: bool = Field(False, examples=[True])
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, examples=[0.7])
    max_tokens: Optional[int] = Field(None, examples=[4096])
    messages: Optional[list[dict]] = Field(
        None,
        examples=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "What is the capital of France?",
            },
        ],
    )

class ChatPromptParam(BaseModel):
    model: str = Field("deepseek-v3-0324", examples=["deepseek-chat"])
    stream: bool = Field(False, examples=[True])
    prompt_type: str = Field(
        ..., 
        examples=["translate", "code_review", "document_summary", "sql_generator", "business_analysis", "email_writer"],
        description="预设prompt类型"
    )
    params: Optional[dict] = Field(
        None, 
        examples=[
            {"name": "用户管理系统"},  # translate
            {"language": "python", "code": "def hello(): print('world')"},  # code_review
            {"doc_type": "技术文档", "content": "这是一个关于API的文档..."},  # document_summary
            {"db_type": "MySQL", "table_info": "users表包含id,name,email字段", "requirement": "查询所有用户"},  # sql_generator
            {"topic": "销售增长", "data": "Q1销售100万，Q2销售120万", "perspective": "市场分析"},  # business_analysis
            {"email_type": "工作邮件", "recipient": "张总", "content": "项目进度汇报", "tone": "正式"}  # email_writer
        ],
        description="prompt模板参数"
    )
