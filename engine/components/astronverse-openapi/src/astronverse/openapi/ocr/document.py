import base64
import json

from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY


def ocr_document(
    src_file: PATH = "",
    output_format: str = "markdown",
    output_level: int = 1,
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "document_ocr",
) -> dict:
    files = utils.generate_src_files(src_file)
    if not files:
        raise BizException(IMAGE_EMPTY, "文件路径不存在或格式错误")

    with open(files[0], "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    resp = GatewayClient.post(
        "/ocr/document",
        {"image": image_b64, "output_format": output_format, "output_level": output_level},
    )

    raw_b64 = resp["payload"]["result"]["text"]
    raw_str = base64.b64decode(raw_b64).decode("utf-8")
    raw = json.loads(raw_str)
    text = raw.get("text", raw_str)

    saved_file = ""
    if is_save:
        saved_file = utils.write_text_file(dst_file, dst_file_name, text, suffix=".txt")

    return {"text": text, "raw": raw, "saved_file": saved_file}
