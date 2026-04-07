import os
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY


def _read_image_bytes(src_file: str) -> tuple[str, bytes]:
    files = utils.generate_src_files(src_file)
    if not files:
        raise BizException(IMAGE_EMPTY, "图像路径不存在或格式错误")
    path = files[0]
    with open(path, "rb") as f:
        return os.path.basename(path), f.read()


def _collect_dir_files(src_dir: str) -> list[str]:
    files = utils.generate_src_files(src_dir)
    if not files:
        raise BizException(IMAGE_EMPTY, "图像文件夹不存在或为空")
    return files


def _run_multipart_ocr(
    api_path: str,
    is_multi: bool,
    src_file,
    src_dir,
    is_save: bool,
    dst_file,
    dst_file_name: str,
    extra_fields: dict | None = None,
) -> list:
    if is_multi:
        raw_paths = _collect_dir_files(src_dir)
        file_pairs = []
        for fp in raw_paths:
            with open(fp, "rb") as f:
                file_pairs.append((os.path.basename(fp), f.read()))
    else:
        fname, fbytes = _read_image_bytes(src_file)
        file_pairs = [(fname, fbytes)]

    results = []
    for fname, fbytes in file_pairs:
        resp = GatewayClient.post_multipart(api_path, fbytes, fname, extra_fields)
        results.append(resp)

    if is_save and results:
        utils.write_to_excel(dst_file, dst_file_name, {}, results)

    return results
