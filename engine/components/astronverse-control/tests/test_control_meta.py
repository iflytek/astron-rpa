"""控制流原子能力注册出的 meta 契约测试。

Code 类的方法体全是 pass，唯一的可观察行为是 @atomicMg.atomic 注册出来的 meta：
- key：executor 的 syntax token 按字面量匹配（见 astronverse-executor 的 token.py）
- inputList / outputList：设计器据此渲染表单并回填流程变量
- options / dynamics：条件下拉框和 args2 的显隐联动
任一项漂移都会静默破坏已有流程，因此在此逐项锁定。
"""

import pytest

# executor 的 syntax token 依赖这些 key，改名等于破坏已存流程
EXECUTOR_TOKEN_KEYS = {
    "Code.Break",
    "Code.Continue",
    "Code.Return",
    "Code.If",
    "Code.ElseIf",
    "Code.Else",
    "Code.IfEnd",
    "Code.While",
    "Code.ForStep",
    "Code.ForList",
    "Code.ForDict",
    "Code.ForEnd",
    "Code.Try",
    "Code.Catch",
    "Code.Finally",
    "Code.TryEnd",
    "Code.Group",
    "Code.GroupEnd",
}

# 全部注册的原子能力
ALL_KEYS = EXECUTOR_TOKEN_KEYS | {
    "Code.ElseEnd",
    "Code.ElseIfEnd",
    "Code.WhileEnd",
    "Code.ForListEnd",
    "Code.ForDictEnd",
    "Code.ForStepEnd",
    "Code.CatchEnd",
    "Code.FinallyEnd",
}

# 带条件表达式的原子能力：args1 + condition + args2
CONDITIONAL_KEYS = ("Code.If", "Code.ElseIf", "Code.While")

# args2 仅在二元比较运算符下显示，true/false/empty/notempty 时隐藏
ARGS2_SHOW_EXPRESSION = (
    "return ['==', '!=', '>', '>=', '<', '<=', 'in', 'notin'].includes($this.condition.value)"
)


def test_registers_exactly_the_expected_atomics(base_meta):
    """注册集合必须完全等于预期，新增/删除原子能力都应显式更新此断言。"""
    assert set(base_meta) == ALL_KEYS


def test_executor_token_keys_are_all_registered(base_meta):
    """executor 的 syntax token 引用的 key 必须都能在 meta 中找到。"""
    assert set(base_meta) >= EXECUTOR_TOKEN_KEYS


@pytest.mark.parametrize("key", sorted(ALL_KEYS))
def test_every_atomic_declares_core_fields(base_meta, key, component_version):
    """每个原子能力都要有 version / src / noAdvanced，供前端与执行器定位。"""
    atomic = base_meta[key]
    assert atomic["key"] == key
    assert atomic["version"] == component_version
    assert atomic["src"] == "astronverse.control.control.Code().{}".format(key.split(".", 1)[1])
    assert atomic["noAdvanced"] is True


@pytest.mark.parametrize("key", sorted(ALL_KEYS))
def test_marker_atomics_have_no_hidden_advanced_params(base_meta, key):
    """控制流节点均声明 noAdvanced，前端不应渲染延时等高级参数面板。"""
    assert base_meta[key]["noAdvanced"] is True


@pytest.mark.parametrize(
    ("key", "input_keys", "output_keys"),
    [
        ("Code.Break", [], []),
        ("Code.Continue", [], []),
        ("Code.Return", [], []),
        ("Code.Else", [], []),
        ("Code.IfEnd", [], []),
        ("Code.ElseEnd", [], []),
        ("Code.ElseIfEnd", [], []),
        ("Code.WhileEnd", [], []),
        ("Code.ForEnd", [], []),
        ("Code.ForListEnd", [], []),
        ("Code.ForDictEnd", [], []),
        ("Code.ForStepEnd", [], []),
        ("Code.Try", [], []),
        ("Code.TryEnd", [], []),
        ("Code.Catch", [], []),
        ("Code.CatchEnd", [], []),
        ("Code.Finally", [], []),
        ("Code.FinallyEnd", [], []),
        ("Code.Group", [], []),
        ("Code.GroupEnd", [], []),
        ("Code.If", ["args1", "condition", "args2"], []),
        ("Code.ElseIf", ["args1", "condition", "args2"], []),
        ("Code.While", ["args1", "condition", "args2"], []),
        ("Code.ForList", ["list_obj"], ["index", "item"]),
        ("Code.ForDict", ["dicts"], ["key", "value"]),
        ("Code.ForStep", ["start", "end", "step"], ["index"]),
    ],
)
def test_param_keys_and_order(base_meta, key, input_keys, output_keys):
    """输入输出的 key 与顺序决定表单渲染顺序和流程里的变量名。"""
    atomic = base_meta[key]
    assert [p["key"] for p in atomic["inputList"]] == input_keys
    assert [p["key"] for p in atomic["outputList"]] == output_keys


@pytest.mark.parametrize(
    ("key", "types"),
    [
        ("Code.ForList", {"index": "Int", "item": "Any"}),
        ("Code.ForDict", {"key": "Any", "value": "Any"}),
        ("Code.ForStep", {"index": "Int"}),
    ],
)
def test_loop_outputs_types_and_form_type(base_meta, key, types):
    """循环变量的 types 决定下游节点的类型推断，formType 固定为 RESULT。"""
    outputs = {p["key"]: p for p in base_meta[key]["outputList"]}
    assert {k: v["types"] for k, v in outputs.items()} == types
    for param in outputs.values():
        assert param["formType"]["type"] == "RESULT"


def test_for_step_input_types_and_default(base_meta):
    """计数循环的三个入参均为 Int，step 默认 1。"""
    inputs = {p["key"]: p for p in base_meta["Code.ForStep"]["inputList"]}
    assert {k: v["types"] for k, v in inputs.items()} == {"start": "Int", "end": "Int", "step": "Int"}
    assert inputs["step"]["default"] == 1
    assert "default" not in inputs["start"]
    assert "default" not in inputs["end"]


@pytest.mark.parametrize(
    ("key", "param", "types"),
    [("Code.ForList", "list_obj", "List"), ("Code.ForDict", "dicts", "Dict")],
)
def test_loop_input_types(base_meta, key, param, types):
    """列表/字典循环的入参类型由注解反射得到，前端据此做输入校验。"""
    inputs = {p["key"]: p for p in base_meta[key]["inputList"]}
    assert inputs[param]["types"] == types


@pytest.mark.parametrize("key", CONDITIONAL_KEYS)
def test_condition_param_options_match_enum(base_meta, key):
    """condition 下拉选项由 ConditionType 反射生成，顺序与值必须一致。"""
    from astronverse.control import ConditionType

    condition = next(p for p in base_meta[key]["inputList"] if p["key"] == "condition")
    assert condition["types"] == "ConditionType"
    assert condition["default"] == ConditionType.EQ.value
    assert [opt["value"] for opt in condition["options"]] == [member.value for member in ConditionType]


@pytest.mark.parametrize("key", CONDITIONAL_KEYS)
def test_condition_uses_select_form_type(base_meta, key):
    """选项超过 3 个时 actionlib 反射为 SELECT，前端渲染下拉而非单选。"""
    condition = next(p for p in base_meta[key]["inputList"] if p["key"] == "condition")
    assert condition["formType"]["type"] == "SELECT"


@pytest.mark.parametrize("key", CONDITIONAL_KEYS)
def test_args2_visibility_dynamics(base_meta, key):
    """args2 的显隐表达式覆盖全部二元运算符，且不包含一元条件。"""
    args2 = next(p for p in base_meta[key]["inputList"] if p["key"] == "args2")
    assert args2["dynamics"] == [{"key": "$this.args2.show", "expression": ARGS2_SHOW_EXPRESSION}]


def test_args2_dynamics_covers_exactly_binary_conditions():
    """显隐表达式里的运算符集合应与 ConditionType 的二元运算符一一对应。"""
    import re

    from astronverse.control import ConditionType

    in_expression = set(re.findall(r"'([^']+)'", ARGS2_SHOW_EXPRESSION))
    unary = {
        ConditionType.TRUE.value,
        ConditionType.FALSE.value,
        ConditionType.EMPTY.value,
        ConditionType.NOT_EMPTY.value,
    }
    binary = {member.value for member in ConditionType} - unary
    assert in_expression == binary


@pytest.mark.parametrize("key", CONDITIONAL_KEYS)
def test_condition_operands_accept_variables_and_python(base_meta, key):
    """args1/args2 需允许变量与 Python 表达式输入，否则条件判断无法引用流程变量。"""
    inputs = {p["key"]: p for p in base_meta[key]["inputList"]}
    for name in ("args1", "args2"):
        assert inputs[name]["types"] == "Any"
        assert inputs[name]["formType"]["type"] == "INPUT_VARIABLE_PYTHON"
