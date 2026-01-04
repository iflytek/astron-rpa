import json
from enum import Enum
from typing import Any, Dict, List
from astronverse.executor.flow.syntax import IParam, InputParam, Token, OutputParam


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
    def _param_to_eval(ls: list, gv: dict = None) -> (Any, bool):
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
                if gv and data in gv:  # 兜底
                    pieces.append(f"gv[{data!r}]")
                else:
                    pieces.append(data)

        if len(pieces) == 1:
            return pieces[0], need_eval
        if need_eval:
            return "+".join(f"str({p})" for p in pieces), need_eval
        else:
            return "".join(pieces), need_eval, need_eval

    def parse_param(self, i: dict, token=None) -> InputParam:
        name = i.get("name", i.get("key"))
        data = i.get("value")
        parse = i.get("need_parse")
        key = token.value.get("key") if token else ""
        special = ""

        if parse is not None:
            if parse == "json_str":
                data = json.loads(data)
            return InputParam(key=name, value=data, need_eval=True, special="complex_param_parser")
        else:
            if isinstance(data, list) and len(data) == 1 and data[0].get("type", None) == ParamType.ELEMENT.value:
                # 元素
                special = "element"
            elif key == "Script.process" and name == "process":
                # 子模块
                special = "module"
            elif key == "Script.module" and name == "content":
                # 子模块
                special = "module"
            elif key == "Script.component" and name == "component":
                # 子模块
                special = "component"
            elif key == "Smart.run_code" and name == "smart_component":
                # 子组件的子模块
                special = "smart_component"
            value, need_eval = self._param_to_eval(self.pre_param_handler(data))
            return InputParam(key=name, value=value, need_eval=need_eval, special=special)

    def parse_input(self, token: Token) -> Dict[str, InputParam]:
        res = {}
        params_name = {}
        input_list = token.value.get("inputList", [])
        for i in input_list:
            # 优化: 过滤高级选项中的默认值，减少参数传递[可以剔除这段优化代码]
            if (
                i.get("key")
                in [
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

            # 1. 显隐关系
            if not i.get("show", True):
                continue

            if not i.get("key").startswith("__"):
                params_name[i.get("name", i.get("key"))] = i.get("title", "")

            # 2. 解析
            res[i.get("name", i.get("key"))] = self.parse_param(i, token=token)

        # 高级选项
        info = [
            token.value.get("__line__", 0),
            token.value.get("__process_id__", ""),
        ]
        res["info"] = InputParam(key="__info__", value=info, need_eval=True)
        project_id = self.svc.ast_curr_info.get("__project_id__")
        self.svc.add_atomic_info(project_id, token.value.get("key"), params_name)
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
                value = ls[0].get("data", "")

                project_id = self.svc.ast_curr_info.get("__project_id__")
                global_var = self.svc.ast_globals_dict[project_id].project_info.global_var
                if global_var and value in global_var:
                    value = f"gv[{value!r}]"

                # 2. 解析
                res.append(OutputParam(value=value))
        return res
