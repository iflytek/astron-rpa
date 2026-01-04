import importlib
import importlib.util
import inspect

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta
from astronverse.actionlib.atomic import atomicMg
from astronverse.script.error import MODULE_IMPORT_ERROR, MODULE_MAIN_FUNCTION_NOT_FOUND, BaseException


class Script:
    def _call(path: str, package: str, **kwargs):
        try:
            process_module = importlib.import_module(path, package=package)
        except Exception as e:
            raise BaseException(MODULE_IMPORT_ERROR.format(path), f"无法导入模块 {path}: {str(e)}")

        main_func = next((obj for _, obj in inspect.getmembers(process_module, inspect.isfunction)), None)
        if not main_func or not callable(main_func):
            raise BaseException(MODULE_MAIN_FUNCTION_NOT_FOUND.format(path), f"模块 {path} 未定义可调用的 main 函数")

        # module_package = getattr(process_module, '__package__', None)
        # if module_package != package:
        #     process_module.__package__ = package

        res = main_func(kwargs)

        return res, kwargs

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
            package = ""

            # 跳过当前帧（_get_auto_context 本身）
            frame = frame.f_back
            if frame is None:
                return {}, ""

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
            return all_vars, package
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
            ),
        ],
        outputList=[atomicMg.param("process_res", types="Any")],
    )
    def process(process: str, process_param: list):
        """动态调用流程"""

        kwargs = {}
        if process_param:
            for p in process_param:
                kwargs[p.get("varName")] = p.get("varValue")

        _, package = Script._get_auto_context()
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
            ),
        ],
        outputList=[atomicMg.param("program_script", types="Any")],
    )
    def module(content: str, module_param: list):
        """动态调用模块"""

        _, package = Script._get_auto_context()
        kwargs = {}
        if module_param:
            for p in module_param:
                kwargs[p.get("varName")] = p.get("varValue")
        _, kwargs = Script._call(".{}".format(content), package=package, **kwargs)
        return kwargs

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
