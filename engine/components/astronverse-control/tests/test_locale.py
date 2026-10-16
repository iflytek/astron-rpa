"""locale 文案完整性测试。

meta.json 只带结构，展示文案全部来自 locale/{lang}.json。缺项时前端会渲染出
空标题或裸英文 key，是最常见的回归形态，因此按语言逐项校验覆盖度。
"""

import pytest
from astronverse.actionlib.locale import apply_locale
from astronverse.control import ConditionType

LANGS = ("zh_CN", "en_US")


@pytest.mark.parametrize("lang", LANGS)
def test_locale_covers_every_atomic(locales, base_meta, lang):
    """locale 的 action 区段必须覆盖全部原子能力，且不含已删除的多余 key。"""
    keys = set(locales[lang]) - {"options"}
    assert keys == set(base_meta)


@pytest.mark.parametrize("lang", LANGS)
def test_every_atomic_has_title_and_comment(locales, base_meta, lang):
    """title 用于树和节点展示，comment 用于节点语义说明，缺一都会露出空白。"""
    missing = [
        key
        for key in base_meta
        if not locales[lang].get(key, {}).get("title") or not locales[lang].get(key, {}).get("comment")
    ]
    assert missing == []


@pytest.mark.parametrize("lang", LANGS)
def test_every_param_has_title(locales, base_meta, lang):
    """输入输出参数的 title 缺失会让表单出现无标签字段。"""
    missing = []
    for key, atomic in base_meta.items():
        loc = locales[lang].get(key, {})
        for list_key in ("inputList", "outputList"):
            declared = {p["key"] for p in atomic[list_key]}
            translated = {k for k, v in loc.get(list_key, {}).items() if v.get("title")}
            missing.extend((key, list_key, name) for name in sorted(declared - translated))
    assert missing == []


@pytest.mark.parametrize("lang", LANGS)
def test_locale_has_no_orphan_param_entries(locales, base_meta, lang):
    """locale 里残留已删除参数的翻译，说明改签名时漏改文案。"""
    orphans = []
    for key, atomic in base_meta.items():
        loc = locales[lang].get(key, {})
        for list_key in ("inputList", "outputList"):
            declared = {p["key"] for p in atomic[list_key]}
            orphans.extend((key, list_key, name) for name in sorted(set(loc.get(list_key, {})) - declared))
    assert orphans == []


@pytest.mark.parametrize("lang", LANGS)
def test_condition_type_options_fully_translated(locales, lang):
    """条件下拉的每个 value 都要有 label，缺失时前端会退化成显示运算符字面量。"""
    option_labels = locales[lang].get("options", {}).get("ConditionType", {})
    missing = [member.value for member in ConditionType if not option_labels.get(member.value)]
    assert missing == []


@pytest.mark.parametrize("lang", LANGS)
def test_apply_locale_translates_condition_options(base_meta, locales, lang):
    """apply_locale 需要把 options label 按 types 名替换掉，value 保持不变。"""
    translated = apply_locale(base_meta, locales[lang])
    condition = next(p for p in translated["Code.If"]["inputList"] if p["key"] == "condition")
    expected = locales[lang]["options"]["ConditionType"]
    assert [opt["value"] for opt in condition["options"]] == [member.value for member in ConditionType]
    assert {opt["value"]: opt["label"] for opt in condition["options"]} == expected


def test_languages_are_not_cross_contaminated(locales):
    """两种语言的 title 应当不同，全等通常意味着漏翻或复制粘贴。"""
    identical = [
        key
        for key in locales["zh_CN"]
        if key != "options" and locales["zh_CN"][key].get("title") == locales["en_US"].get(key, {}).get("title")
    ]
    assert identical == []
