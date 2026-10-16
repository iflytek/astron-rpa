import copy

# -------------------------------------------------------------------
# 公共高级参数骨架：只含结构和静态属性，不含任何可译文本
# 可译文本（title、options.label）统一通过 TRANSLATIONS 按 locale 查表注入
# -------------------------------------------------------------------
COMMON_ADVANCED_PARAMETERS: list[dict[str, any]] = [
    {
        "types": "Bool",
        "formType": {"type": "RADIO", "params": {}},
        "key": "__res_print__",
        "name": "__res_print__",
        "options": [
            {"value": True},
            {"value": False},
        ],
        "default": False,
    },
    {
        "types": "Float",
        "formType": {"type": "INPUT_VARIABLE_PYTHON", "params": {}},
        "key": "__delay_before__",
        "name": "__delay_before__",
        "default": 0,
    },
    {
        "types": "Float",
        "formType": {"type": "INPUT_VARIABLE_PYTHON"},
        "key": "__delay_after__",
        "name": "__delay_after__",
        "default": 0,
    },
    {
        "types": "Str",
        "formType": {"type": "RADIO", "params": {}},
        "key": "__skip_err__",
        "name": "__skip_err__",
        "options": [
            {"value": "exit"},
            {"value": "skip"},
            {"value": "retry"},
        ],
        "default": "exit",
    },
    {
        "types": "Int",
        "formType": {"type": "INPUT_VARIABLE_PYTHON"},
        "key": "__retry_time__",
        "name": "__retry_time__",
        "dynamics": [
            {
                "key": "$this.__retry_time__.show",
                "expression": "return  $this.__skip_err__.value == 'retry'",
            }
        ],
        "default": 0,
    },
    {
        "types": "Float",
        "formType": {"type": "INPUT_VARIABLE_PYTHON"},
        "key": "__retry_interval__",
        "name": "__retry_interval__",
        "dynamics": [
            {
                "key": "$this.__retry_interval__.show",
                "expression": "return  $this.__skip_err__.value == 'retry'",
            }
        ],
        "default": 0,
    },
]

# -------------------------------------------------------------------
# 翻译表：{locale: {param_key: {"title": ..., "options": {value: label}}}}
# options 中以选项的 value 为 key 映射到该语言的 label
# -------------------------------------------------------------------
TRANSLATIONS: dict[str, dict[str, any]] = {
    "zh_CN": {
        "__res_print__": {
            "title": "打印输出变量值",
            "options": {True: "是", False: "否"},
        },
        "__delay_before__": {"title": "执行前延迟(秒)"},
        "__delay_after__": {"title": "执行后延迟(秒)"},
        "__skip_err__": {
            "title": "执行异常时",
            "options": {"exit": "退出", "skip": "跳过", "retry": "重试"},
        },
        "__retry_time__": {"title": "重试次数(次)"},
        "__retry_interval__": {"title": "重试间隔(秒)"},
    },
    "en_US": {
        "__res_print__": {
            "title": "Print Output Variable",
            "options": {True: "Yes", False: "No"},
        },
        "__delay_before__": {"title": "Pre-execution Delay (s)"},
        "__delay_after__": {"title": "Post-execution Delay (s)"},
        "__skip_err__": {
            "title": "On Error",
            "options": {"exit": "Exit", "skip": "Skip", "retry": "Retry"},
        },
        "__retry_time__": {"title": "Retry Count"},
        "__retry_interval__": {"title": "Retry Interval (s)"},
    },
}


def get_common_advanced_parameters(locale: str = "zh_CN") -> list[dict[str, any]]:
    """
    返回注入指定语言翻译的公共高级参数列表

    Args:
        locale: 语言代码，如 "zh_CN"（默认）或 "en_US"

    Returns:
        已翻译的参数列表（深拷贝，不修改原始数据）
    """
    t = TRANSLATIONS.get(locale, TRANSLATIONS.get("zh_CN", {}))
    result = []
    for param in COMMON_ADVANCED_PARAMETERS:
        item = copy.deepcopy(param)
        key = item["key"]
        trans = t.get(key, {})
        if "title" in trans:
            item["title"] = trans["title"]
        if "options" in trans and "options" in item:
            opt_labels = trans["options"]
            for opt in item["options"]:
                v = opt["value"]
                if v in opt_labels:
                    opt["label"] = opt_labels[v]
        result.append(item)
    return result
