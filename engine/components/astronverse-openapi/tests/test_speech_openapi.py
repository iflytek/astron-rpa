import base64
from pathlib import Path
from unittest.mock import patch

from astronverse.openapi import speech_asr_zh, speech_tts_ultra_human


def test_speech_asr_zh_saves_text_result(tmp_path):
    source = tmp_path / "sample.wav"
    source.write_bytes(b"RIFF")

    response_payload = {
        "text": "你好世界",
        "result": {"segments": [{"text": "你好世界"}]},
    }

    with patch("astronverse.openapi.speech._common.GatewayClient.post", return_value=response_payload):
        result = speech_asr_zh(
            src_file=str(source),
            is_save=True,
            dst_file=str(tmp_path),
            dst_file_name="speech_result",
            save_format="txt",
        )

    assert result["text"] == "你好世界"
    assert Path(result["saved_file"]).read_text(encoding="utf-8") == "你好世界"


def test_speech_tts_writes_audio_file(tmp_path):
    audio_bytes = b"fake-audio"
    response_payload = {
        "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
        "result": {"format": "mp3"},
    }

    with patch("astronverse.openapi.speech._common.GatewayClient.post", return_value=response_payload):
        result = speech_tts_ultra_human(
            text="你好",
            dst_file=str(tmp_path),
            dst_file_name="tts_demo",
        )

    assert Path(result["audio_file"]).read_bytes() == audio_bytes
    assert result["result"]["format"] == "mp3"
