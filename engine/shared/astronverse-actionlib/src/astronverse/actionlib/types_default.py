import copy

# -------------------------------------------------------------------
# 类型（types）骨架：只含结构和非可译字段
#   - key, src, version, channel
#   - template（仅对语言无关的字面量保留，如数字、路径、日期、URL）
#   - funcList 中只含 key、resType、useSrc（均非可译）
# 可译文本（desc、locale 相关 template、funcDesc、resDesc）
# 统一通过 TRANSLATIONS 按 locale 查表注入
# -------------------------------------------------------------------
TYPES_FRAME: dict[str, any] = {
    "Any": {
        "key": "Any",
        "src": "",
        "version": "1",
        "channel": "global",
        "funcList": [],
    },
    "Float": {
        "key": "Float",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "template": "10.1",
        "funcList": [
            {"key": "Float.toStr", "resType": "Str", "useSrc": "str(@{self:self})"},
            {"key": "Float.toInt", "resType": "Int", "useSrc": "int(@{self:self})"},
        ],
    },
    "Int": {
        "key": "Int",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "template": "10",
        "funcList": [
            {"key": "Int.toStr", "resType": "Str", "useSrc": "str(@{self:self})"},
        ],
    },
    "Bool": {
        "key": "Bool",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "funcList": [],
    },
    "Str": {
        "key": "Str",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "funcList": [
            {"key": "Str.strip", "resType": "Str", "useSrc": "@{self:self}.strip()"},
            {"key": "Str.toInt", "resType": "Int", "useSrc": "int(@{self:self})"},
            {"key": "Str.toFloat", "resType": "Float", "useSrc": "float(@{self:self})"},
        ],
    },
    "List": {
        "key": "List",
        "src": "",
        "version": "1",
        "channel": "global",
        "template": "[1,2,3]",
        "funcList": [
            {"key": "List.get", "resType": "Any", "useSrc": "@{self:self}[@(p1:int)]"},
            {"key": "List.getEnd", "resType": "Any", "useSrc": "@{self:self}[-@(p1:int)]"},
            {"key": "List.getLen", "resType": "Int", "useSrc": "len(@{self:self})"},
            {"key": "List.getSlice", "resType": "List", "useSrc": "@{self:self}[@(p1:int):@(p2:int)]"},
        ],
    },
    "Dict": {
        "key": "Dict",
        "src": "",
        "version": "1",
        "channel": "global",
        "funcList": [
            {"key": "Dict.get", "resType": "Any", "useSrc": '@{self:self}["@(p1:str)"]'},
            # 注意：此条 key 与 List.getLen 相同，与原 tree_frame.json 保持一致
            {"key": "List.getLen", "resType": "Int", "useSrc": "len(@{self:self})"},
        ],
    },
    "PATH": {
        "key": "PATH",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "template": "C://Users",
        "funcList": [
            {"key": "PATH.root", "resType": "Str", "useSrc": "@{self:self}.root()"},
            {"key": "PATH.directory", "resType": "Str", "useSrc": "@{self:self}.directory()"},
            {"key": "PATH.file_name", "resType": "Str", "useSrc": "@{self:self}.file_name()"},
            {
                "key": "PATH.file_name_without_extension",
                "resType": "Str",
                "useSrc": "@{self:self}.file_name_without_extension()",
            },
            {"key": "PATH.file_extension", "resType": "Str", "useSrc": "@{self:self}.file_extension()"},
        ],
    },
    "DIRPATH": {
        "key": "DIRPATH",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "template": "C://Users",
        "funcList": [
            {"key": "DIRPATH.root", "resType": "Str", "useSrc": "@{self:self}.root()"},
            {"key": "DIRPATH.directory", "resType": "Str", "useSrc": "@{self:self}.directory()"},
        ],
    },
    "Date": {
        "key": "Date",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "template": "2025-01-10 17:00:00",
        "funcList": [
            {"key": "Date.get_time_year", "resType": "Int", "useSrc": "@{self:self}.get_time_year()"},
            {"key": "Date.get_time_month", "resType": "Int", "useSrc": "@{self:self}.get_time_month()"},
            {"key": "Date.get_time_day", "resType": "Int", "useSrc": "@{self:self}.get_time_day()"},
            {"key": "Date.get_time_hour", "resType": "Int", "useSrc": "@{self:self}.get_time_hour()"},
            {"key": "Date.get_time_minute", "resType": "Int", "useSrc": "@{self:self}.get_time_minute()"},
            {"key": "Date.get_time_second", "resType": "Int", "useSrc": "@{self:self}.get_time_second()"},
            {"key": "Date.get_time_weekday", "resType": "Int", "useSrc": "@{self:self}.get_time_weekday()"},
            {"key": "Date.get_time_week", "resType": "Int", "useSrc": "@{self:self}.get_time_week()"},
        ],
    },
    "URL": {
        "key": "URL",
        "src": "",
        "version": "1",
        "channel": "global",
        "template": "https://www.iflytek.com/",
        "funcList": [],
    },
    "Pick": {
        "key": "Pick",
        "src": "",
        "version": "1",
        "channel": "",
        "funcList": [],
    },
    "WebPick": {
        "key": "WebPick",
        "src": "",
        "version": "1",
        "channel": "global",
        "funcList": [],
    },
    "WinPick": {
        "key": "WinPick",
        "src": "",
        "version": "1",
        "channel": "global",
        "funcList": [],
    },
    "IMGPick": {
        "key": "IMGPick",
        "src": "",
        "version": "1",
        "channel": "global",
        "funcList": [],
    },
    "Password": {
        "key": "Password",
        "src": "",
        "version": "1",
        "channel": "global,main",
        "template": "******",
        "funcList": [],
    },
    "FeishuBaseInstance": {
        "key": "FeishuBaseInstance",
        "src": "",
        "version": "1",
        "channel": "",
        "funcList": [],
    },
    "DialogResult": {
        "key": "DialogResult",
        "src": "",
        "version": "1",
        "channel": "",
        "funcList": [],
    },
    "Browser": {
        "key": "Browser",
        "src": "rpabrowser.browser.Browser()",
        "version": "1.0.1",
        "channel": "global",
        "funcList": [
            {"key": "Browser.get_url", "resType": "Str", "useSrc": "@{self:self}.get_url()"},
            {"key": "Browser.get_title", "resType": "Str", "useSrc": "@{self:self}.get_title()"},
        ],
    },
    "DocumentObject": {
        "key": "DocumentObject",
        "src": "astronverse.word.docx_obj.DocumentObject()",
        "version": "1.0.1",
        "channel": "global",
        "funcList": [],
    },
    "ExcelObj": {
        "key": "ExcelObj",
        "src": "astronverse.excel.excel_obj.ExcelObj()",
        "version": "1.0.1",
        "channel": "global",
        "funcList": [
            {"key": "ExcelObj.get_full_name", "resType": "Str", "useSrc": "@{self:self}.get_full_name()"},
            {"key": "ExcelObj.get_first_free_row", "resType": "Int", "useSrc": "@{self:self}.get_first_free_row()"},
        ],
    },
}

# -------------------------------------------------------------------
# 翻译表：{locale: translations}
#
# 每个 locale 的翻译条目形如：
#   type_key  → {"desc": ..., "template": ...}      # 类型级翻译
#   func_key  → {"funcDesc": ..., "resDesc": ...}   # 方法级翻译
#
# func_key 格式：{TypeKey}.{method_name}，与 TYPES_FRAME.funcList[].key 对应
# -------------------------------------------------------------------
TRANSLATIONS: dict[str, dict[str, any]] = {
    "zh_CN": {
        # ---- 类型描述 & locale 相关模板 ----
        "Any": {"desc": "任意值", "template": "任何值"},
        "Float": {"desc": "数值"},
        "Int": {"desc": "整数"},
        "Bool": {"desc": "布尔值", "template": "true或者false"},
        "Str": {"desc": "字符串", "template": "\u201c你好\u201d"},
        "List": {"desc": "列表"},
        "Dict": {"desc": "字典", "template": {"name": "小明"}},
        "PATH": {"desc": "文件路径"},
        "DIRPATH": {"desc": "文件夹路径"},
        "Date": {"desc": "日期时间"},
        "URL": {"desc": "地址"},
        "Pick": {"desc": "元素", "template": "JSON字符串"},
        "WebPick": {"desc": "网页元素", "template": "JSON字符串"},
        "WinPick": {"desc": "桌面元素", "template": "JSON字符串"},
        "IMGPick": {"desc": "图像元素", "template": "JSON字符串"},
        "Password": {"desc": "密码"},
        "FeishuBaseInstance": {"desc": "飞书对象", "template": "飞书对象."},
        "DialogResult": {"desc": "对话框输出结果", "template": "JSON字符串"},
        "Browser": {"desc": "浏览器对象", "template": "Browser对象"},
        "DocumentObject": {"desc": "Word对象", "template": "DocumentObject对象"},
        "ExcelObj": {"desc": "Excel对象", "template": "ExcelObj对象"},
        # ---- 方法描述 ----
        "Float.toStr": {"funcDesc": "转文本", "resDesc": "字符串"},
        "Float.toInt": {"funcDesc": "取整数部分", "resDesc": "整数"},
        "Int.toStr": {"funcDesc": "转文本", "resDesc": "字符串"},
        "Str.strip": {"funcDesc": "删除两端空格", "resDesc": "字符串"},
        "Str.toInt": {"funcDesc": "转整数", "resDesc": "整数"},
        "Str.toFloat": {"funcDesc": "转数值", "resDesc": "数值"},
        "List.get": {"funcDesc": "列表第@{p1:int}项", "resDesc": "任意值"},
        "List.getEnd": {"funcDesc": "列表倒数第@{p1:int}项", "resDesc": "任意值"},
        "List.getLen": {"funcDesc": "列表长度", "resDesc": "整数"},
        "List.getSlice": {"funcDesc": "列表第@{p1:int}项到第@{p2:int}项", "resDesc": "列表"},
        "Dict.get": {"funcDesc": "字典键@{p1:str}的值", "resDesc": "任意值"},
        "PATH.root": {"funcDesc": "根目录", "resDesc": "字符串"},
        "PATH.directory": {"funcDesc": "父目录", "resDesc": "字符串"},
        "PATH.file_name": {"funcDesc": "文件名称", "resDesc": "字符串"},
        "PATH.file_name_without_extension": {"funcDesc": "文件名称(不带扩展名)", "resDesc": "字符串"},
        "PATH.file_extension": {"funcDesc": "文件扩展名", "resDesc": "字符串"},
        "DIRPATH.root": {"funcDesc": "根目录", "resDesc": "字符串"},
        "DIRPATH.directory": {"funcDesc": "父目录", "resDesc": "字符串"},
        "Date.get_time_year": {"funcDesc": "获取年份", "resDesc": "整数"},
        "Date.get_time_month": {"funcDesc": "获取月份", "resDesc": "整数"},
        "Date.get_time_day": {"funcDesc": "获取日", "resDesc": "整数"},
        "Date.get_time_hour": {"funcDesc": "获取小时", "resDesc": "整数"},
        "Date.get_time_minute": {"funcDesc": "获取分钟", "resDesc": "整数"},
        "Date.get_time_second": {"funcDesc": "获取秒", "resDesc": "整数"},
        "Date.get_time_weekday": {"funcDesc": "获取周几", "resDesc": "整数"},
        "Date.get_time_week": {"funcDesc": "获取周数", "resDesc": "整数"},
        "Browser.get_url": {"funcDesc": "该网页的地址", "resDesc": "字符串"},
        "Browser.get_title": {"funcDesc": "该网页的标题", "resDesc": "字符串"},
        "ExcelObj.get_full_name": {"funcDesc": "文件所在位置", "resDesc": "字符串"},
        "ExcelObj.get_first_free_row": {"funcDesc": "第一个可用行", "resDesc": "整数"},
    },
    "en_US": {
        # ---- Type descriptions & locale-specific templates ----
        "Any": {"desc": "Any Value", "template": "Any Value"},
        "Float": {"desc": "Number"},
        "Int": {"desc": "Integer"},
        "Bool": {"desc": "Boolean", "template": "true or false"},
        "Str": {"desc": "String", "template": '"Hello"'},
        "List": {"desc": "list"},
        "Dict": {"desc": "dictionary", "template": {"name": "John"}},
        "PATH": {"desc": "File Path"},
        "DIRPATH": {"desc": "Folder Path"},
        "Date": {"desc": "Date & Time"},
        "URL": {"desc": "URL"},
        "Pick": {"desc": "Element", "template": "JSON String"},
        "WebPick": {"desc": "Web Element", "template": "JSON String"},
        "WinPick": {"desc": "Desktop Element", "template": "JSON String"},
        "IMGPick": {"desc": "Image Element", "template": "JSON String"},
        "Password": {"desc": "Password"},
        "FeishuBaseInstance": {"desc": "Feishu Object", "template": "Feishu Object."},
        "DialogResult": {"desc": "Dialog Result", "template": "JSON String"},
        "Browser": {"desc": "Browser Object", "template": "Browser Object"},
        "DocumentObject": {"desc": "Word Object", "template": "DocumentObject"},
        "ExcelObj": {"desc": "Excel Object", "template": "ExcelObj"},
        # ---- Function descriptions ----
        "Float.toStr": {"funcDesc": "To String", "resDesc": "String"},
        "Float.toInt": {"funcDesc": "To Integer", "resDesc": "Integer"},
        "Int.toStr": {"funcDesc": "To String", "resDesc": "String"},
        "Str.strip": {"funcDesc": "Strip Whitespace", "resDesc": "String"},
        "Str.toInt": {"funcDesc": "To Integer", "resDesc": "Integer"},
        "Str.toFloat": {"funcDesc": "To Number", "resDesc": "Number"},
        "List.get": {"funcDesc": "Item @{p1:int}", "resDesc": "any Value"},
        "List.getEnd": {"funcDesc": "Last @{p1:int}th Item", "resDesc": "any Value"},
        "List.getLen": {"funcDesc": "list Length", "resDesc": "Integer"},
        "List.getSlice": {"funcDesc": "Items @{p1:int} to @{p2:int}", "resDesc": "list"},
        "Dict.get": {"funcDesc": "Value of Key @{p1:str}", "resDesc": "any Value"},
        "PATH.root": {"funcDesc": "Root Directory", "resDesc": "String"},
        "PATH.directory": {"funcDesc": "Parent Directory", "resDesc": "String"},
        "PATH.file_name": {"funcDesc": "File Name", "resDesc": "String"},
        "PATH.file_name_without_extension": {"funcDesc": "File Name (no extension)", "resDesc": "String"},
        "PATH.file_extension": {"funcDesc": "File Extension", "resDesc": "String"},
        "DIRPATH.root": {"funcDesc": "Root Directory", "resDesc": "String"},
        "DIRPATH.directory": {"funcDesc": "Parent Directory", "resDesc": "String"},
        "Date.get_time_year": {"funcDesc": "Get Year", "resDesc": "Integer"},
        "Date.get_time_month": {"funcDesc": "Get Month", "resDesc": "Integer"},
        "Date.get_time_day": {"funcDesc": "Get Day", "resDesc": "Integer"},
        "Date.get_time_hour": {"funcDesc": "Get Hour", "resDesc": "Integer"},
        "Date.get_time_minute": {"funcDesc": "Get Minute", "resDesc": "Integer"},
        "Date.get_time_second": {"funcDesc": "Get Second", "resDesc": "Integer"},
        "Date.get_time_weekday": {"funcDesc": "Get Weekday", "resDesc": "Integer"},
        "Date.get_time_week": {"funcDesc": "Get Week Number", "resDesc": "Integer"},
        "Browser.get_url": {"funcDesc": "Current URL", "resDesc": "String"},
        "Browser.get_title": {"funcDesc": "Page Title", "resDesc": "String"},
        "ExcelObj.get_full_name": {"funcDesc": "File Location", "resDesc": "String"},
        "ExcelObj.get_first_free_row": {"funcDesc": "First Free Row", "resDesc": "Integer"},
    },
}


def get_types_config(locale: str = "zh_CN") -> dict[str, any]:
    """
    返回注入指定语言翻译的类型配置字典

    返回格式与 config.get("types") 相同，可直接作为 TypesManager.json() 的数据源。

    Args:
        locale: 语言代码，如 "zh_CN"（默认）或 "en_US"

    Returns:
        完整类型配置字典（深拷贝，不修改原始数据）
    """
    t = TRANSLATIONS.get(locale, TRANSLATIONS.get("zh_CN", {}))
    result: dict[str, any] = {}

    for type_key, type_def in TYPES_FRAME.items():
        item = copy.deepcopy(type_def)
        type_trans = t.get(type_key, {})

        # 注入类型级翻译
        if "desc" in type_trans:
            item["desc"] = type_trans["desc"]
        if "template" in type_trans:
            item["template"] = type_trans["template"]

        # 注入方法级翻译
        for func in item.get("funcList", []):
            func_key = func.get("key", "")
            func_trans = t.get(func_key, {})
            if "funcDesc" in func_trans:
                func["funcDesc"] = func_trans["funcDesc"]
            if "resDesc" in func_trans:
                func["resDesc"] = func_trans["resDesc"]

        result[type_key] = item

    return result
