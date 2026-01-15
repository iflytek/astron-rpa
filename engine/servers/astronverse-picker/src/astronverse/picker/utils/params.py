import functools
import inspect
import json
from enum import Enum
from typing import Any, Optional


class ParamType(Enum):
    PYTHON = "python"  # python模式
    VAR = "var"  # 流变量
    P_VAR = "p_var"  # 流程变量
    G_VAR = "g_var"  # 全局变量
    STR = "str"  # 明确是str
    OTHER = "other"  # 等同于str, 引擎会简单转换[当前版本不做转换]
    ELEMENT = "element"  # 元素

    @classmethod
    def to_dict(cls):
        return {item.value: item.value for item in cls}


param_type_dict = ParamType.to_dict()


class RpaExpression:
    """
    包装编译后的 code object，并提供安全求值接口
    """

    __slots__ = ("code", "expr_str")

    def __init__(self, expr_str: str):
        self.expr_str = expr_str
        self.code = compile(expr_str, "<rpa>", "eval")

    def eval(self, context: dict):
        return eval(self.code, context)

    def __repr__(self):
        return f"RpaExpression({self.expr_str!r})"


@functools.lru_cache(maxsize=1024)
def _compile_expression(expr_str: str) -> RpaExpression:
    return RpaExpression(expr_str)


class ComplexParamParser:
    """
    复杂参数解析器
    """

    @staticmethod
    def pre_param_handler(param_value: Any):
        """
        预处理参数
        1. 预处理data优先
        2. 过筛前端无效数据
        """

        ls = []
        # 判断是不是列表, 并且列表的结构符合要求
        if (
            isinstance(param_value, list)
            and len(param_value) > 0
            and "type" in param_value[0]
            and param_value[0]["type"] in param_type_dict
        ):
            # 预处理1: 处理data优先
            # 预处理2: 过略前端无效数据
            for v in param_value:
                if "data" not in v:
                    v["data"] = v.get("value", "")
                del v["value"]
                if v["data"] != "":
                    ls.append(v)
            if len(ls) == 0:
                ls.append(param_value[0])
        else:
            ls = [{"type": ParamType.OTHER.value, "data": param_value}]
        return ls

    @staticmethod
    def param_to_eval(ls: list, gv: dict = None) -> (Any, bool):
        """
        将参数解析成evaL能执行的状态,
        need_eval=False是为了加速, 能够直接算出来就不经过eval处理, 直接输出结果
        """

        need_eval = False
        for v in ls:
            if v.get("type", "str") in [
                ParamType.PYTHON.value,
                ParamType.VAR.value,
                ParamType.G_VAR.value,
                ParamType.P_VAR.value,
            ]:
                need_eval = True
                break

        pieces = []
        for v in ls:
            types = v.get("type", "str")
            data = v.get("data", v.get("value", ""))
            if need_eval:
                if types in [ParamType.STR.value, ParamType.OTHER.value]:
                    pieces.append(f"{data!r}")
                elif types in [ParamType.G_VAR.value]:
                    pieces.append(f"gv[{data!r}]")
                else:
                    pieces.append(f"{data}")
            else:
                if gv and data in gv:  # 兜底[目前没有兜底策略]
                    pieces.append(f"gv[{data!r}]")
                else:
                    pieces.append(data)

        if len(pieces) == 1:
            return pieces[0], need_eval
        if need_eval:
            return "+".join(f"str({p})" for p in pieces), need_eval
        else:
            return "".join(pieces), need_eval, need_eval

    @classmethod
    def _recursive_convert_params(cls, data: Any) -> Any:
        """
        递归转换复杂参数结构
        """
        if isinstance(data, dict):
            if data.get("rpa") == "special" and "value" in data:
                if isinstance(data["value"], list) and len(data["value"]) > 0:
                    expr_str, need_eval = cls.param_to_eval(data["value"])
                    if need_eval:
                        return _compile_expression(expr_str)
                    else:
                        return expr_str
                else:
                    return data["value"]
            return {k: cls._recursive_convert_params(v) for k, v in data.items()}
        if isinstance(data, list):
            return [cls._recursive_convert_params(item) for item in data]
        return data

    @classmethod
    def parse_params(cls, source: Any, context_vars: Optional[dict] = None) -> Any:
        """
        解析复杂参数结构
        """
        # context_vars 参数保留用于向后兼容，但在转换阶段不需要使用
        # 真正的变量解析在 evaluate_params 阶段进行
        return cls._recursive_convert_params(source)

    @classmethod
    def evaluate_params(cls, converted: Any, ctx: Optional[dict] = None) -> Any:
        """
        对已解析的参数结构进行求值
        """
        auto_ctx = cls._get_auto_context()
        if ctx is not None:
            merged_ctx = {**auto_ctx, **ctx}
        else:
            merged_ctx = auto_ctx
        return cls._evaluate_params_recursive(converted, merged_ctx)

    @classmethod
    def _evaluate_params_recursive(cls, converted: Any, merged_ctx: dict) -> Any:
        """
        递归求值参数结构，使用预获取的上下文
        """
        if isinstance(converted, RpaExpression):
            res = converted.eval(merged_ctx)
            return res
        if isinstance(converted, dict):
            return {k: cls._evaluate_params_recursive(v, merged_ctx) for k, v in converted.items()}
        if isinstance(converted, list):
            return [cls._evaluate_params_recursive(item, merged_ctx) for item in converted]
        return converted

    @staticmethod
    def _get_auto_context() -> dict:
        """
        自动获取调用者的上下文变量，收集所有调用栈中的变量
        """
        return {}


def complex_param_parser(complex_param: Any, global_data: Any) -> dict:
    res = ComplexParamParser.parse_params(complex_param)

    ctx = {}
    for g in global_data:
        var_value = g.get("varValue", "")
        try:
            var_value = json.loads(var_value)
        except Exception as e:
            pass
        var_value = ComplexParamParser.pre_param_handler(var_value)
        code, need_eval = ComplexParamParser.param_to_eval(var_value)
        if not need_eval:
            code = repr(code)
        ctx[g.get("varName")] = eval(code)
    return ComplexParamParser.evaluate_params(res, {"gv": ctx})
