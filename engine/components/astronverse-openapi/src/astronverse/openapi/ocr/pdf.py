import os

from astronverse.actionlib.types import PATH
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY


def ocr_pdf(
    src_file: PATH = "",
    pdf_url: str = "",
    export_format: str = "json",
    dst_file: PATH = "",
    dst_file_name: str = "pdf_ocr",
) -> dict:
    if pdf_url:
        resp = GatewayClient.post(
            "/ocr/pdf",
            {"pdf_url": pdf_url, "export_format": export_format},
        )
    elif src_file:
        with open(src_file, "rb") as f:
            file_bytes = f.read()
        resp = GatewayClient.post_multipart(
            "/ocr/pdf",
            file_bytes,
            os.path.basename(src_file),
            extra_fields={"export_format": export_format},
        )
    else:
        raise BizException(IMAGE_EMPTY, "src_file 和 pdf_url 不能同时为空")

    payload = resp.get("payload", {})
    return {
        "task_no": payload.get("task_no", ""),
        "status": payload.get("status", ""),
        "page_count": payload.get("page_count", 0),
        "result_url": payload.get("result_url", ""),
    }
