import os
from pathlib import Path

from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY

TEXT_FILE_FILTERS = {".txt", ".md", ".json", ".xml"}
MAX_FILE_SIZE_BYTES = 7 * 1024
MAX_TEXT_BYTES = 7000
MAX_TEXT_CHARS = 2000
ERROR_TYPE_LABELS = {
    "black_list": "敏感词",
    "punc": "标点",
    "leader": "领导人职称",
    "org": "机构名",
    "pol": "政治术语",
    "grammar_pc": "语法",
    "order": "语序",
    "idm": "成语",
    "word": "词语",
    "char": "别字",
    "redund": "冗余",
    "miss": "缺漏",
    "dapei": "搭配",
    "number": "数字",
    "addr": "地址",
    "name": "人名",
}
EXCEL_HEADERS = {
    "错误位置": "错误位置",
    "错误文本": "错误文本",
    "纠正文本": "纠正文本",
    "错误类型": "错误类型",
}


def _raise_validation(message: str) -> None:
    raise BizException(IMAGE_EMPTY, message)


def _count_cjk_chars(text: str) -> int:
    total = 0
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            total += 1
    return total


def _validate_text_content(text: str) -> None:
    if not text:
        _raise_validation("文本内容是必填的")
    if len(text) > MAX_TEXT_CHARS:
        _raise_validation("文本内容超出最大限制2000字符")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES or _count_cjk_chars(text) > MAX_TEXT_CHARS:
        _raise_validation("文本内容超出最大限制2000字符")


def _read_text_file(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext not in TEXT_FILE_FILTERS:
        _raise_validation("文件路径不支持该文件格式")
    if os.path.getsize(path) > MAX_FILE_SIZE_BYTES:
        _raise_validation("文本内容超出最大限制2000字符")
    content = Path(path).read_text(encoding="utf-8")
    _validate_text_content(content)
    return content


def _resolve_text_sources(input_type: str, is_multi: bool, text: str, src_file: str, src_dir: str) -> list[tuple[str, str]]:
    if input_type == "text":
        _validate_text_content(text)
        return [("", text)]

    if is_multi:
        if not src_dir:
            _raise_validation("文件路径是必填的")
        files = utils.generate_src_files(src_dir, file_type="file")
        files = [fp for fp in files if Path(fp).suffix.lower() in TEXT_FILE_FILTERS]
        if not files:
            _raise_validation("文件路径是必填的")
        return [(fp, _read_text_file(fp)) for fp in files]

    if not src_file:
        _raise_validation("文件路径是必填的")
    files = utils.generate_src_files(src_file, file_type="file")
    if not files:
        _raise_validation("文件路径是必填的")
    return [(files[0], _read_text_file(files[0]))]


def _iter_error_rows(decoded_result: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for category, label in ERROR_TYPE_LABELS.items():
        for item in _iter_correction_items(decoded_result, category):
            rows.append(
                {
                    "错误位置": str(item[0]),
                    "错误文本": item[1],
                    "纠正文本": item[2],
                    "错误类型": label,
                }
            )
    return rows


def _collect_replacements(decoded_result: dict) -> list[tuple[int, str, str]]:
    replacements: list[tuple[int, str, str]] = []
    for category in ERROR_TYPE_LABELS:
        for item in _iter_correction_items(decoded_result, category):
            position, wrong_text, corrected_text = item[0], item[1], item[2]
            if isinstance(position, int) and wrong_text:
                replacements.append((position, wrong_text, corrected_text))
    return replacements


def _apply_replacements(original_text: str, decoded_result: dict) -> str:
    corrected_text = original_text
    for position, wrong_text, corrected_text_value in sorted(
        _collect_replacements(decoded_result),
        key=lambda item: item[0],
        reverse=True,
    ):
        candidate_indexes = [position, max(position - 1, 0)]
        applied = False
        for start in candidate_indexes:
            end = start + len(wrong_text)
            if corrected_text[start:end] == wrong_text:
                corrected_text = corrected_text[:start] + corrected_text_value + corrected_text[end:]
                applied = True
                break
        if not applied:
            corrected_text = corrected_text.replace(wrong_text, corrected_text_value, 1)
    return corrected_text


def _build_output_name(base_name: str, source_path: str, suffix: str, is_multi: bool) -> str:
    if is_multi and source_path:
        return f"{base_name}_{Path(source_path).stem}{suffix}"
    return base_name


def _iter_correction_items(decoded_result: dict, category: str):
    entries = decoded_result.get(category, []) or []
    if not isinstance(entries, list):
        return []
    valid_items = []
    for item in entries:
        if not isinstance(item, (list, tuple)) or len(item) < 3:
            continue
        valid_items.append(item)
    return valid_items


def _request_result(source_text: str) -> dict:
    response = GatewayClient.post("/nlp/text-correction", {"text": source_text})
    body = response.get("data") if isinstance(response, dict) else None
    if not isinstance(body, dict):
        body = response if isinstance(response, dict) else {}
    return body.get("result") or body.get("decoded_result") or {}


def _process_one_text(
    source_path: str,
    source_text: str,
    is_save: bool,
    error_dst_file: str,
    error_dst_file_name: str,
    export_corrected_doc: bool,
    corrected_dst_file: str,
    corrected_dst_file_name: str,
    is_multi: bool,
) -> dict:
    result = _request_result(source_text)
    error_rows = _iter_error_rows(result)

    error_detail_file = ""
    if is_save and error_rows:
        error_detail_file = utils.write_to_excel(
            error_dst_file,
            _build_output_name(error_dst_file_name, source_path, ".xlsx", is_multi),
            EXCEL_HEADERS,
            error_rows,
        )
    elif is_save:
        print("无错误，无需导出文档")

    corrected_file = ""
    if export_corrected_doc:
        corrected_text = _apply_replacements(source_text, result)
        corrected_file = utils.write_text_file(
            corrected_dst_file,
            _build_output_name(corrected_dst_file_name, source_path, ".txt", is_multi),
            corrected_text,
            ".txt",
        )
    return {
        "source_file": source_path,
        "data": result,
        "error_detail_file": error_detail_file,
        "corrected_file": corrected_file,
    }


def nlp_text_correction(
    input_type: str = "text",
    is_multi: bool = False,
    src_file: PATH = "",
    src_dir: PATH = "",
    text: str = "",
    is_save: bool = True,
    error_dst_file: PATH = "",
    error_dst_file_name: str = "text_correction",
    export_corrected_doc: bool = False,
    corrected_dst_file: PATH = "",
    corrected_dst_file_name: str = "text_correction_corrected",
) -> dict:
    text_sources = _resolve_text_sources(input_type, is_multi, text, src_file, src_dir)

    if is_save and not error_dst_file:
        _raise_validation("文档输出路径是必填的")
    if export_corrected_doc and not corrected_dst_file:
        _raise_validation("纠错后完整文档输出路径是必填的")

    items = [
        _process_one_text(
            source_path=source_path,
            source_text=source_text,
            is_save=is_save,
            error_dst_file=error_dst_file,
            error_dst_file_name=error_dst_file_name,
            export_corrected_doc=export_corrected_doc,
            corrected_dst_file=corrected_dst_file,
            corrected_dst_file_name=corrected_dst_file_name,
            is_multi=is_multi,
        )
        for source_path, source_text in text_sources
    ]

    if is_multi:
        return {
            "data": [item["data"] for item in items],
            "error_detail_file": [item["error_detail_file"] for item in items if item["error_detail_file"]],
            "corrected_file": [item["corrected_file"] for item in items if item["corrected_file"]],
        }

    item = items[0]
    return {
        "data": item["data"],
        "error_detail_file": item["error_detail_file"],
        "corrected_file": item["corrected_file"],
    }
