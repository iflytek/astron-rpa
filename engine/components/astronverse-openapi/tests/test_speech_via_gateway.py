"""通过本地路由（13159端口）测试 astronverse-openapi 的语音接口。

运行方式：
    RUN_GATEWAY_TESTS=1 pytest tests/test_speech_via_gateway.py -v

可选环境变量：
    GATEWAY_PORT                  本地路由端口，默认 13159
    OPENAPI_LOCAL_TTS_VOICE       TTS 发音人，默认 x5_lingyuyan_flow
"""

import os
import re
from pathlib import Path

import pytest

from astronverse.actionlib.atomic import atomicMg
from astronverse.openapi import speech_asr_zh, speech_asr_multilingual, speech_tts_ultra_human


RUN_GATEWAY_TESTS = os.getenv("RUN_GATEWAY_TESTS") == "1"
GATEWAY_PORT = os.getenv("GATEWAY_PORT", "13159")
TTS_VOICE = os.getenv("OPENAPI_LOCAL_TTS_VOICE", "x5_lingyuyan_flow")
ZH_TEXT = "你好，这是通过本地路由的联调测试。"

pytestmark = pytest.mark.skipif(
    not RUN_GATEWAY_TESTS,
    reason="gateway tests are skipped by default; set RUN_GATEWAY_TESTS=1 to run",
)


@pytest.fixture(autouse=True)
def configure_gateway_port(monkeypatch):
    monkeypatch.setattr(
        atomicMg.__class__,
        "_cfg",
        {"GATEWAY_PORT": GATEWAY_PORT, "WS": None},
    )


def _normalize(text: str) -> str:
    return re.sub(r"[\W_]+", "", text).lower()


def test_gateway_tts(tmp_path):
    """TTS 通过网关返回有效音频文件"""
    result = speech_tts_ultra_human(
        text=ZH_TEXT,
        voice=TTS_VOICE,
        speed=50,
        volume=50,
        pitch=50,
        dst_file=str(tmp_path),
        dst_file_name="gateway_tts",
        audio_format="mp3",
    )

    audio_path = Path(result["audio_file"])
    assert audio_path.exists(), "音频文件不存在"
    assert audio_path.stat().st_size > 0, "音频文件为空"


def test_gateway_tts_asr_roundtrip(tmp_path):
    """TTS 生成音频后，ASR 能识别出与原文有重叠的文字"""
    tts_result = speech_tts_ultra_human(
        text=ZH_TEXT,
        voice=TTS_VOICE,
        speed=35,
        dst_file=str(tmp_path),
        dst_file_name="gateway_roundtrip",
    )

    audio_path = Path(tts_result["audio_file"])
    assert audio_path.exists()
    assert audio_path.stat().st_size > 0

    asr_result = speech_asr_zh(
        src_file=str(audio_path),
        is_save=True,
        dst_file=str(tmp_path),
        dst_file_name="gateway_asr",
        save_format="txt",
    )

    assert asr_result["text"], "ASR 返回文本为空"

    actual = _normalize(asr_result["text"])
    expected = _normalize(ZH_TEXT)
    common = set(actual) & set(expected)
    assert len(common) >= 2, (
        f"识别文本与原文重叠字符太少；原文={ZH_TEXT!r}，识别={asr_result['text']!r}，公共字符={sorted(common)!r}"
    )

    saved = Path(asr_result["saved_file"]).read_text(encoding="utf-8").strip()
    assert saved == asr_result["text"].strip()
