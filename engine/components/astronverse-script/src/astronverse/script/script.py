import importlib
from astronverse.actionlib.atomic import atomicMg
from astronverse.script.error import BaseException, MODULE_IMPORT_ERROR, MODULE_MAIN_FUNCTION_NOT_FOUND


class Script:

    @staticmethod
    def _call(path: str, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if not k.startswith("__")}
        try:
            process_module = importlib.import_module(path)
        except Exception as e:
            raise BaseException(MODULE_IMPORT_ERROR.format(path), f"无法导入模块 {path}: {str(e)}")

        main_func = getattr(process_module, "main", None)
        if not main_func or not callable(main_func):
            raise BaseException(MODULE_MAIN_FUNCTION_NOT_FOUND.format(path), f"模块 {path} 未定义可调用的 main 函数")
        return main_func(**kwargs)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("call_process", types="Any")],
    )
    def call_process(process_path: str, **kwargs):
        """动态调用流程"""
        return Script._call(process_path, **kwargs)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("call_module", types="Any")],
    )
    def call_module(module_path: str, **kwargs):
        """动态调用模块"""
        return Script._call(module_path, **kwargs)
