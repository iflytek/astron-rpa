import importlib
import importlib.util
import inspect

from typing import Any
from astronverse.actionlib.atomic import atomicMg
from astronverse.browser.browser import Browser
from astronverse.browser.browser_element import get_browser_instance
from astronverse.smart.browser_ai.web_browser import WebBrowser


class Smart:
    @staticmethod
    def _smart_call(path: str, package: str, **kwargs):
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

        res = main_func(**kwargs)

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
        "Smart",
        inputList=[
            atomicMg.param("smart_info"),
            atomicMg.param("code_params", required=False),
        ],
    )
    def run_code(smart_component: dict, **code_params) -> Any:
        """
        执行 AI 生成的代码，支持网页自动化和数据处理两种类型。
        """
        file_name = smart_component.get("file_path", "")
        smart_type = smart_component.get("smart_type", "")

        if smart_type != "web_auto":
            return Smart.run_core(file_name, **code_params)
        else:
            web_browser = None
            for key, value in code_params.items():
                if isinstance(value, Browser):
                    web_browser = WebBrowser(value)
                    code_params[key] = web_browser
                    break

            if web_browser is None:
                web_browser = WebBrowser(get_browser_instance())
                code_params["browser"] = web_browser

            # WebPick类型转为WebElement类型
            for key, value in code_params.items():
                if isinstance(value, dict) and value.get("elementData"):
                    code_params[key] = web_browser.get_element_by_web_pick(value)

            return Smart.run_core(file_name, **code_params)

    @staticmethod
    def run_core(file_name, **kwargs) -> Any:
        _, package = Smart._get_auto_context()
        res, _ = Smart._smart_call(".{}".format(file_name), package=package, **kwargs)
        return res
