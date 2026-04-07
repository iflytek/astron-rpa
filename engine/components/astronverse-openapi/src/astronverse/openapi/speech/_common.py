import base64

from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY


def _post_speech(path: str, payload: dict) -> dict:
    return GatewayClient.post(path, payload)


def _read_audio_file(src_file: str) -> tuple[str, str]:
    files = utils.generate_src_files(src_file, file_type="file")
    if len(files) == 0:
        raise BizException(IMAGE_EMPTY, "音频路径不存在或格式错误")
    file_path = files[0]
    with open(file_path, "rb") as file:
        audio_base64 = base64.b64encode(file.read()).decode("utf-8")
    return file_path, audio_base64
