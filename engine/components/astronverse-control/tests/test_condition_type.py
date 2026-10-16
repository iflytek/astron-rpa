"""ConditionType 枚举契约测试。

枚举的 value 直接落进 meta 的 options，并被前端设计器和 control.py 的 dynamics
表达式引用，改动 value 会静默破坏已有流程配置，因此逐个锁定。
"""

from astronverse.control import ConditionType

EXPECTED_VALUES = {
    "EQ": "==",
    "NE": "!=",
    "GT": ">",
    "GE": ">=",
    "LT": "<",
    "LE": "<=",
    "IN": "in",
    "NOT_IN": "notin",
    "TRUE": "true",
    "FALSE": "false",
    "EMPTY": "empty",
    "NOT_EMPTY": "notempty",
}


def test_condition_type_members_and_values():
    """成员名与 value 必须与前端/流程数据里的字面量完全一致。"""
    assert {member.name: member.value for member in ConditionType} == EXPECTED_VALUES


def test_condition_type_values_are_unique():
    """value 用作 options 的唯一标识，重复会让选项互相覆盖。"""
    values = [member.value for member in ConditionType]
    assert len(values) == len(set(values))


def test_condition_type_declaration_order_is_stable():
    """meta 中 options 的顺序即枚举声明顺序，决定下拉框展示顺序。"""
    assert [member.value for member in ConditionType] == list(EXPECTED_VALUES.values())
