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
        outputList=[atomicMg.param("process", types="Any")],
    )
    def process(content: str, **kwargs):
        """动态调用流程"""
        return Script._call(content, **kwargs)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("module", types="Any")],
    )
    def module(content: str, **kwargs):
        """动态调用模块"""
        return Script._call(content, **kwargs)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("condition", types="Bool")],
    )
    def condition(args1, condition, args2) -> bool:
        return True

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("condition", types="Int")],
    )
    def for_range(start: int, end: int, step: int):
        return range(start, end, step)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("index", types="Int"), atomicMg.param("list_item", types="Any")]
    )
    def for_list(lists):
        return enumerate(lists)

    @staticmethod
    @atomicMg.atomic(
        "Script",
        outputList=[atomicMg.param("key", types="Any"), atomicMg.param("value", types="Any")]
    )
    def for_dict(dicts):
        return dict(dicts).items()