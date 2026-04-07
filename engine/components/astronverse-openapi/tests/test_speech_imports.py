def test_speech_imports_from_submodule():
    from astronverse.openapi.speech import (
        speech_asr_multilingual,
        speech_asr_zh,
        speech_transcribe_audio,
        speech_tts_ultra_human,
    )

    assert callable(speech_asr_zh)
    assert callable(speech_asr_multilingual)
    assert callable(speech_transcribe_audio)
    assert callable(speech_tts_ultra_human)


def test_speech_imports_from_top_level():
    from astronverse.openapi import (
        speech_asr_multilingual,
        speech_asr_zh,
        speech_transcribe_audio,
        speech_tts_ultra_human,
    )

    assert callable(speech_asr_zh)
    assert callable(speech_asr_multilingual)
    assert callable(speech_transcribe_audio)
    assert callable(speech_tts_ultra_human)
