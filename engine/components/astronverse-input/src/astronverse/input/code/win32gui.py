"""win32gui 窗口操作相关"""

from typing import Any

import win32com.client
import win32con
import win32gui
from astronverse.actionlib.types import WinPick
from astronverse.input.code import ControlInfo

WINDOW_SHADOW_OFFSET = 9  # 阴影宽度


def window_find(pick: WinPick) -> Any:
    """
    _find 查找 handle
    """
    wnd_name = pick.get("elementData", {}).get("path", [])[0].get("name", "")
    wnd_class_name = pick.get("elementData", {}).get("path", [])[0].get("cls", "")

    window_handle = win32gui.FindWindow(wnd_class_name, wnd_name)
    if not window_handle:
        window_handle = win32gui.FindWindowEx(None, None, None, wnd_name)
        if not window_handle:
            raise Exception("未找到目标窗口{}".format(pick))
    return window_handle


def window_info(handler: Any) -> ControlInfo:
    """
    info 查询信息
    """
    window_rect = win32gui.GetWindowRect(handler)
    # 计算去除阴影的窗口位置
    position = (
        window_rect[0] + WINDOW_SHADOW_OFFSET,
        window_rect[1] + WINDOW_SHADOW_OFFSET,
        window_rect[2] - WINDOW_SHADOW_OFFSET,
        window_rect[3] - WINDOW_SHADOW_OFFSET,
    )
    return ControlInfo(
        name=win32gui.GetWindowText(handler),
        classname=win32gui.GetWindowText(handler),
        position=position,
        client_position=win32gui.GetClientRect(handler),
        handler=handler,
    )


def window_top(handler):
    """置顶窗口"""
    if win32gui.IsIconic(handler):
        win32gui.ShowWindow(handler, win32con.SW_NORMAL)
    else:
        # 结合键盘事件
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")
        win32gui.SetForegroundWindow(handler)
