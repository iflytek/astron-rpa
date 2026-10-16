"""locale — 将紧凑嵌套格式的翻译字典叠加到 meta/types 数据上。

locale/zh_CN.json 格式约定
──────────────────────────
action 区段:
    "GroupKey.method": {
        "title": "...",
        "comment": "...",
        "inputList":  { "field_key": {"title": "...", "tip": "..."}, ... },
        "outputList": { "field_key": {"title": "...", "tip": "..."}, ... }
    }

options 区段（全局复用枚举标签）:
    "options": {
        "TypeName": { "value1": "label1", ... }
    }
"""

import copy
import json
import pathlib


def load_locale(lang: str, locale_dir: str | pathlib.Path = "locale") -> dict:
    """从 {locale_dir}/{lang}.json 加载翻译字典，文件不存在时返回空字典。"""
    path = pathlib.Path(locale_dir) / f"{lang}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def apply_locale(meta: dict, locale: dict) -> dict:
    """将 locale 翻译叠加到 meta 字典上，返回新字典（不修改原对象）。

    Args:
        meta:   由 atomicMg.json() 生成的基础元数据字典（无翻译或默认语言）。
        locale: 紧凑嵌套格式的翻译字典，从 locale/{lang}.json 加载。

    Returns:
        深拷贝后叠加翻译的新字典。
    """
    result = copy.deepcopy(meta)
    options_loc: dict = locale.get("options", {})

    for action_key, action in result.items():
        loc: dict = locale.get(action_key, {})

        # 叠加 action 级别文本
        if "title" in loc:
            action["title"] = loc["title"]
        if "comment" in loc:
            action["comment"] = loc["comment"]

        # 叠加 inputList + outputList 字段文本
        # locale 格式: loc["inputList"] / loc["outputList"] 为 {field_key: {title, tip, subTitle}}
        for list_key in ("inputList", "outputList"):
            list_loc: dict = loc.get(list_key, {})
            for field in action.get(list_key) or []:
                fl: dict = list_loc.get(field["key"], {})
                if "title" in fl:
                    field["title"] = fl["title"]
                if "tip" in fl:
                    field["tip"] = fl["tip"]
                if "subTitle" in fl:
                    field["subTitle"] = fl["subTitle"]

                # 按 types 类型名全局复用 options label
                type_opts: dict = options_loc.get(field.get("types") or "", {})
                for opt in field.get("options") or []:
                    if opt["value"] in type_opts:
                        opt["label"] = type_opts[opt["value"]]

    return result


def apply_types_locale(types_data: dict, locale: dict) -> dict:
    """将 locale 中的类型翻译叠加到 typesMg.json() 生成的字典上。

    locale 中类型相关格式（与 action 区段平级）：
    {
      "TypeName": {
        "desc": "...",
        "TypeName.method": { "funcDesc": "..." }
      }
    }
    """
    result = copy.deepcopy(types_data)
    for type_key, type_entry in result.items():
        loc: dict = locale.get(type_key, {})
        if not loc:
            continue
        if "desc" in loc:
            type_entry["desc"] = loc["desc"]
        if "template" in loc:
            type_entry["template"] = loc["template"]
        for func in type_entry.get("funcList") or []:
            func_key = func.get("key", "")
            func_loc: dict = loc.get(func_key, {})
            if "funcDesc" in func_loc:
                func["funcDesc"] = func_loc["funcDesc"]
            if "resDesc" in func_loc:
                func["resDesc"] = func_loc["resDesc"]
    return result
