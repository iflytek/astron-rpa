"""Code 类自身的调用面测试。

控制流原子能力是标记节点，真实执行由 executor 的 syntax 解释器完成。这里锁定两件
事：装饰后仍可被直接调用（build_meta、调试脚本都会走这条路），以及每个原子能力都
带上了 atomicMg 的注册标记（缺失时 register 会静默跳过，原子能力凭空消失）。
"""

import inspect

import pytest
from astronverse.control import ConditionType
from astronverse.control.control import Code

MARKER_METHODS = (
    "Break",
    "Continue",
    "Return",
    "Else",
    "IfEnd",
    "ElseEnd",
    "ElseIfEnd",
    "WhileEnd",
    "ForEnd",
    "ForListEnd",
    "ForDictEnd",
    "ForStepEnd",
    "Try",
    "TryEnd",
    "Catch",
    "CatchEnd",
    "Finally",
    "FinallyEnd",
    "Group",
    "GroupEnd",
)


def _atomic_methods() -> list[str]:
    return [
        name
        for name, member in inspect.getmembers(Code, predicate=inspect.isfunction)
        if getattr(member, "__tag_key__", None) == "atomic"
    ]


def test_all_public_methods_are_registered_atomics():
    """Code 上不应存在漏加装饰器的公开方法，否则它不会进入 meta。"""
    public = [name for name, _ in inspect.getmembers(Code, predicate=inspect.isfunction) if not name.startswith("_")]
    assert sorted(public) == sorted(_atomic_methods())


@pytest.mark.parametrize("name", MARKER_METHODS)
def test_marker_atomics_are_callable_without_arguments(name):
    """无参标记节点直接调用不应抛异常，返回 None。"""
    assert getattr(Code, name)() is None


def test_conditional_atomics_accept_keyword_arguments():
    """条件节点走关键字调用，默认 condition 为 ==。"""
    assert Code.If(args1="a", args2="b") is None
    assert Code.ElseIf(args1=1, condition=ConditionType.GT, args2=0) is None
    assert Code.While(args1=1, condition=ConditionType.NE, args2=2) is None


def test_loop_atomics_accept_keyword_arguments():
    """循环节点同样只做标记，不真正迭代。"""
    assert Code.ForList(list_obj=[1, 2, 3]) is None
    assert Code.ForDict(dicts={"a": 1}) is None
    assert Code.ForStep(start=0, end=3) is None
    assert Code.ForStep(start=0, end=3, step=2) is None


def test_positional_arguments_are_rejected():
    """atomicMg 的 wrapper 不支持位置参数，避免流程里参数错位。"""
    from astronverse.actionlib.error import BizException

    with pytest.raises(BizException):
        Code.If("a", ConditionType.EQ, "b")


@pytest.mark.parametrize("name", ["If", "ElseIf", "While"])
def test_condition_default_is_equal(name):
    """condition 的默认值决定新拖入节点的初始运算符。"""
    signature = inspect.signature(getattr(Code, name).__wrapped__)
    assert signature.parameters["condition"].default is ConditionType.EQ
    assert signature.parameters["args2"].default is None
