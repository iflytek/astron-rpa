import base64
import os

from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY


def ocr_general(
    is_multi: bool = False,
    src_file: PATH = "",
    src_dir: PATH = "",
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "general_ocr",
) -> list:
    if is_multi:
        files = utils.generate_src_files(src_dir)
        if not files:
            raise BizException(IMAGE_EMPTY, "图像文件夹不存在或为空")
    else:
        files = utils.generate_src_files(src_file)
        if not files:
            raise BizException(IMAGE_EMPTY, "图像路径不存在或格式错误")

    results = []
    for fp in files:
        with open(fp, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(fp)[1].lstrip(".").lower() or "jpg"
        resp = GatewayClient.post("/ocr/general", {"image": image_b64, "encoding": ext, "status": 3})
        results.append(resp)

    if is_save and results:
        utils.write_to_excel(dst_file, dst_file_name, {}, results)

    return results
