import base64

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.speech._common import _post_speech


@atomicMg.atomic(
    "OpenApi",
    inputList=[
        atomicMg.param("text"),
        atomicMg.param("voice"),
        atomicMg.param(
            "dst_file",
            formType=AtomicFormTypeMeta(
                type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                params={"file_type": "folder"},
            ),
        ),
    ],
    outputList=[
        atomicMg.param("audio_file", types="PATH"),
        atomicMg.param("result", types="Dict"),
    ],
)
def speech_tts_ultra_human(
    text: str = "",
    voice: str = "x5_lingyuyan_flow",
    speed: int = 50,
    volume: int = 50,
    pitch: int = 50,
    dst_file: PATH = "",
    dst_file_name: str = "speech_tts_ultra_human",
    audio_format: str = "mp3",
) -> dict:
    response = _post_speech(
        "/speech/tts",
        {
            "text": text,
            "voice": voice,
            "speed": speed,
            "volume": volume,
            "pitch": pitch,
            "audio_format": audio_format,
            "sample_rate": 16000,
        },
    )
    audio_file = utils.write_binary_file(
        dst_file,
        dst_file_name,
        base64.b64decode(response["audio_base64"]),
        f".{audio_format}",
    )
    return {"audio_file": audio_file, "result": response["result"]}
