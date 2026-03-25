import sys
from typing import Any, Optional, Union

import requests
from astronverse.baseline.logger.logger import logger
from astronverse.locator import (
    LIKE_CHROME_BROWSER_TYPES,
    BrowserType,
    ILocator,
    Rect,
    BROWSER_UIA_POINT_CLASS,
    BROWSER_UIA_WINDOW_CLASS,
    BROWSER_AX_PROCESS_NAMES,
)
from astronverse.locator.error import (
    BizException,
    BROWSER_PLUGIN_CHANNEL_ERROR,
    BROWSER_PLUGIN_COMMUNICATION_ERROR,
    BROWSER_PLUGIN_GET_ELEMENT_ERROR_FORMAT,
    BROWSER_PLUGIN_CONNECTION_ERROR,
    BROWSER_PLUGIN_TIMEOUT_ERROR,
    BROWSER_WINDOW_NOT_FOUND_FORMAT,
    ERROR_FORMAT,
)

if sys.platform == "win32":
    import uiautomation as auto
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
        scroll_into_center = kwargs.get("scroll_into_center", True)

        if sys.platform == "darwin":
            menu_height, menu_left = cls.__get_web_top_mac__(ele, app=app)
        else:
            menu_height, menu_left = cls.__get_web_top__(ele, app=app)

        # 通过插件获取元素位置信息
        rect_res = cls.__get_rect_from_browser_plugin__(
            ele, app=app, scroll_into_view=scroll_into_view, scroll_into_center=scroll_into_center
        )
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
    def __get_rect_from_browser_plugin__(cls, element: dict, app: str, scroll_into_view=True, scroll_into_center=True):
        """通过浏览器插件获取rect"""
        url = "http://127.0.0.1:9082/browser/transition"
        browser_type = app
        path_data = element.get("path", {})
        try:
            # 如果需要滚动到视图中
            if scroll_into_view:
                path_data = {**path_data, "atomConfig": {"scrollIntoCenter": scroll_into_center}}
                requests.post(
                    url, json={"browser_type": browser_type, "data": path_data, "key": "scrollIntoView"}, timeout=10
                )

            # 检查元素
            response = requests.post(
                url, json={"browser_type": browser_type, "data": path_data, "key": "checkElement"}, timeout=10
            )

            if response.status_code != 200:
                raise BizException(BROWSER_PLUGIN_CHANNEL_ERROR, "浏览器插件通信通道出错，请重启应用")

            logger.info(f"浏览器插件返回结果: {response.text}")
            res_json = response.json()

            if not res_json or res_json.get("code", "") != "0000":  # 通信错误
                raise BizException(BROWSER_PLUGIN_COMMUNICATION_ERROR, "浏览器插件通信失败, 请检查插件是否安装并启用")
            elif res_json.get("code", "") == "0000":
                data = res_json.get("data", {})
                if data.get("code", "") != "0000":  # 元素错误
                    msg = data.get("msg", "浏览器插件获取元素失败")
                    raise BizException(BROWSER_PLUGIN_GET_ELEMENT_ERROR_FORMAT.format(msg), msg)
                web_info = data.get("data", {})
                return web_info["rect"]

        except requests.exceptions.ConnectionError:
            raise BizException(BROWSER_PLUGIN_CONNECTION_ERROR, "无法连接浏览器插件服务，请确认插件状态")
        except requests.exceptions.Timeout:
            raise BizException(BROWSER_PLUGIN_TIMEOUT_ERROR, "浏览器插件响应超时，请检查插件是否安装并启用")
        except Exception as e:
            error_msg = f"获取元素失败：{e}"
            raise BizException(ERROR_FORMAT.format(error_msg), error_msg)

    @classmethod
    def __get_web_top_mac__(cls, element: dict, app: str) -> tuple[int, int]:
        """浏览器内容区域左上角位置（macOS AXUIElement 版本）"""
        process_names = BROWSER_AX_PROCESS_NAMES.get(app)
        if not process_names:
            return 0, 0

        try:
            import psutil
            from ApplicationServices import (
                AXUIElementCreateApplicationWithPID,
                AXUIElementCopyAttributeValue,
                kAXErrorSuccess,
            )
            import ApplicationServices as AS
        except ImportError:
            return 0, 0

        # ── AX 工具函数（与 axui_picker 保持一致） ──────────────────────────

        def _ax_attr(el, attr):
            try:
                err, val = AXUIElementCopyAttributeValue(el, attr, None)
                return val if err == kAXErrorSuccess else None
            except Exception:
                return None

        def _ax_unpack_point(val):
            try:
                ok, pt = AS.AXValueGetValue(val, AS.kAXValueCGPointType, None)
                if ok and pt is not None:
                    return pt.x, pt.y
            except Exception:
                pass
            return None

        # 1. 通过进程名找 PID ──────────────────────────────────────────────
        pid = 0
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                proc_name = proc.info.get("name", "") or ""
                for candidate in process_names:
                    if (
                        candidate.lower() in proc_name.lower()
                        or proc_name.lower() in candidate.lower()
                    ):
                        pid = proc.info["pid"]
                        break
                if pid:
                    break
        except Exception:
            pass

        if pid == 0:
            msg = f"未找到{app}浏览器进程，请确认浏览器是否已启动"
            raise BizException(BROWSER_WINDOW_NOT_FOUND_FORMAT.format(app), msg)

        # 2. 激活浏览器窗口（置前） ─────────────────────────────────────────
        try:
            import AppKit
            for running_app in AppKit.NSWorkspace.sharedWorkspace().runningApplications():
                if running_app.processIdentifier() == pid:
                    running_app.activateWithOptions_(
                        AppKit.NSApplicationActivateIgnoringOtherApps
                    )
                    break
        except Exception:
            pass

        # 3. 创建 AXApplication 并获取主窗口 ──────────────────────────────
        ax_app = AXUIElementCreateApplicationWithPID(pid)
        main_window = (
            _ax_attr(ax_app, "AXMainWindow")
            or _ax_attr(ax_app, "AXFocusedWindow")
        )
        if main_window is None:
            windows = _ax_attr(ax_app, "AXWindows") or []
            if not windows:
                return 0, 0
            main_window = windows[0]

        # 4. 遍历 AX 树找到 web 内容区域 ──────────────────────────────────
        # 策略一：Chrome/Edge/Chromium 的 BrowserView > View 模式
        # 与 axui_picker.AXUIOperate.get_web_control 逻辑保持一致
        def _find_browser_view(node, depth=0):
            if depth > 12:
                return None
            dom_class = _ax_attr(node, "AXDOMClassList") or []
            if "View" in dom_class:
                parent = _ax_attr(node, "AXParent")
                if parent is not None:
                    parent_dom = _ax_attr(parent, "AXDOMClassList") or []
                    if "BrowserView" in parent_dom:
                        pv = _ax_attr(node, "AXPosition")
                        pt = _ax_unpack_point(pv) if pv else None
                        if pt:
                            return int(pt[1]), int(pt[0])  # top, left
            for child in (_ax_attr(node, "AXChildren") or []):
                result = _find_browser_view(child, depth + 1)
                if result:
                    return result
            return None

        # 策略二：通用 AXWebArea（Firefox 兜底）
        def _find_webarea(node, depth=0):
            if depth > 12:
                return None
            if _ax_attr(node, "AXRole") == "AXWebArea":
                pv = _ax_attr(node, "AXPosition")
                pt = _ax_unpack_point(pv) if pv else None
                if pt:
                    return int(pt[1]), int(pt[0])  # top, left
            for child in (_ax_attr(node, "AXChildren") or []):
                result = _find_webarea(child, depth + 1)
                if result:
                    return result
            return None

        result = _find_browser_view(main_window) or _find_webarea(main_window)
        return result if result else (0, 0)

    @classmethod
    def __get_web_top__(cls, element: dict, app: str) -> tuple[int, int]:
        """浏览器右上角位置"""
        app_name = app
        cfg = BROWSER_UIA_WINDOW_CLASS.get(app_name)
        if not cfg:
            return 0, 0
        point_cfg = BROWSER_UIA_POINT_CLASS.get(app_name)
        if not point_cfg:
            return 0, 0

        class_name, patterns, match_type = cfg
        tag_value, tag = point_cfg

        # 查找窗口
        root_control = auto.GetRootControl()
        base_ctrl = None
        for control, depth in auto.WalkControl(root_control, includeTop=True, maxDepth=1):
            if control.ClassName != class_name:
                continue
            if not patterns:
                base_ctrl = control
                break
            text = control.Name.split("-")[-1].strip() if match_type == "last_in" else control.Name
            if any(p.lower() in text.lower() for p in patterns):
                base_ctrl = control
                break

        if base_ctrl is None:
            msg = f"未找到{app_name}浏览器窗口，请确认浏览器是否已启动"
            raise BizException(BROWSER_WINDOW_NOT_FOUND_FORMAT.format(app_name), msg)

        # 置顶窗口
        try:
            top_browser(handle=base_ctrl.NativeWindowHandle, ctrl=base_ctrl)
        except Exception as e:
            pass

        # 获取位置
        for control, depth in auto.WalkControl(base_ctrl, includeTop=True, maxDepth=12):
            if tag == "ClassName":
                tag_match = control.ClassName
            elif tag == "AutomationId":
                tag_match = control.AutomationId
            else:
                tag_match = ""
            if tag_match == tag_value:
                bounding_rect = control.BoundingRectangle
                top = bounding_rect.top
                left = bounding_rect.left
                return top, left
        return 0, 0


web_factory = WebFactory()
