import importlib
import importlib.util
import inspect

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, ReportTip
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.report import report
from astronverse.script.error import (
    MODULE_IMPORT_ERROR,
    MODULE_MAIN_FUNCTION_NOT_FOUND,
    BaseException,
    MSG_MODULE_VERSION_WARRING,
)


class Script:
    process_info_dict = None

    @staticmethod
    def _params(path):
        if not Script.process_info_dict:
            cfg = atomicMg.cfg()
            process_info = cfg["PROJECT_JSON"].get("process_info", {})
            process_info_dict = {}
            for _, process in process_info.items():
                process_params = process.get("process_params", [])
                process_params_dict = {}
                for param in process_params:
                    process_params_dict[param.get("varName")] = param.get("varValue")
                process_info_dict[".{}".format(process.get("process_file_name"))] = process_params_dict
            Script.process_info_dict = process_info_dict

        return Script.process_info_dict.get("{}.py".format(path), [])

    @staticmethod
    def _call(path: str, package: str, **kwargs):
        try:
            process_module = importlib.import_module(path, package=package)
        except Exception as e:
            raise BaseException(MODULE_IMPORT_ERROR.format(path), f"无法导入模块 {path}: {str(e)}")

        main_func = getattr(process_module, "main", None)
        if not main_func or not callable(main_func):
            raise BaseException(MODULE_MAIN_FUNCTION_NOT_FOUND.format(path), f"模块 {path} 未定义可调用的 main 函数")

        res = main_func(kwargs)

        return res, kwargs

    @staticmethod
    def _module_call(path: str, package: str, out_kwargs, inn_kwargs):
        try:
            process_module = importlib.import_module(path, package=package)
        except Exception as e:
            raise BaseException(MODULE_IMPORT_ERROR.format(path), f"无法导入模块 {path}: {str(e)}")

        def is_v2() -> bool:
            """
            返回 1 表示 main(*args, **kwargs)
            返回 2 表示 main(args)
            """
            sig = inspect.signature(process_module.main)

            # 只要出现 VAR_POSITIONAL 或 VAR_KEYWORD 就是第一版
            # main(args) 是第二版
            # main(*args, **kwargs) 是第一版本
            params = list(sig.parameters.values())
            return len(params) == 1 and params[0].name == "args"

        if is_v2():
            out_params = Script._params(path)
            out_params_res = {}
            for k, v in out_params.items():
                out_params_res[k] = eval(v, process_module.__dict__)

            out_kwargs = {**out_params_res, **out_kwargs}

            main_func = getattr(process_module, "main", None)
            if not main_func or not callable(main_func):
                raise BaseException(
                    MODULE_MAIN_FUNCTION_NOT_FOUND.format(path), f"模块 {path} 未定义可调用的 main 函数"
                )

            res = main_func(out_kwargs)
            return out_kwargs
        else:
            report.warning(ReportTip(msg_str=MSG_MODULE_VERSION_WARRING))

            main_func = getattr(process_module, "main", None)
            if not main_func or not callable(main_func):
                raise BaseException(
                    MODULE_MAIN_FUNCTION_NOT_FOUND.format(path), f"模块 {path} 未定义可调用的 main 函数"
                )

            res = main_func(**inn_kwargs)
            return res

    @staticmethod
    def _get_auto_context() -> (dict, str):
        """
        自动获取调用者的上下文变量，收集所有调用栈中的变量
        """
        try:
            frame = inspect.currentframe()
            if frame is None:
                return {}, ""

            # 收集所有调用栈中的变量
            all_vars = {}
            global_vars = {}
            package = ""

            # 跳过当前帧（_get_auto_context 本身）
            frame = frame.f_back
            if frame is None:
                return {}, "", ""

            # 遍历所有调用栈，找到最外层为main的层
            cframe = None
            while frame is not None:
                # 获取当前帧的局部变量
                if frame.f_code.co_name == "main":
                    # 找到 main 函数帧，使用该帧
                    cframe = frame
                    break
                else:
                    frame = frame.f_back

            # 获取局部变量和全局变量
            if cframe is not None:
                local_vars = cframe.f_locals
                # 合并变量，局部变量优先（覆盖全局变量）
                all_vars.update(local_vars)
                package = cframe.f_globals.get("__package__")
                global_vars = cframe.f_globals.get("gv")
            return all_vars, package, global_vars
        except Exception:
            return {}, ""

    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[
            atomicMg.param(
                "process",
                types="Any",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": ["Process"]}),
            ),
            atomicMg.param(
                "process_param",
                types="List",
                need_parse=True,
                formType=AtomicFormTypeMeta(type=AtomicFormType.PROCESSPARAM.value, params={"linkage": "process"}),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("process_res", types="Any")],
    )
    def process(process: str, process_param: list = None):
        """动态调用流程"""

        kwargs = {}
        if process_param:
            for p in process_param:
                kwargs[p.get("varName")] = p.get("varValue")

        _, package, _ = Script._get_auto_context()
        _, kwargs = Script._call(".{}".format(process), package=package, **kwargs)
        return kwargs

    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[
            atomicMg.param(
                "content",
                types="Any",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": "PyModule"}),
            ),
            atomicMg.param(
                "module_param",
                types="List",
                need_parse=True,
                formType=AtomicFormTypeMeta(type=AtomicFormType.PROCESSPARAM.value, params={"linkage": "content"}),
                required=False,
            ),
        ],
        outputList=[atomicMg.param("program_script", types="Any")],
    )
    def module(content: str, module_param: list = None):
        """动态调用模块"""

        out_kwargs = {}
        if module_param:
            for p in module_param:
                out_kwargs[p.get("varName")] = p.get("varValue")

        inn_kwargs, package, global_vars = Script._get_auto_context()
        inn_kwargs = {**global_vars, **inn_kwargs}

        # 为了兼容老版本独立出来
        res = Script._module_call(".{}".format(content), package=package, out_kwargs=out_kwargs, inn_kwargs=inn_kwargs)
        return res

    @staticmethod
    @atomicMg.atomic("Script", inputList=[], outputList=[])
    def component(component: str, **kwargs):
        # 忽略掉所有__开头的kwargs值
        kwargs = {k: v for k, v in kwargs.items() if not k.startswith("__")}

        # 解析组件路径: c1990298105483890688.main -> 组件目录名和模块名
        package = component.split(".")[0] if "." in component else component
        module_name = component.split(".")[-1] if "." in component else component
        _, kwargs = Script._call(".{}".format(module_name), package=package, **kwargs)
        return kwargs
