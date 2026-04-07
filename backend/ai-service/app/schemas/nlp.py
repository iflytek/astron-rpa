import json
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class TextCorrectionRequestBody(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="待纠错文本，最大 2000 个字符")
    uid: Optional[str] = Field(None, description="可选用户标识，使用黑白名单功能时必传")
    res_id: Optional[str] = Field(None, description="可选资源标识，使用黑白名单功能时必传")


class TextCorrectionResponseHeader(BaseModel):
    code: int = Field(..., description="返回码，0 表示会话成功")
    message: str = Field(..., description="返回信息")
    sid: str = Field(..., description="会话唯一标识")


class TextCorrectionResponseResult(BaseModel):
    compress: str = Field(..., description="文本压缩格式")
    encoding: str = Field(..., description="文本编码格式")
    format: str = Field(..., description="文本格式")
    text: str = Field(..., description="base64 编码的纠错结果")


class TextCorrectionResponsePayload(BaseModel):
    result: TextCorrectionResponseResult


class TextCorrectionDecodedResult(BaseModel):
    ret: Optional[int] = None
    desc: Optional[str] = None
    message: Optional[str] = None
    black_list: list[tuple[int, str, str, str]] = Field(default_factory=list)
    punc: list[tuple[int, str, str, str]] = Field(default_factory=list)
    leader: list[tuple[int, str, str, str]] = Field(default_factory=list)
    org: list[tuple[int, str, str, str]] = Field(default_factory=list)
    pol: list[tuple[int, str, str, str]] = Field(default_factory=list)
    grammar_pc: list[tuple[int, str, str, str]] = Field(default_factory=list)
    order: list[tuple[int, str, str, str]] = Field(default_factory=list)
    idm: list[tuple[int, str, str, str]] = Field(default_factory=list)
    word: list[tuple[int, str, str, str]] = Field(default_factory=list)
    char: list[tuple[int, str, str, str]] = Field(default_factory=list)
    redund: list[tuple[int, str, str, str]] = Field(default_factory=list)
    miss: list[tuple[int, str, str, str]] = Field(default_factory=list)
    dapei: list[tuple[int, str, str, str]] = Field(default_factory=list)
    number: list[tuple[int, str, str, str]] = Field(default_factory=list)
    addr: list[tuple[int, str, str, str]] = Field(default_factory=list)
    name: list[tuple[int, str, str, str]] = Field(default_factory=list)


class TextCorrectionUpstreamResponseBody(BaseModel):
    header: TextCorrectionResponseHeader
    payload: Optional[TextCorrectionResponsePayload] = None
    result: Optional[TextCorrectionDecodedResult] = Field(
        None, description="对 payload.result.text 做 base64 解码后的 JSON"
    )

    @field_validator("result", mode="before")
    @classmethod
    def _normalize_decoded_result(cls, value: Any):
        if value is None or isinstance(value, dict) or isinstance(value, TextCorrectionDecodedResult):
            return value
        if isinstance(value, str):
            return json.loads(value)
        raise TypeError("decoded_result must be a JSON object")


class TextCorrectionResponseBody(BaseModel):
    header: TextCorrectionResponseHeader
    result: Optional[TextCorrectionDecodedResult] = Field(
        None, description="对上游结果解码后的文本纠错详情"
    )

    @field_validator("result", mode="before")
    @classmethod
    def _normalize_public_result(cls, value: Any):
        if value is None or isinstance(value, dict) or isinstance(value, TextCorrectionDecodedResult):
            return value
        if isinstance(value, str):
            return json.loads(value)
        raise TypeError("result must be a JSON object")


class TextModerationRequestBody(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="待审核文本")
    is_match_all: int = Field(0, description="是否全匹配，1 为是，0 为否")
    categories: list[str] = Field(default_factory=list, description="指定检测的敏感分类")
    lib_ids: list[str] = Field(default_factory=list, description="指定自定义词库 id 列表")


class TextModerationWordInfo(BaseModel):
    word: str
    positions: list[int] = Field(default_factory=list)


class TextModerationCategory(BaseModel):
    confidence: int
    category: str
    suggest: str
    category_description: str
    word_list: list[str] = Field(default_factory=list)
    word_infos: list[TextModerationWordInfo] = Field(default_factory=list)


class TextModerationDetail(BaseModel):
    content: str
    category_list: list[TextModerationCategory] = Field(default_factory=list)


class TextModerationResult(BaseModel):
    suggest: str
    detail: TextModerationDetail


class TextModerationData(BaseModel):
    result: TextModerationResult
    request_id: str


class TextModerationResponseBody(BaseModel):
    code: str
    desc: str
    data: Optional[TextModerationData] = None
    sid: str


class TranslationRequestBody(BaseModel):
    text: str = Field(..., min_length=1, description="待翻译文本")
    from_lang: str = Field(..., alias="from", description="源语种")
    to: str = Field(..., description="目标语种")

    model_config = {"populate_by_name": True}


class TranslationDecodedResultData(BaseModel):
    src: str
    dst: str


class TranslationDecodedResult(BaseModel):
    from_lang: str = Field(..., alias="from")
    to: str
    trans_result: TranslationDecodedResultData

    model_config = {"populate_by_name": True}


class TranslationResponseData(BaseModel):
    result: TranslationDecodedResult


class TranslationResponseBody(BaseModel):
    code: int
    message: str
    sid: str
    data: Optional[TranslationResponseData] = None
