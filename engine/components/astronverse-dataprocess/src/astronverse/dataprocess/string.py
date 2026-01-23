"""字符串处理相关功能。"""

import math
import re
from copy import deepcopy
from typing import Optional

from astronverse.actionlib import DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.dataprocess import (
    CaseChangeType,
    ConcatStringType,
    CutStringType,
    ExtractType,
    FillStringType,
    ReplaceType,
    StripStringType,
)
from astronverse.dataprocess.error import *


def get_pattern(pattern_type, regex_formula: str) -> Optional[str]:
    """根据类型选择对应的正则表达式。"""
    pattern: Optional[str] = None
    if pattern_type in [ReplaceType.DIGIT, ExtractType.DIGIT]:
        pattern = r"\d+"
    elif pattern_type in [ReplaceType.EMAIL, ExtractType.EMAIL]:
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*"
    elif pattern_type in [ReplaceType.PHONE_NUMBER, ExtractType.PHONE_NUMBER]:
        pattern = r"1[3-9]\d{9}"
    elif pattern_type in [ReplaceType.URL, ExtractType.URL]:
        pattern = r"(?:http[s]?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[a-zA-Z0-9-._?&=]*)?"
    elif pattern_type in [ReplaceType.ID_NUMBER, ExtractType.ID_NUMBER]:
        pattern = r"\d{17}[\dXx]"
    elif pattern_type in [ReplaceType.REGEX, ReplaceType.STRING, ExtractType.REGEX]:
        pattern = regex_formula

    return pattern


class StringProcess:
    """字符串处理工具集合。"""

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param(
                "regex_formula",
                dynamics=[
                    DynamicsItem(
                        key="$this.regex_formula.show",
                        expression=f"return $this.extract_type.value == '{ExtractType.REGEX.value}'",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("extract_from_string", types="List")],
    )
    def extract_content_from_string(
        text: str,
        extract_type: ExtractType = ExtractType.DIGIT,
        regex_formula: str = "",
        first_flag: bool = True,
    ):
        """从文本中提取匹配内容。"""
        if regex_formula:
            try:
                re.compile(regex_formula)
                pass
            except re.error:
                raise BaseException(INVALID_REGEX_ERROR_FORMAT.format(regex_formula), "请重新输入")

        pattern = get_pattern(extract_type, regex_formula) or ""
        result = re.findall(pattern, text)
        if first_flag:
            result = result[0] if result else []
        return result

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param(
                "replaced_string",
                dynamics=[
                    DynamicsItem(
                        key="$this.replaced_string.show",
                        expression=f"return $this.replace_type.value == '{ReplaceType.STRING.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "regex_formula",
                dynamics=[
                    DynamicsItem(
                        key="$this.regex_formula.show",
                        expression=f"return $this.replace_type.value == '{ReplaceType.REGEX.value}'",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("replaced_content_string", types="List")],
    )
    def replace_content_in_string(
        text: str = "",
        replace_type: ReplaceType = ReplaceType.STRING,
        replaced_string: str = "",
        regex_formula: str = "",
        new_value: str = "",
        first_flag: bool = True,
        ignore_case_flag: bool = False,
    ):
        """替换字符串中匹配的内容。"""
        if regex_formula:
            try:
                re.compile(regex_formula)
                pass
            except re.error:
                raise BaseException(INVALID_REGEX_ERROR_FORMAT.format(regex_formula), "请重新输入")

        if replace_type == ReplaceType.REGEX:
            old_value = regex_formula
        elif replace_type == ReplaceType.STRING:
            old_value = replaced_string
        else:
            old_value = ""

        count = 1 if first_flag else 0
        pattern = get_pattern(replace_type, old_value) or ""
        return re.sub(
            pattern,
            new_value,
            text,
            count=count,
            flags=re.IGNORECASE if ignore_case_flag else 0,
        )

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("list_data", types="Any"),
        ],
        outputList=[atomicMg.param("merged_string_from_list", types="Str")],
    )
    def merge_list_to_string(list_data: list, separator: str = ""):
        """
        列表聚合成文本
        """
        return str(separator).join(str(x) for x in list_data)

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[],
        outputList=[atomicMg.param("split_list_from_string", types="List")],
    )
    def split_string_to_list(string_data: str, separator: str = ""):
        """
        文本分割为列表
        """
        if separator == "":
            return list(string_data)
        return string_data.split(separator)

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("string_data_1", types="Str"),
            atomicMg.param("string_data_2", types="Str"),
            atomicMg.param(
                "separator",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.separator.show",
                        expression=f"return $this.concat_type.value == '{ConcatStringType.OTHER.value}'",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("concat_string", types="Str")],
    )
    def concatenate_string(
        string_data_1: str,
        string_data_2: str,
        concat_type: ConcatStringType = ConcatStringType.NONE,
        separator: str = "",
    ):
        """拼接两个字符串，按 concat_type 确定分隔符。"""
        if concat_type == ConcatStringType.NONE:
            separator = ""
        elif concat_type == ConcatStringType.SPACE:
            separator = " "
        elif concat_type == ConcatStringType.HYPHEN:
            separator = "-"
        elif concat_type == ConcatStringType.UNDERLINE:
            separator = "_"
        elif concat_type == ConcatStringType.LINEBREAK:
            separator = "\n"
        elif concat_type == ConcatStringType.OTHER:
            separator = str(separator)
        return string_data_1 + separator + string_data_2

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("string_data", types="Str"),
        ],
        outputList=[atomicMg.param("complete_string", types="Str")],
    )
    def fill_string_to_length(
        string_data: str = "",
        add_str: str = "",
        total_length: str = "",
        fill_type: FillStringType = FillStringType.RIGHT,
    ):
        """按指定方向填充字符串到目标长度。"""
        if (not string_data) or (not add_str):
            raise ValueError("目标文本或补充文本不能为空!")
        try:
            total_length_int = int(total_length)
            assert total_length_int >= 0
        except Exception as e:
            raise ValueError("长度输入不合法,请提供整数类型数据!")

        result_str = deepcopy(str(string_data))
        if total_length_int <= len(string_data):
            return result_str
        n = math.ceil((total_length_int - len(string_data)) / len(add_str))  # 向上取整获得重复次数
        if fill_type == FillStringType.LEFT:  # 左端补齐
            result_str = (add_str * n)[0 : total_length_int - len(string_data)] + string_data
        elif fill_type == FillStringType.RIGHT:  # 右端补齐
            result_str = (string_data + add_str * n)[0:total_length]
        return result_str

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("string_data", types="Str"),
        ],
        outputList=[atomicMg.param("stripped_string", types="Str")],
    )
    def strip_string(string_data: str, strip_method: StripStringType = StripStringType.BOTH):
        """移除字符串空白。"""
        if not string_data:
            return ""

        result_str = deepcopy(string_data)
        if strip_method == StripStringType.BOTH:  # 默认删除两端的空格
            result_str = string_data.strip()
        elif strip_method == StripStringType.LEFT:  # 删除左端的空格
            result_str = string_data.lstrip()
        elif strip_method == StripStringType.RIGHT:  # 删除右端的空格
            result_str = string_data.rstrip()
        return result_str

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("string_data", types="Str"),
            atomicMg.param(
                "index",
                dynamics=[
                    DynamicsItem(
                        key="$this.index.show",
                        expression=f"return $this.cut_type.value == '{CutStringType.INDEX.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "find_str",
                dynamics=[
                    DynamicsItem(
                        key="$this.find_str.show",
                        expression=f"return $this.cut_type.value == '{CutStringType.STRING.value}'",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("cut_string", types="Str")],
    )
    def cut_string_to_length(
        string_data: str,
        length: int,
        cut_type: CutStringType = CutStringType.FIRST,
        index: int = 0,
        find_str: str = "",
    ):
        """按照指定方式截取字符串。"""
        if not string_data:
            raise ValueError("目标文本不能为空!")
        if length < 0:
            raise ValueError("长度输入不合法,请提供整数类型数据!")

        result_str = ""
        if cut_type == CutStringType.FIRST:
            result_str = string_data[:length]
        elif cut_type == CutStringType.INDEX:
            result_str = string_data[index : index + length]
        elif cut_type == CutStringType.STRING:
            index = string_data.find(find_str)
            if index == -1:
                raise ValueError("未找到指定字符串!")
            result_str = string_data[index : index + length]
        return result_str

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("string_data", types="Str"),
        ],
        outputList=[atomicMg.param("change_case_string", types="Str")],
    )
    def change_case_of_string(string_data: str, case_type: CaseChangeType = CaseChangeType.LOWER):
        """转换字符串大小写。"""
        if not string_data:
            return ""
        if case_type == CaseChangeType.LOWER:
            return string_data.lower()
        if case_type == CaseChangeType.UPPER:
            return string_data.upper()
        if case_type == CaseChangeType.CAPS:
            return string_data.capitalize()
        raise ValueError("不支持的大小写转换类型")

    @staticmethod
    @atomicMg.atomic(
        "StringProcess",
        inputList=[
            atomicMg.param("string_data", types="Str"),
        ],
        outputList=[atomicMg.param("string_length", types="Int")],
    )
    def get_string_length(string_data: str):
        """返回字符串长度。"""
        return len(string_data) if string_data else 0
