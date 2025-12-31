from __future__ import annotations

import platform
import sys
import time
import re
from typing import List

from astronverse.actionlib.types import WebPick, PATH
from astronverse.browser import *
from astronverse.browser.browser import Browser
from astronverse.browser.browser_element import BrowserElement
from astronverse.browser.core.core import IBrowserCore
from astronverse.browser.js.base import BaseBuilder
from astronverse.browser.js.chrome import CodeChromeBuilder
from astronverse.baseline.logger.logger import logger

if sys.platform == "win32":
    from astronverse.browser.core.core_win import BrowserCore
    from astronverse.locator.locator import locator
    from astronverse.locator import smooth_move
elif platform.system() == "Linux":
    from astronverse.browser.core.core_unix import BrowserCore
    from astronverse.locator.locator import locator
    from astronverse.locator import smooth_move
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

BrowserCore: IBrowserCore = BrowserCore()
CodeChromeBuilder: BaseBuilder = CodeChromeBuilder()
Locator = locator


class WebElement:
    def __init__(self, browser: Browser, element_data: WebPick):
        self.browser = browser
        self.element_data = element_data

    def find_elements_by_xpath(self, xpath_selector: str, *, timeout=3) -> List[WebElement]:
        """
        in the current element, use this method when you need to match multiple elements.
        return a list of document's elements（WebElement）that match the specific xpath, raise exception if match failed
        * @param xpath_selector, the xpath selector to match the elements
        * @param timeout, please specify the timeout value as 3, it is important to use this value. if no one of the elements is found within the timeout, raise exception
        * @return `List[WebElement]`, return the list of the Web elements that match the xpath selector
        """
        if xpath_selector[0] == ".":
            xpath_selector = xpath_selector[1:]
        elements = BrowserElement().get_relative_element(
            browser_obj=self.browser,
            element_data=self.element_data,
            relative_type=RelativeType.Child,
            child_element_type=ChildElementType.Xpath,
            child_element_xpath=xpath_selector,
            element_timeout=timeout,
        )

        logger.info("\n\n\nfind all elements by xpath: \n" + str(elements) + "\n" + str(type(elements)) + "\n\n")

        if elements is None:
            raise Exception("Can not find element by xpath: " + xpath_selector)

        if not isinstance(elements, list):
            elements = [elements]

        logger.info("\n\n\nfind all elements by xpath: \n" + str(elements) + "\n" + str(type(elements)) + "\n\n")

        return [WebElement(browser=self.browser, element_data=element) for element in elements]

    def input(self, text: str, *, delay_after=0.3) -> None:
        """
        type into the field character by character, as if it was a user with a real keyboard with
        focuses the element and triggers an input event with the entered text. it works for <input>, <textarea> and [contenteditable] elements.
        * @param text, the text to type into the field
        * @param delay_after, the delay time after the input operation, please specify the value as 0.3, it is important to use this value.
        """
        BrowserElement().input(
            browser_obj=self.browser,
            element_data=self.element_data,
            simulate_flag=True,
            fill_type=FillInputForFillTypeFlag.Text,
            fill_input=text,
            focus_time=100,
        )
        time.sleep(delay_after)

    def get_text(self) -> str:
        """
        return current innerText or value attribute of the element as a string.
        """
        return BrowserElement().element_text(browser_obj=self.browser, element_data=self.element_data)

    def click(self, *, delay_after=0.3) -> None:
        """
        performs a simple human click. if the element is not currently visible, this method will scroll the element into view
        * @param delay_after, the delay time after the click operation, please specify the value as 0.3, it is important to use this value.
        """
        BrowserElement().click(
            browser_obj=self.browser,
            element_data=self.element_data,
            simulate_flag=True,
            button_type=ButtonForClickTypeFlag.Left,
        )
        time.sleep(delay_after)

    def dbl_click(self, *, delay_after=0.3) -> None:
        """
        performs a double click on the element. if the element is not currently visible, this method will scroll the element into view
        * @param delay_after, the delay time after the double click operation, please specify the value as 0.3, it is important to use this value.
        """
        BrowserElement().click(
            browser_obj=self.browser,
            element_data=self.element_data,
            simulate_flag=True,
            button_type=ButtonForClickTypeFlag.Double,
        )
        time.sleep(delay_after)

    def right_click(self, *, delay_after=0.3) -> None:
        """
        performs a right click on the element. if the element is not currently visible, this method will scroll the element into view
        * @param delay_after, the delay time after the right click operation, please specify the value as 0.3, it is important to use this value.
        """
        BrowserElement().click(
            browser_obj=self.browser,
            element_data=self.element_data,
            simulate_flag=True,
            button_type=ButtonForClickTypeFlag.Right,
        )
        time.sleep(delay_after)

    def wait_element_exist(self, xpath_selector: str, timeout=3) -> WebElement:
        """
        Wait for the first element matching the specified XPath to appear in the current page.
        Returns the WebElement once it is located, or raises an exception if the timeout is exceeded.
        * @param xpath_selector, the xpath selector to match the element
        * @param timeout, please specify the timeout value as 3, it is important to use this value. if the element is not found within the timeout, raise exception
        * @return `WebElement`, return the WebElement object
        * @raises TimeoutException, if the element is not found within the specified timeout
        """
        if xpath_selector is None:
            raise Exception("xpath_selector cannot be None")
        if xpath_selector[0] == ".":
            xpath_selector = xpath_selector[1:]
        elements = BrowserElement().get_relative_element(
            browser_obj=self.browser,
            element_data=self.element_data,
            relative_type=RelativeType.Child,
            child_element_type=ChildElementType.Xpath,
            child_element_xpath=xpath_selector,
            element_timeout=timeout,
        )
        if elements is None:
            raise Exception("element not found")

        return WebElement(browser=self.browser, element_data=elements)

    def wait_all_elements_exist(self, xpath_selector: str, timeout=3) -> List[WebElement]:
        """
        Wait for all elements matching the specified XPath to appear in the current page.
        Returns a list of all matching WebElements. If no elements are found within the timeout,
        returns an empty list instead of raising an exception.
        * @param xpath, the XPath selector used to locate the elements
        * @param timeout, the maximum time to wait for elements to appear (default 10 seconds)
        * @return `List[WebElement]`, a list of all elements that match the rule specified by the xpath parameter.
                         Returns an empty list if no elements are found within the timeout.
        """
        web_elements = []
        if xpath_selector is None:
            return []
        if xpath_selector[0] == ".":
            xpath_selector = xpath_selector[1:]
        elements = BrowserElement().get_relative_element(
            browser_obj=self.browser,
            element_data=self.element_data,
            relative_type=RelativeType.Child,
            child_element_type=ChildElementType.Xpath,
            child_element_xpath=xpath_selector,
            element_timeout=timeout,
            is_multiple=True,
        )

        if elements is None:
            raise Exception("element not found")
        if not isinstance(elements, list):
            elements = [elements]
        for element in elements:
            web_elements.append(WebElement(browser=self.browser, element_data=element))

        return web_elements

    def screenshot(self, folder_path: str, *, filename=None) -> None:
        """
        screenshot the element and save the image to the specified folder.
        * @param folder_path, the path to save the screenshot
        * @param filename, the name of the screenshot file, note that the file name cannot contain the following characters: \ / : * ? " < > |
        """
        BrowserElement().screenshot(
            browser_obj=self.browser, element_data=self.element_data, folder_path=PATH(folder_path), filename=filename
        )

    def set_attribute(self, name: str, value: str) -> None:
        """
        sets the value of an attribute on the specified element.
        if the attribute already exists, the value is updated; otherwise a new attribute is added with the specified name and value.
        * @param name, the name of the attribute
        * @param value, the value of the attribute
        """
        BrowserElement().element_operation(
            browser_obj=self.browser,
            element_data=self.element_data,
            operation_type=ElementAttributeOpTypeFlag.Set,
            attribute_name=name,
            attribute_value=value,
        )

    def get_attribute(self, name: str) -> str:
        """
        return element attribute value. if the attribute does not exist, return an empty string, if is boolean, return the string "True" or "False"（please note it is not "true" or "false"）.
        * @param name, the name of the attribute
        * @return `str`, return the str value of the attribute
        """
        return BrowserElement().element_operation(
            browser_obj=self.browser,
            element_data=self.element_data,
            operation_type=ElementAttributeOpTypeFlag.Get,
            get_type=ElementGetAttributeTypeFlag.GetAttribute,
            attribute_name=name,
        )

    def get_html(self) -> str:
        """
        return current outerHTML attribute of the element as a string.
        """
        return BrowserElement().element_operation(
            browser_obj=self.browser,
            element_data=self.element_data,
            operation_type=ElementAttributeOpTypeFlag.Get,
            get_type=ElementGetAttributeTypeFlag.GetHtml,
        )

    def scroll_into_view(self) -> None:
        """
        scrolls the element into view if it is not currently visible
        """
        BrowserElement().scroll_into_view(browser_obj=self.browser, element_data=self.element_data)

    def hover(self, delay_after=0.3) -> None:
        """
        hover over the matching element.
        * @param delay_after, the delay time after the hover operation, please specify the value as 0.3, it is important to use this value.
        """
        BrowserElement().hover_over(browser_obj=self.browser, element_data=self.element_data)
        time.sleep(delay_after)

    def parent(self) -> WebElement:
        """
        returns the WebElement parent Element, or None if the WebElement either has no parent
        * @return `WebElement`, return the parent WebElement object
        """
        elements = BrowserElement().get_relative_element(
            browser_obj=self.browser, element_data=self.element_data, relative_type=RelativeType.Parent
        )

        if elements is None:
            raise Exception("parent element not found")

        return WebElement(browser=self.browser, element_data=elements)

    def children(self) -> List[WebElement]:
        """
        returns a list[WebElement] which contains all the child elements of the WebElement upon which it was called
        * @return `List[WebElement]`, return the list of the child WebElement objects
        """
        elements = BrowserElement().get_relative_element(
            browser_obj=self.browser,
            element_data=self.element_data,
            relative_type=RelativeType.Child,
            child_element_type=ChildElementType.All,
        )
        if elements is None:
            raise Exception("child element not found")
        if not isinstance(elements, list):
            elements = [elements]

        return [WebElement(browser=self.browser, element_data=element) for element in elements]

    def child_at(self, index) -> WebElement:
        """
        call xbot.element children internally: return None if eid is None else return the child element at the specified index
        * @param index, the index of the child element
        * @return `WebElement`, return the child WebElement object at the specified index
        """
        element = BrowserElement().get_relative_element(
            browser_obj=self.browser,
            element_data=self.element_data,
            relative_type=RelativeType.Child,
            child_element_type=ChildElementType.Index,
            child_element_index=index,
        )

        return WebElement(browser=self.browser, element_data=element)

    def slider_hover(
        self,
        progress_element: WebElement,
        percent_value: float = 0.0,
        drag_direction: str = "right",
        drag_type: str = "start",
        duration: float = 0.25,
    ) -> None:
        """
        滑块拖拽操作
        * @param progress_element, 滑条元素（滑块移动的轨道）
        * @param percent_value, 拖拽百分比（0-100）
        * @param drag_direction, 拖拽方向（"left", "right", "up", "down"）
        * @param drag_type, 拖拽类型（"start" 从起点开始, "current" 相对当前位置）
        * @param duration, 拖拽持续时间
        """
        from rpabrowser.browser_element import BrowserElement
        from rpabrowser import ElementDragDirectionTypeFlag, ElementDragTypeFlag

        # 转换字符串参数为枚举
        direction_map = {
            "left": ElementDragDirectionTypeFlag.Left,
            "right": ElementDragDirectionTypeFlag.Right,
            "up": ElementDragDirectionTypeFlag.Up,
            "down": ElementDragDirectionTypeFlag.Down,
        }

        type_map = {"start": ElementDragTypeFlag.Start, "current": ElementDragTypeFlag.Current}

        drag_direction_flag = direction_map.get(drag_direction.lower(), ElementDragDirectionTypeFlag.Right)
        drag_type_flag = type_map.get(drag_type.lower(), ElementDragTypeFlag.Start)

        BrowserElement.slider_hover(
            browser_obj=self.browser,
            element_slider=self.element_data,  # 当前元素作为滑块
            element_progress=progress_element.element_data,  # 传入的滑条元素
            percent_value=percent_value,
            drag_direction=drag_direction_flag,
            drag_type=drag_type_flag,
            duration=duration,
        )

    def scroll_to(self, *, location="bottom") -> None:
        """
        scrolls to a particular set of coordinates inside a given element
        * @param location, the position to scroll to, default scroll to the bottom of the element
            * `'bottom'`, scroll to the bottom of the element
            * `'top'`, scroll to the top of the element
        """
        from rpabrowser import ScrollbarType, ScrollDirection, ScrollbarForYScrollTypeFlag

        if location == "bottom":
            y_scroll_type = ScrollbarForYScrollTypeFlag.Bottom
        elif location == "top":
            y_scroll_type = ScrollbarForYScrollTypeFlag.Top
        else:
            raise ValueError(f"Unsupported location: {location}. Supported values are 'top' and 'bottom'")

        BrowserElement().scroll(
            browser_obj=self.browser,
            element_data=self.element_data,
            scrollbar_type=ScrollbarType.Element,
            scroll_direction=ScrollDirection.Vertical,
            y_scroll_type=y_scroll_type,
        )

    def drag_to(self, *, top=0, left=0, delay_after=0.3) -> None:
        """
        drag current element with the specified offset
        please note that the mouse will key down at current element's center (x,y)，move to the target position (x+left,y+top) and release
        * @param top, the vertical offset
        * @param left, the horizontal offset
        * @param delay_after, the delay time after the drag operation, please specify the value as 0.3, it is important to use this value.
        """
        # 尝试使用现有的Mouse API和smooth_move
        from rpagui.code.mouse import Mouse
        from rpa_locator import smooth_move

        # 获取元素中心位置
        element = Locator.locator(self.element_data.get("elementData"))
        center = element.point()

        start_x, start_y = center.x, center.y
        end_x = start_x + left
        end_y = start_y + top

        # 执行拖拽操作
        smooth_move(start_x, start_y, duration=0.05)
        Mouse.down(x=start_x, y=start_y, button="left")
        smooth_move(end_x, end_y, duration=0.3)
        Mouse.up(x=end_x, y=end_y, button="left")

        time.sleep(delay_after)

    # 暂未使用，未验证
    def execute_javascript(self, code: str, argument=None, execution_world="ISOLATED") -> str:
        """
        executes javascript code on the current element
        * @param code, the javascript code to execute, must be a javascript function, like:
        ```python
        function (element, args) {
            // element is current element
            // args represents the input parameters
            return args;
        }
        ``` {data-source-line="232"}
        note: the value returned by the function must be a string, if you need to return other types, you need to organize them as a string in the function. For example:
        ```js
        function (element, args) {
            return JSON.stringify(args);
        }
        ``` {data-source-line="238"}
        * @param argument, the argument to pass to the javascript function, must be a string, if you need to pass other types, you can first convert them to JSON string
        * @param execution_world, the execution environment, support value "ISOLATED"(plugin environment) or "MAIN"(web page environment), default is "ISOLATED"
        * @return `str`, return the str result of the javascript execution
        """
        from rpabrowser.browser_script import BrowserScript
        from rpabrowser import InputType

        # === 新增：自动修复常见的错误输入 ===
        # 匹配 function(...) { ... } 或 function (...) { ... }
        pattern = r"^\s*function\s*\([^)]*\)\s*\{(.*)\}\s*$"
        match = re.fullmatch(pattern, code.strip(), re.DOTALL)
        if match:
            # 提取函数体，并去除首尾空白
            code = match.group(1).strip()
            # 可选：打印警告（调试用）
            print("Warning: Detected full function declaration. Extracted body only.")

        # 构建JavaScript代码，确保包含main函数
        if "function main" not in code:
            js_code = f"function main(element, args) {{\n{code}\n}}"
        else:
            js_code = code

        # 准备参数
        params = []
        if argument is not None:
            params.append({"varName": "args", "varValue": str(argument)})

        result = BrowserScript.js_run(
            browser_obj=self.browser,
            input_type=InputType.Content,
            content=js_code,
            params=params,
            element_data=self.element_data,  # 传递当前元素数据
        )

        return str(result) if result is not None else ""
