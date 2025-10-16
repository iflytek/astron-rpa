import json
from enum import Enum
from typing import Any, Dict, List
from astronverse.executorv2.flow.syntax import IParam, InputParam, Token, OutputParam


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


class Param(IParam):

    def __init__(self, svc):
        self.svc = svc

    def _dict_deep_traverse(self, data, process_func):
        """深度遍历字典"""
        if isinstance(data, dict):
            for key in list(data.keys()):  # 使用list()来避免在遍历过程中修改字典
                value = data[key]
                res = process_func(key, value)
                if res is not None:
                    data[key] = res
                    continue
                self._dict_deep_traverse(value, process_func)
        elif isinstance(data, list):
            for item in data:
                self._dict_deep_traverse(item, process_func)

    @staticmethod
    def pre_param_handler(param_value: Any):
        """
        预处理参数
        1. 预处理data优先
        2. 过筛前端无效数据
        """

        ls = []
        # 判断是不是列表, 并且列表的结构符合要求
        if isinstance(param_value, list) and len(param_value) > 0 and "type" in param_value[0] and param_value[0]["type"] in param_type_dict:
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
    def _param_to_eval(ls: list) -> (Any, bool):
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
            data = v.get("data", "")
            if need_eval:
                # 转换成eval能执行的状态
                if types == ParamType.STR.value:
                    res.append("\"{}\"".format(data.replace("\n", "\\n").replace('\t', '\\t').replace('\r', '\\r')))
                else:
                    res.append("{}".format(data))
            else:
                # 直接输出
                res.append(data)

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

    def _param_to_eval_special(self, value: Any) -> Any:
        """特殊dict处理"""

        if not isinstance(value, dict):
            return

        if value.get("rpa", "") != "special":
            return

        ls = self.pre_param_handler(value.get("value", []))
        return self._param_to_eval(ls)

    def parse_param(self, i: dict) -> InputParam:
        ls = self.pre_param_handler(i.get("value"))
        value, need_eval = self._param_to_eval(ls)
        return InputParam(key=i.get("name"), value=value, need_eval=need_eval)

    def _custom_json_dumps(self, obj):
        if isinstance(obj, InputParam):
            if obj.need_eval:
                return obj.value
            else:
                return json.dumps(obj.value, ensure_ascii=False)
        elif isinstance(obj, dict):
            items = []
            for key, value in obj.items():
                key_str = json.dumps(key, ensure_ascii=False)
                value_str = self._custom_json_dumps(value)
                items.append(f"{key_str}: {value_str}")
            return "{" + ", ".join(items) + "}"
        elif isinstance(obj, list):
            items = [self._custom_json_dumps(item) for item in obj]
            return "[" + ", ".join(items) + "]"
        else:
            return json.dumps(obj, ensure_ascii=False)

    def parse_param_special(self, i: dict) -> InputParam:
        data = i.get("value")
        parse = i.get("need_parse")
        if parse == "json_str":
            data = json.loads(data)

        def process_func(key, value):
            res = self._param_to_eval_special(value)
            if res is None:
                return
            value, need_eval = res
            return InputParam(value=value, need_eval=need_eval)

        self._dict_deep_traverse(data, process_func)
        
        # 使用自定义序列化函数，直接处理InputParam对象
        data_str = self._custom_json_dumps(data)
        
        return InputParam(key=i.get("name"), value=data_str, need_eval=True)

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
        return InputParam(key="__condition__", value=value, need_eval=True)

    def parse_input(self, token: Token) -> Dict[str, InputParam]:
        res = {}
        input_list = token.value.get("inputList", [])
        for i in input_list:
            # 优化: 过滤高级选项中的默认值，减少参数传递[可以剔除这段优化代码]
            if (i.get("key") in [
                "__delay_before__",
                "__delay_after__",
                "__retry_time__",
                "__retry_interval__",
            ]
                    and i.get("value") == [{"type": "other", "value": 0}]
                    or i.get("key") == "__res_print__"
                    and i.get("value") is False
                    or i.get("key") == "__skip_err__"
                    and i.get("value") == "exit"
            ):
                continue

            # 0. 显隐关系
            if not i.get("show", True):
                continue

            if i.get("need_parse", None) is not None:
                res[i.get("name")] = self.parse_param_special(i)
            else:
                res[i.get("name")] = self.parse_param(i)

        # 高级选项
        info = [
            token.value.get("__line__", 0),
            token.value.get("id", ""),
            token.value.get("alias", token.value.get("title", "")),
        ]
        res["info"] = InputParam(key="__info__", value=info, need_eval=False)
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
                res.append(OutputParam(value=ls[0].get("data", "")))
        return res
