from io import BytesIO
import wave

import pytest

from app.utils.speech import (
    SpeechError,
    normalize_short_iat_error_message,
    prepare_short_audio_payload,
    validate_short_audio_sample_rate,
)


def _build_wav_bytes(*, sample_rate: int, channels: int = 1, sample_width: int = 2, frames: bytes = b"\x00\x00" * 16) -> bytes:
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(frames)
    return buffer.getvalue()


def test_validate_short_audio_sample_rate_rejects_unsupported_rate():
    with pytest.raises(SpeechError, match="8000Hz or 16000Hz"):
        validate_short_audio_sample_rate(44100, "sample.wav")


def test_prepare_short_audio_payload_rejects_wav_with_unsupported_rate():
    audio_bytes = _build_wav_bytes(sample_rate=44100)

    with pytest.raises(SpeechError, match="44100Hz"):
        prepare_short_audio_payload(audio_bytes, "sample.wav")


def test_prepare_short_audio_payload_accepts_wav_with_supported_rate():
    audio_bytes = _build_wav_bytes(sample_rate=16000)

    stream_bytes, encoding, sample_rate = prepare_short_audio_payload(audio_bytes, "sample.wav")

    assert stream_bytes
    assert encoding == "raw"
    assert sample_rate == 16000


def test_normalize_short_iat_error_message_maps_licc_fail():
    message = normalize_short_iat_error_message("licc failed")

    assert "authorization failed" in message
    assert "AppID" in message
