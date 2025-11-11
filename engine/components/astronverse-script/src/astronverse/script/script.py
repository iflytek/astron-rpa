import sys
import os
import importlib.util
import importlib
import inspect
from astronverse.actionlib import AtomicFormTypeMeta, AtomicFormType
from astronverse.actionlib.atomic import atomicMg
from astronverse.script.error import BaseException, MODULE_IMPORT_ERROR, MODULE_MAIN_FUNCTION_NOT_FOUND


class Script:

    @staticmethod
    def _call(path: str, **kwargs):
        try:
            # 先尝试找到模块规范
            spec = importlib.util.find_spec(path)
            if spec is None or spec.origin is None:
                raise BaseException(MODULE_IMPORT_ERROR.format(path), f"无法找到模块 {path}")

            module_dir = os.path.dirname(os.path.abspath(spec.origin))

            # 临时修改 sys.path，将模块目录添加到最前面
            original_path = sys.path.copy()
            module_dir_added = False
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
                module_dir_added = True

            try:
                # 如果模块已经导入，检查是否需要重新导入
                # 只有当模块目录不在 sys.path 中时才需要重新导入
                if path in sys.modules and module_dir_added:
                    # 使用 reload 而不是删除，更安全
                    process_module = importlib.reload(sys.modules[path])
                else:
                    process_module = importlib.import_module(path)
            finally:
                # 恢复 sys.path
                sys.path[:] = original_path

        except Exception as e:
            raise BaseException(MODULE_IMPORT_ERROR.format(path), f"无法导入模块 {path}: {str(e)}")

        main_func = getattr(process_module, "main", None)
        if not main_func or not callable(main_func):
            raise BaseException(MODULE_MAIN_FUNCTION_NOT_FOUND.format(path), f"模块 {path} 未定义可调用的 main 函数")
        res = main_func(kwargs)
        return res, kwargs

    @staticmethod
    def _get_auto_context() -> dict:
        """
        自动获取调用者的上下文变量，收集所有调用栈中的变量
        """
        try:
            frame = inspect.currentframe()
            if frame is None:
                return {}

            # 收集所有调用栈中的变量
            all_vars = {}

            # 跳过当前帧（_get_auto_context 本身）
            frame = frame.f_back
            if frame is None:
                return {}

            # 遍历所有调用栈，找到最外层为main的层
            cframe = frame
            while frame is not None:
                # 获取当前帧的局部变量
                if frame.f_locals.get("main"):
                    break
                else:
                    cframe = frame
                    frame = frame.f_back

            # 获取局部变量和全局变量
            if cframe is not None:
                local_vars = cframe.f_locals
                # 合并变量，局部变量优先（覆盖全局变量）
                all_vars.update(local_vars)
            return all_vars
        except Exception:
            return {}

    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[
            atomicMg.param("process", types="Any", formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": ["Process"]})),
            atomicMg.param("process_param", types="List", need_parse=True, formType=AtomicFormTypeMeta(type=AtomicFormType.PROCESSPARAM.value, params={"linkage": "process"})),
        ],
        outputList=[atomicMg.param("process_res", types="Any")],
    )
    def process(process: str, process_param: list):
        """动态调用流程"""

        kwargs = {}
        if process_param:
            for p in process_param:
                kwargs[p.get("varName")] = p.get("varValue")
        _, kwargs = Script._call(process, **kwargs)
        return kwargs

    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[atomicMg.param("content", types="Any", formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": "PyModule"}))],
        outputList=[atomicMg.param("program_script", types="Any")],
    )
    def module(content: str):
        """动态调用模块"""
        kwargs = Script._get_auto_context()
        res, _ = Script._call(content, **kwargs)
        return res

    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[],
        outputList=[]
    )
    def component(component: str, **kwargs):
        # 忽略掉所有__开头的kwargs值
        kwargs = {k: v for k, v in kwargs.items() if not k.startswith('__')}
        _, kwargs = Script._call(component, **kwargs)
        return kwargs
