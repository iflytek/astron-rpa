"""
匹配工具模块

提供统一的属性值匹配功能，支持全等、通配符、正则表达式三种匹配模式。
对齐 web 端 ElementAttrs.type 的 0/1/2 约定。
"""

import fnmatch
import re


class MatchType:
    EXACT = 0  # 全等
    WILDCARD = 1  # 通配符（* 和 ?）
    REGEX = 2  # 正则表达式


def match_value(pattern: str, actual: str, match_type: int = MatchType.EXACT) -> bool:
    """
    统一匹配函数

    Args:
        pattern: 前端传来的期望值（精确值 / 通配符模式 / 正则表达式）
        actual:  从控件实际读到的值
        match_type: 匹配模式，默认 0（全等）
    """
    if not pattern and not actual:
        return True
    if pattern is None or actual is None:
        return pattern == actual

    pattern = str(pattern)
    actual = str(actual)

    if match_type == MatchType.REGEX:
        try:
            return bool(re.search(pattern, actual))
        except re.error:
            return False
    elif match_type == MatchType.WILDCARD:
        return fnmatch.fnmatch(actual, pattern)
    else:
        return pattern == actual
