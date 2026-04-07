import ctypes
import os
import time
from typing import Any

import AppKit
import ApplicationServices as AS
import psutil
from ApplicationServices import (
    AXUIElementCopyAttributeValue,
    AXUIElementCreateApplication,
    AXUIElementGetPid,
    AXUIElementPerformAction,
    AXUIElementSetAttributeValue,
    kAXErrorSuccess,
)

from astronverse.browser import BROWSER_AX_PROCESS_NAMES, BROWSER_MAC_APP_NAME
from astronverse.browser.error import BizException, DOWNLOAD_TIMEOUT, DOWNLOAD_WINDOW_NO_FIND, UPLOAD_WINDOW_NO_FIND


def _ax_attr(element: Any, attr_name: str):
    try:
        err, value = AXUIElementCopyAttributeValue(element, attr_name, None)
        if err == kAXErrorSuccess:
            return value
    except Exception:
        pass
    return None


def _ax_perform(element: Any, action_name: str) -> bool:
    try:
        return AXUIElementPerformAction(element, action_name) == kAXErrorSuccess
    except Exception:
        return False


def _ax_set(element: Any, attr_name: str, value: Any) -> bool:
    try:
        return AXUIElementSetAttributeValue(element, attr_name, value) == kAXErrorSuccess
    except Exception:
        return False


def _ax_unpack_point(value: Any):
    try:
        ok, point = AS.AXValueGetValue(value, AS.kAXValueCGPointType, None)
        if ok and point is not None:
            return int(point.x), int(point.y)
    except Exception:
        pass
    return None


def _match_browser_app(running_app: Any, browser_type: str) -> bool:
    app_name = BROWSER_MAC_APP_NAME.get(browser_type, "")
    plain_name = app_name.removesuffix(".app")
    process_names = BROWSER_AX_PROCESS_NAMES.get(browser_type, [])
    candidates = {browser_type.lower(), app_name.lower(), plain_name.lower(), *(name.lower() for name in process_names)}

    for getter in (
        lambda: running_app.localizedName() or "",
        lambda: running_app.bundleIdentifier() or "",
        lambda: (running_app.executableURL().lastPathComponent() if running_app.executableURL() else "") or "",
    ):
        try:
            value = getter().strip().lower()
        except Exception:
            continue
        if not value:
            continue
        if value in candidates:
            return True
        if any(candidate and candidate in value for candidate in candidates):
            return True
    return False


def _get_running_app(browser_type: str):
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    front_app = workspace.frontmostApplication()
    if front_app is not None and _match_browser_app(front_app, browser_type):
        return front_app

    for running_app in workspace.runningApplications() or []:
        if _match_browser_app(running_app, browser_type):
            return running_app

    target_names = {name.lower() for name in BROWSER_AX_PROCESS_NAMES.get(browser_type, [])}
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            proc_name = (proc.info.get("name", "") or "").strip()
            if not proc_name:
                continue
            proc_name_lower = proc_name.lower()
            if proc_name_lower not in target_names and not any(name in proc_name_lower for name in target_names):
                continue
            return AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(int(proc.info["pid"]))
        except Exception:
            continue
    return None


def _get_main_window(app_element: Any):
    main_window = _ax_attr(app_element, "AXMainWindow") or _ax_attr(app_element, "AXFocusedWindow")
    if main_window is not None:
        return main_window

    windows = _ax_attr(app_element, "AXWindows") or []
    if not windows:
        return None

    for window in windows:
        minimized = _ax_attr(window, "AXMinimized")
        if minimized is False:
            return window
    return windows[0]


def _get_pid(element: Any) -> int:
    try:
        pid = ctypes.c_int(0)
        AXUIElementGetPid(element, ctypes.byref(pid))
        return int(pid.value)
    except Exception:
        return 0


def _activate_browser_app(pid: int):
    if pid <= 0:
        return
    for running_app in AppKit.NSWorkspace.sharedWorkspace().runningApplications() or []:
        try:
            if int(running_app.processIdentifier()) != pid:
                continue
        except Exception:
            continue
        running_app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
        return


def _walk_children(node: Any, depth: int = 0, max_depth: int = 20):
    if node is None or depth > max_depth:
        return
    yield node, depth
    for child in _ax_attr(node, "AXChildren") or []:
        yield from _walk_children(child, depth + 1, max_depth)


def _find_descendant(node: Any, predicate, max_depth: int = 20):
    for child, _depth in _walk_children(node, max_depth=max_depth):
        if predicate(child):
            return child
    return None


def _find_descendants(node: Any, predicate, max_depth: int = 20):
    results = []
    for child, _depth in _walk_children(node, max_depth=max_depth):
        if predicate(child):
            results.append(child)
    return results


def _get_sheet(window: Any):
    for child in _ax_attr(window, "AXChildren") or []:
        if (_ax_attr(child, "AXRole") or "") == "AXSheet":
            return child
    return None


def _ax_text(element: Any) -> str:
    return (_ax_attr(element, "AXTitle") or _ax_attr(element, "AXDescription") or _ax_attr(element, "AXLabel") or "").strip()


def _ax_value_text(element: Any) -> str:
    value = _ax_attr(element, "AXValue")
    return value.strip() if isinstance(value, str) else ""


def _has_web_content(window: Any) -> bool:
    for node, _depth in _walk_children(window):
        role = _ax_attr(node, "AXRole") or ""
        if role == "AXWebArea":
            return True
        dom_class = _ax_attr(node, "AXDOMClassList") or []
        if "BrowserView" in dom_class or "View" in dom_class:
            return True
    return False


class BrowserCore:
    @staticmethod
    def get_browser_path(browser_type: str) -> str:
        app_name = BROWSER_MAC_APP_NAME.get(browser_type, "")
        if not app_name:
            return ""

        from astronverse.software.software import Software

        return Software.get_app_path(app_name)

    @staticmethod
    def browser_top_and_max(control):
        pid = _get_pid(control)
        _activate_browser_app(pid)
        _ax_set(control, "AXMain", True)
        _ax_set(control, "AXFocused", True)
        _ax_perform(control, "AXRaise")

        # zoom_button = _ax_attr(control, "AXZoomButton")
        # if zoom_button is not None:
        #     _ax_perform(zoom_button, "AXPress")
        # else:
        #     _ax_set(control, "AXMinimized", False)

    @staticmethod
    def get_browser_point(browser_type: str) -> Any:
        base_ctrl = BrowserCore.get_browser_control(browser_type)
        if not base_ctrl:
            return None

        for node, _depth in _walk_children(base_ctrl):
            role = _ax_attr(node, "AXRole") or ""
            if role == "AXWebArea":
                position = _ax_attr(node, "AXPosition")
                point = _ax_unpack_point(position) if position is not None else None
                if point:
                    left, top = point
                    return top, left

            dom_class = _ax_attr(node, "AXDOMClassList") or []
            if "View" in dom_class:
                position = _ax_attr(node, "AXPosition")
                point = _ax_unpack_point(position) if position is not None else None
                if point:
                    left, top = point
                    return top, left
        return None

    @staticmethod
    def get_browser_control(browser_type: str) -> Any:
        running_app = _get_running_app(browser_type)
        if running_app is None:
            return None

        app_element = AXUIElementCreateApplication(int(running_app.processIdentifier()))
        main_window = _get_main_window(app_element)
        if main_window is not None and _has_web_content(main_window):
            return main_window

        windows = _ax_attr(app_element, "AXWindows") or []
        for window in windows:
            if _has_web_content(window):
                return window

        return main_window

    @staticmethod
    def download_window_operate(**kwargs) -> Any:
        file_name = kwargs.get("file_name", "")
        save_path = kwargs.get("save_path", "")
        custom_flag = kwargs.get("custom_flag")
        is_wait = kwargs.get("is_wait")
        time_out = kwargs.get("time_out")

        browser_type = kwargs.get("browser_type")
        browser_type = browser_type.value if hasattr(browser_type, "value") else browser_type

        dialog = None
        start_time = time.time()
        while time.time() - start_time < 10:
            control = BrowserCore.get_browser_control(browser_type)
            if control is not None:
                dialog = _get_sheet(control)
                if dialog is not None:
                    break
            time.sleep(0.2)

        if dialog is None:
            raise BizException(DOWNLOAD_WINDOW_NO_FIND, "未弹出下载窗口")

        text_fields = _find_descendants(
            dialog,
            lambda element: (_ax_attr(element, "AXRole") or "") == "AXTextField",
        )
        if not text_fields:
            raise BizException(DOWNLOAD_WINDOW_NO_FIND, "未找到下载窗口中的文件名输入框")

        text_field = None
        for candidate in text_fields:
            subrole = (_ax_attr(candidate, "AXSubrole") or "").strip()
            role_desc = (_ax_attr(candidate, "AXRoleDescription") or "").strip()
            value_text = _ax_value_text(candidate)
            if subrole == "AXSearchField" or role_desc == "search field":
                continue
            if value_text:
                text_field = candidate
                break

        if text_field is None:
            for candidate in text_fields:
                subrole = (_ax_attr(candidate, "AXSubrole") or "").strip()
                role_desc = (_ax_attr(candidate, "AXRoleDescription") or "").strip()
                if subrole == "AXSearchField" or role_desc == "search field":
                    continue
                text_field = candidate
                break

        if text_field is None:
            text_field = text_fields[0]

        original_name = _ax_value_text(text_field)
        if not original_name:
            original_name = file_name or ""

        if custom_flag and file_name:
            target_name = file_name
        else:
            target_name = original_name

        if not target_name:
            raise BizException(DOWNLOAD_WINDOW_NO_FIND, "无法确定下载文件名")

        dest_path = os.path.join(save_path, target_name) if save_path else target_name

        from astronverse.input.code.clipboard import Clipboard
        from astronverse.input.code.keyboard import Keyboard

        _ax_set(text_field, "AXFocused", True)
        _ax_perform(text_field, "AXPress")
        time.sleep(0.2)

        Keyboard.hotkey("command", "a")
        time.sleep(0.1)
        Keyboard.press("backspace")
        time.sleep(0.2)

        if save_path:
            Clipboard.copy(os.path.abspath(save_path))
            time.sleep(0.2)
            Keyboard.hotkey("command", "v")
            time.sleep(0.6)

        Keyboard.hotkey("command", "a")
        time.sleep(0.1)
        Keyboard.press("backspace")
        time.sleep(0.2)

        Clipboard.copy(target_name)
        time.sleep(0.2)
        Keyboard.hotkey("command", "v")
        time.sleep(0.3)

        save_button = None
        button_deadline = time.time() + 10
        while time.time() < button_deadline:
            save_button = _find_descendant(
                dialog,
                lambda element: (_ax_attr(element, "AXRole") or "") == "AXButton" and _ax_text(element) == "保存",
            )
            if save_button is not None:
                enabled = _ax_attr(save_button, "AXEnabled")
                if enabled in (True, 1):
                    break
            time.sleep(0.2)

        if save_button is None:
            raise BizException(DOWNLOAD_WINDOW_NO_FIND, "未找到下载窗口中的保存按钮")

        if not _ax_perform(save_button, "AXPress"):
            raise BizException(DOWNLOAD_WINDOW_NO_FIND, "下载窗口中的保存按钮点击失败")

        if is_wait:
            if not (time_out == 0 or time_out == ""):
                try:
                    wait_time_download = int(time_out)
                except Exception:
                    wait_time_download = 60
                while wait_time_download > 0:
                    wait_time_download -= 3
                    if os.path.exists(dest_path):
                        break
                    time.sleep(3)
                if wait_time_download <= 0 and not os.path.exists(dest_path):
                    raise BizException(DOWNLOAD_TIMEOUT, "等待下载完成超时")

        return dest_path

    @staticmethod
    def upload_window_operate(**kwargs) -> Any:
        upload_path = kwargs.get("upload_path", "")
        if isinstance(upload_path, list) or (isinstance(upload_path, str) and "|" in upload_path):
            raise NotImplementedError("macOS upload dialog automation currently supports only a single file")

        if not upload_path:
            return ""

        browser_type = kwargs.get("browser_type")
        browser_type = browser_type.value if hasattr(browser_type, "value") else browser_type

        dialog = None
        start_time = time.time()
        while time.time() - start_time < 10:
            control = BrowserCore.get_browser_control(browser_type)
            if control is not None:
                dialog = _get_sheet(control)
                if dialog is not None:
                    break
            time.sleep(0.2)

        if dialog is None:
            raise BizException(UPLOAD_WINDOW_NO_FIND, "未弹出上传窗口")

        from astronverse.input.code.clipboard import Clipboard
        from astronverse.input.code.keyboard import Keyboard

        normalized_path = os.path.abspath(upload_path)

        Keyboard.hotkey("command", "shift", "g")
        time.sleep(0.5)
        Clipboard.copy(normalized_path)
        time.sleep(0.2)
        Keyboard.hotkey("command", "v")
        time.sleep(0.2)
        Keyboard.press("enter")
        time.sleep(0.8)

        open_button = None
        button_deadline = time.time() + 10
        while time.time() < button_deadline:
            open_button = _find_descendant(
                dialog,
                lambda element: (_ax_attr(element, "AXRole") or "") == "AXButton"
                and (_ax_attr(element, "AXTitle") or _ax_attr(element, "AXDescription") or _ax_attr(element, "AXLabel") or "")
                == "打开",
            )
            if open_button is not None:
                enabled = _ax_attr(open_button, "AXEnabled")
                if enabled in (True, 1):
                    break
            time.sleep(0.2)

        if open_button is None:
            raise BizException(UPLOAD_WINDOW_NO_FIND, "未找到上传窗口中的打开按钮")

        if not _ax_perform(open_button, "AXPress"):
            raise BizException(UPLOAD_WINDOW_NO_FIND, "上传窗口中的打开按钮点击失败")

        return normalized_path
