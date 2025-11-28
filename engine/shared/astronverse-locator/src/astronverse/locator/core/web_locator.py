from typing import Any, Optional, Union

import requests
import uiautomation as auto
from astronverse.baseline.logger.logger import logger
from astronverse.locator import LIKE_CHROME_BROWSER_TYPES, BrowserType, ILocator, Rect
from astronverse.locator.utils.window import top_browser


class WEBLocator(ILocator):
    def __init__(self, rect=None, rects=None):
        self.__rect = rect
        self.__rects = rects

    def rect(self) -> Optional[Rect]:
        if self.__rects is not None and len(self.__rects) > 0:
            return self.__rects
        return self.__rect

    def control(self) -> Any:
        return None


class WebFactory:
    """Web工厂"""

    @classmethod
    def find(cls, ele: dict, picker_type: str, **kwargs) -> Union[WEBLocator, None]:
        cur_target_app = kwargs.get("cur_target_app")
        app = ele.get("app", "")
        if cur_target_app:
            app = cur_target_app
        if app not in LIKE_CHROME_BROWSER_TYPES:
            # 直接结束
            return None
        # 获取外部配置
        scroll_into_view = kwargs.get("scroll_into_view", True)

        menu_height, menu_left = cls.__get_web_top__(ele, app=app)

        # 通过插件获取元素位置信息
        rect_res = cls.__get_rect_from_browser_plugin__(ele, app=app, scroll_into_view=scroll_into_view)
        if not rect_res:
            return None
        rect = Rect(
            int(rect_res[0]["x"] + menu_left),
            int(rect_res[0]["y"] + menu_height),
            int(rect_res[0]["right"] + menu_left),
            int(rect_res[0]["bottom"] + menu_height),
        )
        rects = []
        if len(rect_res) > 1:
            for s_rect in rect_res:
                rects.append(
                    Rect(
                        int(s_rect["x"] + menu_left),
                        int(s_rect["y"] + menu_height),
                        int(s_rect["right"] + menu_left),
                        int(s_rect["bottom"] + menu_height),
                    )
                )
        return WEBLocator(rect=rect, rects=rects)

    @classmethod
    def __get_rect_from_browser_plugin__(cls, element: dict, app: str, scroll_into_view=True):
        """通过浏览器插件获取rect"""
        url = "http://127.0.0.1:9082/browser/transition"
        browser_type = app
        path_data = element.get("path", {})
        try:
            # 如果需要滚动到视图中
            if scroll_into_view:
                requests.post(
                    url, json={"browser_type": browser_type, "data": path_data, "key": "scrollIntoView"}, timeout=10
                )

            # 检查元素
            response = requests.post(
                url, json={"browser_type": browser_type, "data": path_data, "key": "checkElement"}, timeout=10
            )

            if response.status_code != 200:
                raise Exception("浏览器插件通信通道出错，请重启应用")

            logger.info(f"浏览器插件返回结果: {response.text}")
            res_json = response.json()

            if not res_json or res_json.get("code", "") != "0000":  # 通信错误
                raise Exception("浏览器插件通信失败, 请检查插件是否安装并启用")
            elif res_json.get("code", "") == "0000":
                data = res_json.get("data", {})
                if data.get("code", "") != "0000":  # 元素错误
                    raise Exception(data.get("msg", "浏览器插件获取元素失败"))
                web_info = data.get("data", {})
                return web_info["rect"]

        except requests.exceptions.ConnectionError:
            raise Exception("无法连接浏览器插件服务，请确认插件状态")
        except requests.exceptions.Timeout:
            raise Exception("浏览器插件响应超时，请检查插件是否安装并启用")
        except Exception as e:
            raise Exception(f"获取元素失败：{e}")

    @classmethod
    def __get_web_top__(cls, element: dict, app: str) -> tuple[int, int]:
        """浏览器右上角位置"""
        root_control = auto.GetRootControl()
        app_name = app
        uiapath_list = element.get("uiapath", "")
        target_ctl = None if uiapath_list == "" else uiapath_list[0]
        logger.info(f"weblocator-__get_web_top__ 携带的uia头信息 {target_ctl}")

        ct = None
        for control, _ in auto.WalkControl(root_control, includeTop=True, maxDepth=1):
            if app_name in [BrowserType.CHROME.value]:
                if (control.Name == "Chrome Legacy Window") or (
                    ("- Google Chrome" in control.Name) or ("- Chrome" in control.Name)
                ):
                    ct = control
                    break
            if app_name in [BrowserType.EDGE.value]:
                if "- Microsoft​ Edge" in control.Name:
                    ct = control
                    break
            if app_name in [BrowserType.CHROME_360_SE.value]:
                if "360安全浏览器" in control.Name:
                    ct = control
                    break
            if app_name in [BrowserType.CHROME_360_X.value]:
                if "360极速浏览器X" in control.Name:
                    ct = control
                    break
            if app_name in [BrowserType.FIREFOX.value]:
                if "Mozilla Firefox" in control.Name:
                    ct = control
                    break
            if app_name in [BrowserType.CHROMIUM.value]:
                if (control.Name == "Chrome Legacy Window") or ("- Chromium" in control.Name):
                    ct = control
                    break
        if ct is None:
            raise Exception(f"未找到{app_name}浏览器窗口，请确认浏览器是否已启动")

        # 置顶
        # ct.SetActive()  # noqa 会调用SetForegroundWindow，后者会触发焦点事件
        handle = ct.NativeWindowHandle
        top_browser(handle, ct)
        if app_name in [BrowserType.FIREFOX.value]:
            for child, _ in auto.WalkControl(ct, includeTop=True, maxDepth=100):
                if child.AutomationId == "tabbrowser-tabpanels":
                    bounding_rect = child.BoundingRectangle
                    top = bounding_rect.top
                    left = bounding_rect.left
                    return top, left
        else:
            for child, _ in auto.WalkControl(ct, includeTop=True, maxDepth=100):
                if child.ClassName == "Chrome_RenderWidgetHostHWND":
                    bounding_rect = child.BoundingRectangle
                    top = bounding_rect.top
                    left = bounding_rect.left
                    return top, left
        return 0, 0


web_factory = WebFactory()
