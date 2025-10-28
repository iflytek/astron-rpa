import importlib

from astronverse.actionlib import AtomicFormTypeMeta, AtomicFormType
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
        inputList=[
            atomicMg.param("process", types="Any", formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": ["Process"]})),
            atomicMg.param("process_param", types="List", need_parse=True, formType=AtomicFormTypeMeta(type=AtomicFormType.PROCESSPARAM.value, params={"linkage": "process"})),
        ],
        outputList=[atomicMg.param("process_res", types="Any")],
    )
    def process(process: str, process_param: list, **kwargs):
        """动态调用流程"""
        return Script._call(process, **kwargs)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[atomicMg.param("content", types="Any", formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value, params={"filters": "PyModule"}))],
        outputList=[atomicMg.param("program_script", types="Any")],
    )
    def module(content: str, **kwargs):
        """动态调用模块"""
        return Script._call(content, **kwargs)
