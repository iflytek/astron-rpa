from typing import Any

from pydantic import BaseModel, Field


class SpeechASRRequestBody(BaseModel):
    """短音频识别请求，适用于 60 秒以内的日常说话音频。"""

    audio_base64: str
    filename: str
    language: str = "cn"


class SpeechTranscriptionRequestBody(BaseModel):
    """长录音文件转写请求，适用于会议录音等长时间音频。"""

    audio_base64: str
    filename: str
    language: str = "cn"
    result_type: str = "transfer"


class SpeechTTSRequestBody(BaseModel):
    text: str = Field(min_length=1)
    voice: str = "x5_lingyuyan_flow"
    speed: int = 50
    volume: int = 50
    pitch: int = 50
    audio_format: str = "mp3"
    sample_rate: int = 16000


class SpeechASRResponseBody(BaseModel):
    text: str
    result: dict[str, Any]
    duration_seconds: float
    points_cost: int


class SpeechTTSResponseBody(BaseModel):
    audio_base64: str
    result: dict[str, Any]
    points_cost: int
