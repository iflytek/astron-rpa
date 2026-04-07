import json
import os

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.speech._common import _post_speech, _read_audio_file


@atomicMg.atomic(
    "OpenApi",
    inputList=[
        atomicMg.param(
            "src_file",
            formType=AtomicFormTypeMeta(
                type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                params={"file_type": "file"},
            ),
        ),
        atomicMg.param("language"),
        atomicMg.param(
            "dst_file",
            formType=AtomicFormTypeMeta(
                type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                params={"file_type": "folder"},
            ),
            dynamics=[DynamicsItem(key="$this.dst_file.show", expression="return $this.is_save.value == true")],
        ),
    ],
    outputList=[
        atomicMg.param("text", types="Str"),
        atomicMg.param("result", types="Dict"),
        atomicMg.param("saved_file", types="PATH"),
    ],
)
def speech_transcribe_audio(
    src_file: PATH = "",
    language: str = "cn",
    is_save: bool = False,
    dst_file: PATH = "",
    dst_file_name: str = "speech_transcribe_audio",
    save_format: str = "txt",
) -> dict:
    file_path, audio_base64 = _read_audio_file(src_file)
    response = _post_speech(
        "/speech/transcription",
        {
            "audio_base64": audio_base64,
            "filename": os.path.basename(file_path),
            "language": language,
            "result_type": "transfer",
        },
    )
    result = {"text": response["text"], "result": response["result"], "saved_file": ""}
    if is_save:
        if save_format == "json":
            result["saved_file"] = utils.write_text_file(
                dst_file, dst_file_name, json.dumps(response["result"], ensure_ascii=False, indent=2), ".json"
            )
        else:
            result["saved_file"] = utils.write_text_file(dst_file, dst_file_name, response["text"], ".txt")
    return result
