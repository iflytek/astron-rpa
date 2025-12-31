import platform
import sys
import os
from typing import List, Union

from astronverse.actionlib.types import WebPick
from astronverse.browser import *
from astronverse.browser.browser import Browser
from astronverse.browser.browser_software import BrowserSoftware
from astronverse.browser.browser_element import BrowserElement
from astronverse.browser.core.core import IBrowserCore
from astronverse.baseline.logger.logger import logger

from astronverse.smart.browser_ai.web_element import WebElement

if sys.platform == "win32":
    from astronverse.browser.core.core_win import BrowserCore
elif platform.system() == "Linux":
    from astronverse.browser.core.core_unix import BrowserCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))

BrowserCore: IBrowserCore = BrowserCore()


class WebBrowser:
    def __init__(self, browser: Browser):
        self.browser = browser

    def get_url(self) -> str:
        """
        returns the current URL of the page (WebBrowser).
        """
        return self.browser.get_url()

    def get_title(self) -> str:
        """
        returns the title of the page (WebBrowser).
        """
        return self.browser.get_title()

    def web_switch_by_url(self, url="") -> None:
        """
        switch to the browser tab with the specified URL.
        * @param url, the URL of the tab to switch to
        """
        BrowserSoftware().web_switch(browser_obj=self.browser, switch_type=WebSwitchType.URL, tab_url=url)

    def get_element_by_web_pick(self, web_pick: WebPick) -> WebElement:
        return WebElement(browser=self.browser, element_data=web_pick)

    def open_web(self, url: str) -> None:
        """
        open the browser page.
        * @param url, the URL of the page to open
        """
        browser = BrowserSoftware.web_open(browser_obj=self.browser, new_tab_url=url, wait_page=True)
        return WebBrowser(browser=browser)

    def go_back(self, *, load_timeout=10) -> None:
        """
        navigates to the previous page.
        * @param load_timeout, the timeout for loading the page, default is 10s, if the page is not loaded within the timeout, raise exception
        """
        BrowserSoftware().browser_back(browser_obj=self.browser)
        if load_timeout > 0:
            BrowserSoftware().wait_web_load(browser_obj=self.browser, timeout=load_timeout)

    def go_forward(self, *, load_timeout=10) -> None:
        """
        navigates to the next page.
        * @param load_timeout, the timeout for loading the page, default is 10s, if the page is not loaded within the timeout, raise exception
        """
        BrowserSoftware().browser_forward(browser_obj=self.browser)
        if load_timeout > 0:
            BrowserSoftware().wait_web_load(browser_obj=self.browser, timeout=load_timeout)

    def wait_load_completed(self, timeout=10) -> None:
        """
        Returns when the required load state has been reached or the timeout has been exceeded.
        * @param timeout, default 10s, if the page is not loaded within the timeout, raise exception
        """
        BrowserSoftware().wait_web_load(browser_obj=self.browser, timeout=timeout)

    def scroll_to(self, *, location="bottom") -> None:
        """
        scrolls to a particular set of coordinates in the document.
        * @param location, the position to scroll to, default scroll to the bottom of the page
            *`'bottom'` scroll to the bottom of the page
            *`'top'`, scroll to the top of the page
        """
        if location == "bottom":
            y_scroll_type = ScrollbarForYScrollTypeFlag.Bottom
        elif location == "top":
            y_scroll_type = ScrollbarForYScrollTypeFlag.Top
        else:
            raise ValueError(f"Unsupported location: {location}. Supported values are 'top' and 'bottom'")

        BrowserElement.scroll(
            browser_obj=self.browser,
            scrollbar_type=ScrollbarType.Window,
            scroll_direction=ScrollDirection.Vertical,
            y_scroll_type=y_scroll_type,
        )

    def find_elements_by_xpath(self, xpath_selector, *, timeout=3) -> List[WebElement]:
        """
        in the current page, use this method when you need to match multiple elements.
        return a list of document's elements（WebElement）that match the specific xpath, raise exception if match failed
        * @param xpath_selector, the xpath selector to match the elements
        * @param timeout, please specify the timeout value as 3, it is important to use this value. if no one of the elements is found within the timeout, raise exception
        * @return `List[WebElement]`, return the list of the Web elements that match the xpath selector
        """
        # 使用现有的create_element方法
        element_obj = BrowserElement.create_element(
            browser_obj=self.browser, locate_type=LocateType.Xpath, locate_value=xpath_selector
        )

        web_elements = []

        if isinstance(element_obj, list):
            # 返回多个元素
            for element_data in element_obj:
                web_element = WebElement(browser=self.browser, element_data=element_data)
                web_elements.append(web_element)
        else:
            # 返回单个元素
            web_element = WebElement(browser=self.browser, element_data=element_obj)
            web_elements.append(web_element)

        return web_elements

    def screenshot(self, folder_path, *, file_name=None, full_size=True) -> None:
        """
        screenshot the current page and save the image to the specified folder.
        * @param folder_path, the path to save the screenshot
        * @param file_name, the name of the screenshot file, note that the file name cannot contain the following characters: \ / : * ? " < > |
        * @param full_size, whether to capture the entire page, True captures the entire page, False captures the visible area, default is True
        """

        # 如果没有提供文件名，生成一个默认的文件名
        if file_name is None:
            import time

            timestamp = int(time.time())
            file_name = f"screenshot_{timestamp}.jpg"

        # 确保文件名有正确的扩展名
        if not file_name.endswith((".png", ".jpg", ".jpeg")):
            file_name += ".jpg"

        # 根据full_size参数选择截图范围
        shot_range = ScreenShotForShotRangeFlag.All if full_size else ScreenShotForShotRangeFlag.Visual

        # 调用BrowserSoftware的screenshot方法
        BrowserSoftware().screenshot(
            browser_obj=self.browser, shot_range=shot_range, image_path=folder_path, image_name=file_name
        )

    def wait_element_exist(self, xpath_selector: Union[WebElement, str], timeout=3) -> WebElement:
        """
        Wait for the first element matching the specified XPath to appear in the current page.
        Returns the WebElement once it is located, or raises an exception if the timeout is exceeded.
        * @param xpath_selector, the XPath selector used to locate the element
        * @param timeout, the maximum time to wait for the element (default 10 seconds).
                         An exception is raised if the element is not found within this timeout.
        * @return `WebElement`, the first element that matches the rule specified by the xpath parameter.
        * @raises TimeoutException, if the element is not found within the specified timeout
        """
        if isinstance(xpath_selector, WebElement):
            element_data = xpath_selector.element_data
            web_element = xpath_selector

        elif isinstance(xpath_selector, str):
            elements = self.find_elements_by_xpath(xpath_selector, timeout=timeout)
            if not elements:
                raise Exception("element not found")
            logger.info(str(elements))
            web_element = elements[0]
            element_data = elements[0].element_data
        else:
            raise Exception(f"Unsupported xpath selector type: {type(xpath_selector)}")

        exist = BrowserElement().wait_element(
            browser_obj=self.browser,
            element_data=element_data,
            ele_status=WaitElementForStatusFlag.ElementExists,
            element_timeout=timeout,
        )
        if not exist:
            raise Exception("element not found")

        return web_element

    def wait_all_elements_exist(self, xpath_selector: Union[WebElement, str], *, timeout=3) -> List[WebElement]:
        """
        Wait for all elements matching the specified XPath to appear in the current page.
        Returns a list of all matching WebElements. If no elements are found within the timeout,
        returns an empty list instead of raising an exception.
        * @param xpath_selector, the XPath selector used to locate the elements
        * @param timeout, the maximum time to wait for elements to appear (default 10 seconds)
        * @return `List[WebElement]`, a list of all elements that match the rule specified by the xpath parameter.
                         Returns an empty list if no elements are found within the timeout.
        """
        if isinstance(xpath_selector, WebElement):
            element_data = xpath_selector.element_data
            exist = BrowserElement().wait_element(
                browser_obj=self.browser,
                element_data=element_data,
                ele_status=WaitElementForStatusFlag.ElementExists,
                element_timeout=timeout,
            )
            return [xpath_selector] if exist else []

        elif isinstance(xpath_selector, str):
            elements = self.find_elements_by_xpath(xpath_selector, timeout=timeout)
            elements = elements if isinstance(elements, list) else [elements] if elements else []
            logger.info(str(elements))

            # 检查每个元素是否存在（按需保留，若find_elements已确保存在可简化）
            valid_elements = []
            for web_element in elements:
                element_data = web_element.element_data  # 修复：使用当前元素的data
                exist = BrowserElement().wait_element(
                    browser_obj=self.browser,
                    element_data=element_data,
                    ele_status=WaitElementForStatusFlag.ElementExists,
                    element_timeout=timeout,
                )
                if exist:
                    valid_elements.append(web_element)

            logger.info(f"Found {len(valid_elements)} valid elements for XPath: {xpath_selector}")
            return valid_elements

        else:
            raise Exception(f"Unsupported xpath selector: {xpath_selector}")
