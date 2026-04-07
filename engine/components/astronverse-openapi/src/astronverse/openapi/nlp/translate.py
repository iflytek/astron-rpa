import base64
import os
from pathlib import Path

from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY

TEXT_FILE_FILTERS = {".txt", ".md", ".json", ".xml"}
MAX_TEXT_CHARS = 5000
MAX_BASE64_BYTES = 20000
LANGUAGE_LABELS = {
    "auto": "auto",
    "cn": "中文（简体）",
    "cht": "中文（繁体）",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "ru": "俄语",
    "fr": "法语",
    "es": "西班牙语",
    "ar": "阿拉伯语",
    "pt": "葡萄牙语",
    "de": "德语",
    "id": "印尼语",
    "it": "意大利语",
    "nl": "荷兰语",
    "th": "泰语",
    "bo": "藏语",
    "tr": "土耳其语",
}


def _raise_validation(message: str) -> None:
    raise BizException(IMAGE_EMPTY, message)


def _encoded_size(text: str) -> int:
    return len(base64.b64encode(text.encode("utf-8")))


def _validate_text_content(text: str) -> None:
    if not text:
        _raise_validation("文本内容是必填的")
    if len(text) > MAX_TEXT_CHARS or _encoded_size(text) > MAX_BASE64_BYTES:
        _raise_validation("文本内容超出最大限制5000字符")


def _read_text_file(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext not in TEXT_FILE_FILTERS:
        _raise_validation("文件路径是必填的")
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


def _build_output_name(base_name: str, source_path: str, suffix: str, is_multi: bool) -> str:
    if is_multi and source_path:
        return f"{base_name}_{Path(source_path).stem}{suffix}"
    return base_name


def _extract_translated_text(response: dict) -> str:
    decoded_result = response.get("decoded_result") or {}
    if isinstance(decoded_result, dict):
        translated = ((decoded_result.get("trans_result") or {}).get("dst")) or ""
        if translated:
            return translated

    data = response.get("data") or {}
    if isinstance(data, dict):
        translated = (((data.get("result") or {}).get("trans_result") or {}).get("dst")) or ""
        if translated:
            return translated

    return ""


def _validate_languages(from_lang: str, to_lang: str) -> None:
    if not from_lang:
        _raise_validation("源语种是必选的")
    if not to_lang:
        _raise_validation("目标语种是必选的")
    if from_lang == to_lang:
        _raise_validation("二者不可一致，请重新选择")


def _process_one_text(
    source_path: str,
    source_text: str,
    from_lang: str,
    to_lang: str,
    is_save: bool,
    dst_file: str,
    dst_file_name: str,
    is_multi: bool,
) -> dict:
    response = GatewayClient.post(
        "/nlp/translate",
        {"text": source_text, "from": from_lang, "to": to_lang},
    )

    saved_file = ""
    if is_save:
        if not dst_file:
            _raise_validation("文档输出路径是必填的")
        translated_text = _extract_translated_text(response)
        saved_file = utils.write_text_file(
            dst_file,
            _build_output_name(dst_file_name, source_path, ".txt", is_multi),
            translated_text,
            ".txt",
        )

    return {
        "source_file": source_path,
        "data": response,
        "saved_file": saved_file,
    }


def nlp_translate(
    input_type: str = "text",
    is_multi: bool = False,
    text: str = "",
    src_file: PATH = "",
    src_dir: PATH = "",
    from_lang: str = "auto",
    to_lang: str = "en",
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "text_translation",
) -> dict:
    _validate_languages(from_lang, to_lang)
    text_sources = _resolve_text_sources(input_type, is_multi, text, src_file, src_dir)

    items = [
        _process_one_text(
            source_path=source_path,
            source_text=source_text,
            from_lang=from_lang,
            to_lang=to_lang,
            is_save=is_save,
            dst_file=dst_file,
            dst_file_name=dst_file_name,
            is_multi=is_multi,
        )
        for source_path, source_text in text_sources
    ]

    if is_multi:
        return {
            "data": [item["data"] for item in items],
            "saved_file": [item["saved_file"] for item in items if item["saved_file"]],
        }

    item = items[0]
    return {
        "data": item["data"],
        "saved_file": item["saved_file"],
    }
