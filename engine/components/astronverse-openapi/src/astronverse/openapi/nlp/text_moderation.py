import os
from pathlib import Path

from astronverse.actionlib.types import PATH
from astronverse.openapi import utils
from astronverse.openapi.client import GatewayClient
from astronverse.openapi.error import BizException, IMAGE_EMPTY

TEXT_FILE_FILTERS = {".txt", ".md", ".json", ".xml"}
MAX_FILE_SIZE_BYTES = 17 * 1024
MAX_TEXT_CHARS = 5000
DEFAULT_CATEGORIES = [
    "pornDetection",
    "violentTerrorism",
    "political",
    "lowQualityIrrigation",
    "contraband",
    "advertisement",
    "uncivilizedLanguage",
]
CATEGORY_LABELS = {
    "pornDetection": "色情",
    "violentTerrorism": "暴恐",
    "political": "涉政",
    "lowQualityIrrigation": "低质量灌水",
    "contraband": "违禁",
    "advertisement": "广告",
    "uncivilizedLanguage": "不文明用语",
}
EXCEL_HEADERS = {
    "置信度": "置信度",
    "敏感分类": "敏感分类",
    "内容建议结果": "内容建议结果",
    "识别类型": "识别类型",
    "敏感词列表": "敏感词列表",
    "敏感词": "敏感词",
    "敏感词位置下标信息": "敏感词位置下标信息",
}


def _raise_validation(message: str) -> None:
    raise BizException(IMAGE_EMPTY, message)


def _validate_text_content(text: str) -> None:
    if not text:
        _raise_validation("文本内容是必填的")
    if len(text) > MAX_TEXT_CHARS:
        _raise_validation("文本内容超出最大限制5000字符")


def _read_text_file(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext not in TEXT_FILE_FILTERS:
        _raise_validation("文件路径是必填的")
    if os.path.getsize(path) > MAX_FILE_SIZE_BYTES:
        _raise_validation("文本内容超出最大限制5000字符")
    content = Path(path).read_text(encoding="utf-8")
    _validate_text_content(content)
    return content


def _resolve_text_sources(input_type: str, is_multi: bool, content: str, src_file: str, src_dir: str) -> list[tuple[str, str]]:
    if input_type == "text":
        _validate_text_content(content)
        return [("", content)]

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


def _normalize_categories(categories: list | None) -> list[str]:
    valid_categories = []
    for category in categories or DEFAULT_CATEGORIES:
        if category in CATEGORY_LABELS and category not in valid_categories:
            valid_categories.append(category)
    return valid_categories or DEFAULT_CATEGORIES


def _extract_category_rows(response: dict) -> list[dict[str, str]]:
    category_list = (((response.get("data") or {}).get("result") or {}).get("detail") or {}).get("category_list") or []
    rows: list[dict[str, str]] = []
    for category in category_list:
        if not isinstance(category, dict):
            continue
        category_value = str(category.get("category") or "")
        word_infos = category.get("word_infos") or []
        if not isinstance(word_infos, list):
            word_infos = []
        if not word_infos:
            rows.append(
                {
                    "置信度": str(category.get("confidence", "")),
                    "敏感分类": CATEGORY_LABELS.get(category_value, category_value),
                    "内容建议结果": str(category.get("suggest", "")),
                    "识别类型": str(category.get("category_description", "")),
                    "敏感词列表": list(category.get("word_list") or []),
                    "敏感词": "",
                    "敏感词位置下标信息": "",
                }
            )
            continue

        for word_info in word_infos:
            if not isinstance(word_info, dict):
                continue
            positions = [str(position) for position in (word_info.get("positions") or [])]
            rows.append(
                {
                    "置信度": str(category.get("confidence", "")),
                    "敏感分类": CATEGORY_LABELS.get(category_value, category_value),
                    "内容建议结果": str(category.get("suggest", "")),
                    "识别类型": str(category.get("category_description", "")),
                    "敏感词列表": list(category.get("word_list") or []),
                    "敏感词": str(word_info.get("word", "")),
                    "敏感词位置下标信息": positions,
                }
            )
    return rows


def _request_result(source_text: str, categories: list[str]) -> dict:
    return GatewayClient.post(
        "/nlp/text-moderation",
        {
            "content": source_text,
            "is_match_all": 1,
            "categories": categories,
        },
    )


def _process_one_text(
    source_path: str,
    source_text: str,
    categories: list[str],
    is_save: bool,
    dst_file: str,
    dst_file_name: str,
    is_multi: bool,
) -> dict:
    response = _request_result(source_text, categories)
    suggest = (((response.get("data") or {}).get("result") or {}).get("suggest") or "").lower()

    saved_file = ""
    if is_save:
        if not dst_file:
            _raise_validation("文档输出路径是必填的")
        if suggest == "block":
            rows = _extract_category_rows(response)
            saved_file = utils.write_to_excel(
                dst_file,
                _build_output_name(dst_file_name, source_path, ".xlsx", is_multi),
                EXCEL_HEADERS,
                rows,
            )
        else:
            print("审核通过，无审核建议需导出")

    return {
        "source_file": source_path,
        "data": response,
        "saved_file": saved_file,
    }


def nlp_text_moderation(
    input_type: str = "text",
    is_multi: bool = False,
    content: str = "",
    src_file: PATH = "",
    src_dir: PATH = "",
    categories: list = None,
    is_save: bool = True,
    dst_file: PATH = "",
    dst_file_name: str = "text_moderation",
) -> dict:
    text_sources = _resolve_text_sources(input_type, is_multi, content, src_file, src_dir)
    normalized_categories = _normalize_categories(categories)

    items = [
        _process_one_text(
            source_path=source_path,
            source_text=source_text,
            categories=normalized_categories,
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
