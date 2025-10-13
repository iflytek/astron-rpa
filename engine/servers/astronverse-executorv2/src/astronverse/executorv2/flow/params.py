from enum import Enum
from astronverse.actionlib.types import Bool, Float, Int, List as RpaList, Dict as RpaDict
from typing import Any, Dict, List
from astronverse.executorv2.flow.syntax import IParam, InputParam, Token, OutputParam
from astronverse.executorv2.flow.syntax.token import token_type_key_dict


class ParamType(Enum):
    PYTHON = "python"  # python模式
    VAR = "var"  # 流变量
    P_VAR = "p_var"  # 流程变量
    G_VAR = "g_var"  # 全局变量
    STR = "str"  # 明确是str
    OTHER = "other"  # 等同于str,会部分转换
    ELEMENT = "element"  # 元素

    @classmethod
    def to_dict(cls):
        return {item.value: item.value for item in cls}


param_type_dict = ParamType.to_dict()


class Param(IParam):

    def __init__(self, svc):
        self.svc = svc

    @staticmethod
    def pre_param_handler(param_value: Any, param_types: str = None, show_name: str = ""):
        """
        预处理参数
        1. 预处理data优先
        2. 过筛前端无效数据
        3. 基于type为other的数据进行类型转换
        """

        ls = []
        # 判断是不是列表, 并且列表的结构符合要求
        if isinstance(param_value, list) and len(param_value) > 0 and "type" in param_value[0] and param_value[0]["type"] in param_type_dict:
            # 预处理1: 处理data优先
            # 预处理2: 过略前端无效数据
            for v in param_value:
                if "data" not in v:
                    v["data"] = v.get("value", "")
                if v["data"] != "":
                    ls.append(v)
            if len(ls) == 0:
                ls.append(param_value[0])
        else:
            ls = [{"type": ParamType.OTHER.value, "data": param_value}]

        # 预处理3: 基于t处理type为other的数据
        for v in ls:
            if v.get("type") == ParamType.OTHER.value and isinstance(v["data"], str):
                try:
                    param_types = param_types.lower()
                    if param_types == "bool":
                        v["data"] = bool(Bool.__validate__(show_name, v["data"]))
                    elif param_types == "float":
                        v["data"] = float(Float.__validate__(show_name, v["data"]))
                    elif param_types == "int":
                        v["data"] = int(Int.__validate__(show_name, v["data"]))
                    elif param_types == "list":
                        v["data"] = list(RpaList.__validate__(show_name, v["data"]))
                    elif param_types == "dict":
                        v["data"] = dict(RpaDict.__validate__(show_name, v["data"]))
                    elif param_types == "str":
                        v["type"] = ParamType.STR.value
                    else:
                        v["type"] = ParamType.STR.value
                except Exception as e:
                    raise Exception("{}的值转换成{}失败，原始值:{}。".format(show_name, param_types, v["data"])) from e
        # 处理后的数据返回
        return ls

    @staticmethod
    def param_to_eval(ls: list) -> (Any, bool):
        """
        将参数解析成evaL能执行的状态,
        need_eval=False是为了加速, 能够直接算出来就不经过eval处理, 直接输出结果
        """

        # 判断是否需要解析
        need_eval = False
        for v in ls:
            if v.get("type", "str") in [ParamType.PYTHON.value, ParamType.VAR.value, ParamType.G_VAR.value, ParamType.P_VAR.value]:
                need_eval = True
                break

        res = []
        for v in ls:
            types = v.get("type", "str")
            value = v.get("data", "")
            if need_eval:
                # 转换成eval能执行的状态
                if types == ParamType.STR.value:
                    res.append("\"{}\"".format(value.replace("\n", "\\n").replace('\t', '\\t').replace('\r', '\\r')))
                else:
                    res.append("{}".format(value))
            else:
                # 直接输出
                res.append(value)

        # 处理最终数据(>1表示拼凑 =1表示正常数据)
        if len(res) > 1:
            if need_eval:
                # 拼接成eval能执行的状态
                return "+".join("str({})".format(r) for r in res), need_eval
            else:
                # 手动拼接
                res_str = ""
                for r in res:
                    res_str += str(r)
                return res_str, need_eval
        else:
            return res[0], need_eval

    def parse_param(self, i: dict) -> InputParam:
        ls = self.pre_param_handler(i.get("value"), i.get("types").lower(), i.get("title", i.get("name", "")))
        value, need_eval = self.param_to_eval(ls)
        return InputParam(types=i.get("types", "Any"), key=i.get("name"), value=value, need_eval=need_eval)

    def parse_condition_input(self, token: Token) -> InputParam:
        res = {}
        input_list = token.value.get("inputList", [])
        for i in input_list:
            res[i.get("name")] = self.parse_param(i)
        condition = res.get("condition")
        cond = condition.value
        args1 = res.get("args1")
        value = ""
        if cond in ["true", "false", "empty", "notempty"]:
            if cond == "true":
                value = "{} == {}".format(args1.show_value(), True)
            elif cond == "false":
                value = "{} == {}".format(args1.show_value(), False)
            elif cond == "empty":
                value = "{}".format(args1.show_value())
            elif cond == "notempty":
                value = "not {}".format(args1.show_value())
        else:
            args2 = res.get("args2", "")
            if cond == "notin":
                cond = "not in"
            value = "{} {} {}".format(args1.show_value(), cond, args2.show_value())
        return InputParam(types="Bool", key="__condition__", value=value, need_eval=True)

    def parse_input(self, token: Token) -> Dict[str, InputParam]:
        res = {}
        params_name = {}
        input_list = token.value.get("inputList", [])
        for i in input_list:

            # 0. 优化:过滤高级选项中的默认值，减少参数传递[可以剔除这段优化代码]
            if i.get("key") in ["__delay_before__", "__delay_after__", "__retry_time__", "__retry_interval__"] and i.get("value") == [{'type': 'other', 'value': 0}]:
                continue
            elif i.get("key") in ["__res_print__"] and i.get("value") is False:
                continue
            elif i.get("key") in ["__skip_err__"] and i.get("value") == "exit":
                continue

            # 1. 显隐关系
            if not i.get("show", True):
                continue

            # 2. 收集key对应的名称
            if not i.get("key").startswith("__"):
                params_name[i.get("name")] = i.get("title", "")

            if i.get("need_parse", None) is not None:
                res[i.get("name")] = InputParam(types="Any", key=i.get("name"), value=None, need_eval=True)
            else:
                res[i.get("name")] = self.parse_param(i)

        # 添加一些高级选项
        if token.type not in token_type_key_dict:
            res["__project_id__"] = InputParam(types="Str", key="__project_id__", value=token.value.get("__project_id__", ""), need_eval=False)
            res["__process_id__"] = InputParam(types="Str", key="__process_id__", value=token.value.get("__process_id__", ""), need_eval=False)
            res["__process_name__"] = InputParam(types="Str", key="__process_name__", value=token.value.get("__process_name__", ""), need_eval=False)
            res["__atomic_name__"] = InputParam(types="Str", key="__atomic_name__", value=token.value.get("alias", token.value.get("title", "")), need_eval=False)
            res["__line__"] = InputParam(types="Int", key="__line__", value=token.value.get("__line__", 0), need_eval=True)
            res["__line_id__"] = InputParam(types="Str", key="__line_id__", value=token.value.get("id", ""), need_eval=False)
        res["__params_name__"] = InputParam(types="Str", key="__params_name__", value=params_name, need_eval=True)
        return res

    def parse_output(self, token: Token) -> List[OutputParam]:
        res = []
        output_list = token.value.get("outputList", [])
        if len(output_list) > 0:
            for i in output_list:
                # 0. 显隐关系
                if not i.get("show", True):
                    continue

                # 1. 预处理
                ls = self.pre_param_handler(param_value=i.get("value", []))

                # 2. 解析
                res.append(OutputParam(types=i.get("types", "Any"), value=ls[0].get("value", "")))
        return res
