from astronverse.actionlib.types import PATH
from astronverse.openapi.ocr._common import _run_multipart_ocr


def ocr_id_card(
    is_multi: bool = False,
    src_file: PATH = "",
    src_dir: PATH = "",
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "id_card_ocr",
) -> list:
    return _run_multipart_ocr(
        "/ocr/id-card",
        is_multi, src_file, src_dir,
        is_save, dst_file, dst_file_name,
    )
