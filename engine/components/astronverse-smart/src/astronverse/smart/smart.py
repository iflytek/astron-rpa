import inspect
import json
import platform
from typing import Any

from astronverse.actionlib import AtomicFormTypeMeta, AtomicFormType, DynamicsItem
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import WebPick
from astronverse.browser.browser import Browser

from astronverse.browser import *
from astronverse.browser.browser import Browser
from astronverse.browser.browser_software import BrowserSoftware
from astronverse.browser.browser_element import get_browser_obj

from astronverse.smart.browser_ai.web_browser import WebBrowser
from astronverse.smart.core.core import ISmartCore

if platform.system() == "Windows":
    from astronverse.smart.core.core_win import SmartCore
elif platform.system() == "Linux":
    from astronverse.smart.core.core_unix import SmartCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

SmartCore: ISmartCore = SmartCore()


class Smart:
    @staticmethod
    @atomicMg.atomic(
        "Smart",
        inputList=[
            atomicMg.param("smart_info"),
            atomicMg.param("code_params", required=False),
        ],
    )
    def run_code(smart_info: dict, **code_params) -> Any:
        """
        执行 AI 生成的代码，支持网页自动化和数据处理两种类型。
        inputs:
            smart_code：表示AI生成的代码
            smart_type：区分代码类型，web_auto | data_process
            code_params：代码入参
        outputs:
            result：代码执行结果
        """
        smart_code = smart_info.get("smartCode", "")
        smart_type = smart_info.get("smartType", "")

        if not smart_code.strip():
            return None

        if smart_type != "web_auto":
            return Smart.run_core(smart_code, **code_params)

        # Browser类型转为WebBrowser类型
        web_browser = None
        for key, value in code_params.items():
            if isinstance(value, Browser):
                web_browser = WebBrowser(value)
                code_params[key] = web_browser
                break
        # 打开元素对应url
        # if web_browser is None:
        #     for key, value in code_params.items():
        #         if isinstance(value, dict) and value.get("elementData"):
        #             url = value.get("elementData").get("path").get("url")
        #             browser_type = value.get("elementData").get("app")
        #             break
        #     web_browser = WebBrowser(
        #         BrowserSoftware.browser_open(url=url, browser_type=CommonForBrowserType(browser_type)))
        #     code_params["browser"] = web_browser
        # 获取当前url
        if web_browser is None:
            web_browser = WebBrowser(get_browser_obj())
            code_params["browser"] = web_browser

        # WebPick类型转为WebElement类型
        for key, value in code_params.items():
            if isinstance(value, dict) and value.get("elementData"):
                code_params[key] = web_browser.get_element_by_web_pick(value)

        return Smart.run_core(smart_code, **code_params)

    @staticmethod
    def run_core(smart_code_str, **code_params) -> Any:
        # 动态执行环境（限制安全）
        exec_globals = {"__builtins__": __builtins__}
        exec(smart_code_str, exec_globals)

        # 提取唯一的用户自定义顶级函数
        func = next(
            obj
            for name, obj in exec_globals.items()
            if (
                callable(obj)
                # 排除内置函数
                and not inspect.isbuiltin(obj)
                # 排除lambda
                and not isinstance(obj, type(lambda: None).__class__)
                # 排除模块
                and not inspect.ismodule(obj)
                # 确保是函数对象且有代码属性
                and hasattr(obj, "__code__")
                # 函数名与定义名一致
                and obj.__code__.co_name == name
                # 关键：用户在当前代码块中定义的函数，模块属性为__main__
                and getattr(obj, "__module__") is None
                # 额外保险：确保函数是在当前执行的代码中定义的
                and obj.__code__.co_filename == "<string>"
            )
        )
        return func(**code_params)
