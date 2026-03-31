from dataclasses import dataclass
from typing import Any

import AppKit
import Quartz
from ApplicationServices import (
    AXUIElementCopyAttributeValue,
    AXUIElementCreateApplication,
    AXUIElementCreateSystemWide,
    AXUIElementPerformAction,
    AXUIElementSetAttributeValue,
    kAXErrorSuccess,
)
from astronverse.actionlib.types import WinPick
from astronverse.window import ControlInfo, WalkControlInfo, WindowSizeType
from astronverse.window.core import IUITreeCore, IWindowsCore
from astronverse.window.error import BizException, WINDOW_NO_FIND, WINDOW_SIZE_ERROR


@dataclass
class MacWindowHandle:
    pid: int
    window: Any


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


def _window_title(window: Any) -> str:
    return _ax_attr(window, "AXTitle") or ""


def _window_classname(window: Any) -> str:
    return _ax_attr(window, "AXSubrole") or _ax_attr(window, "AXRole") or ""


def _window_position(window: Any):
    position = _ax_attr(window, "AXPosition")
    size = _ax_attr(window, "AXSize")
    if position is None or size is None:
        return (0, 0, 0, 0)

    try:
        pos_ok, pos = Quartz.AXValueGetValue(position, Quartz.kAXValueCGPointType, None)
        size_ok, win_size = Quartz.AXValueGetValue(size, Quartz.kAXValueCGSizeType, None)
        if pos_ok and size_ok and pos is not None and win_size is not None:
            return (int(pos.x), int(pos.y), int(win_size.width), int(win_size.height))
    except Exception:
        pass
    return (0, 0, 0, 0)


def _match_string(expected: str, actual: str) -> bool:
    if not expected:
        return True
    return expected == actual


def _pick_window_name(pick: WinPick) -> str:
    path = pick.get("elementData", {}).get("path", [])
    if not path:
        return pick.get("name", "")
    return path[0].get("name", "")


def _pick_window_class(pick: WinPick) -> str:
    path = pick.get("elementData", {}).get("path", [])
    if not path:
        return pick.get("cls", "")
    return path[0].get("cls", "")


def _pick_app_name(pick: WinPick) -> str:
    return pick.get("elementData", {}).get("app", "") or pick.get("app", "")


def _iter_running_apps():
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    for app in workspace.runningApplications() or []:
        try:
            pid = int(app.processIdentifier())
        except Exception:
            continue
        if pid <= 1:
            continue
        yield app, pid


def _iter_app_windows(pid: int):
    app_ref = AXUIElementCreateApplication(pid)
    windows = _ax_attr(app_ref, "AXWindows") or []
    for window in windows:
        yield window


def _match_app_name(running_app: Any, pick_app_name: str) -> bool:
    if not pick_app_name:
        return True

    candidates = []
    try:
        candidates.append(running_app.localizedName() or "")
    except Exception:
        pass
    try:
        candidates.append(running_app.bundleIdentifier() or "")
    except Exception:
        pass
    try:
        executable_url = running_app.executableURL()
        if executable_url is not None:
            candidates.append(executable_url.lastPathComponent() or "")
    except Exception:
        pass

    return any(candidate == pick_app_name for candidate in candidates if candidate)


def _candidate_windows_from_pick(pick: WinPick):
    pick_name = _pick_window_name(pick)
    pick_class = _pick_window_class(pick)
    pick_app_name = _pick_app_name(pick)

    for running_app, pid in _iter_running_apps():
        if not _match_app_name(running_app, pick_app_name):
            continue
        for window in _iter_app_windows(pid):
            window_name = _window_title(window)
            window_class = _window_classname(window)
            if not _match_string(pick_name, window_name):
                continue
            if not _match_string(pick_class, window_class):
                continue
            yield MacWindowHandle(pid=pid, window=window)


def _activate_pid(pid: int):
    for running_app, app_pid in _iter_running_apps():
        if app_pid != pid:
            continue
        running_app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
        return


def _set_window_size(window: Any, width: int, height: int):
    try:
        current_size = _ax_attr(window, "AXSize")
        if current_size is None:
            raise BizException(WINDOW_SIZE_ERROR, "目标窗口无法设置到指定大小")

        mutable_size = Quartz.CGSize(width, height)
        ax_value = Quartz.AXValueCreate(Quartz.kAXValueCGSizeType, mutable_size)
        if not _ax_set(window, "AXSize", ax_value):
            raise BizException(WINDOW_SIZE_ERROR, "目标窗口无法设置到指定大小")
    except BizException:
        raise
    except Exception as exc:
        raise BizException(WINDOW_SIZE_ERROR, f"目标窗口无法设置到指定大小: {exc}") from exc


class WindowsCore(IWindowsCore):
    @staticmethod
    def toControl(handler: Any) -> Any:
        if isinstance(handler, MacWindowHandle):
            return handler.window
        return handler

    @staticmethod
    def find(pick: WinPick) -> Any:
        for handler in _candidate_windows_from_pick(pick):
            return handler
        raise BizException(WINDOW_NO_FIND, "未找到目标窗口{}".format(pick))

    @staticmethod
    def info(handler: Any) -> ControlInfo:
        if not isinstance(handler, MacWindowHandle):
            raise BizException(WINDOW_NO_FIND, "未找到目标窗口")

        return ControlInfo(
            name=_window_title(handler.window),
            classname=_window_classname(handler.window),
            position=_window_position(handler.window),
            handler=handler,
        )

    @staticmethod
    def top(handler: Any):
        if not isinstance(handler, MacWindowHandle):
            raise BizException(WINDOW_NO_FIND, "未找到目标窗口")

        _activate_pid(handler.pid)
        _ax_set(handler.window, "AXMain", True)
        _ax_set(handler.window, "AXFocused", True)
        _ax_perform(handler.window, "AXRaise")

    @staticmethod
    def close(handler: Any):
        if not isinstance(handler, MacWindowHandle):
            raise BizException(WINDOW_NO_FIND, "未找到目标窗口")

        close_button = _ax_attr(handler.window, "AXCloseButton")
        if close_button is not None and _ax_perform(close_button, "AXPress"):
            return
        _ax_perform(handler.window, "AXClose")

    @staticmethod
    def size(
        handler: Any,
        size_type: WindowSizeType = WindowSizeType.MAX,
        width: int = 0,
        height: int = 0,
    ):
        if not isinstance(handler, MacWindowHandle):
            raise BizException(WINDOW_NO_FIND, "未找到目标窗口")

        if size_type == WindowSizeType.CUSTOM:
            _set_window_size(handler.window, width, height)
            _ax_set(handler.window, "AXMinimized", False)
            return

        if size_type == WindowSizeType.MAX:
            zoom_button = _ax_attr(handler.window, "AXZoomButton")
            if zoom_button is not None:
                _ax_perform(zoom_button, "AXPress")
                return
            _ax_set(handler.window, "AXMinimized", False)
            return

        if size_type == WindowSizeType.MIN:
            _ax_set(handler.window, "AXMinimized", True)


class UITreeCore(IUITreeCore):
    @staticmethod
    def GetRootControl() -> Any:
        return AXUIElementCreateSystemWide()

    @staticmethod
    def WalkControl(control: Any, includeTop: bool = False, maxDepth: int = 0xFFFFFFFF):
        def _walk(node: Any, depth: int):
            if includeTop or depth > 0:
                yield WalkControlInfo(
                    name=_ax_attr(node, "AXTitle") or _ax_attr(node, "AXLabel") or "",
                    classname=_ax_attr(node, "AXRole") or "",
                    position=_window_position(node),
                    control_type=_ax_attr(node, "AXRole"),
                    control_type_name=_ax_attr(node, "AXRoleDescription") or "",
                    control=node,
                    depth=depth,
                    automation_id=_ax_attr(node, "AXIdentifier") or "",
                )
            if depth >= maxDepth:
                return
            for child in _ax_attr(node, "AXChildren") or []:
                yield from _walk(child, depth + 1)

        yield from _walk(control, 0)

    @staticmethod
    def toHandler(control) -> Any:
        return control

    @staticmethod
    def setAction(control) -> bool:
        return _ax_perform(control, "AXRaise") or _ax_perform(control, "AXPress")
