"""Fail-closed environment checks for reviewed desktop workflows only.

This is not an input interceptor or sandbox. Polling cannot prevent every focus
race; administrators must review targets, input bindings and cleanup, and users
must reserve the interactive session for the workflow.
"""

import os
from pathlib import Path


class DesktopError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def probe():
    if os.name != "nt":
        raise DesktopError("DESKTOP_UNAVAILABLE")
    try:
        import ctypes
        from ctypes import wintypes

        import win32api
        import win32gui
        import win32process
        import win32ts

        session = win32ts.ProcessIdToSessionId(os.getpid())
        if (
            session == 0
            or win32ts.WTSQuerySessionInformation(None, session, win32ts.WTSConnectState) != win32ts.WTSActive
        ):
            raise DesktopError("DESKTOP_UNAVAILABLE")
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        user32.OpenInputDesktop.restype = wintypes.HANDLE
        user32.GetUserObjectInformationW.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        user32.CloseDesktop.argtypes = [wintypes.HANDLE]
        user32.GetLastActivePopup.argtypes = [wintypes.HWND]
        user32.GetLastActivePopup.restype = wintypes.HWND
        handle = user32.OpenInputDesktop(0, False, 1)  # DESKTOP_READOBJECTS
        if not handle:
            raise DesktopError("DESKTOP_LOCKED")
        try:
            name, required = ctypes.create_unicode_buffer(256), wintypes.DWORD()
            if not user32.GetUserObjectInformationW(handle, 2, name, ctypes.sizeof(name), ctypes.byref(required)):
                raise DesktopError("DESKTOP_UNAVAILABLE")
            if name.value.casefold() != "default":
                raise DesktopError("DESKTOP_LOCKED")
        finally:
            user32.CloseDesktop(handle)
        windows = []

        def collect(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            popup = user32.GetLastActivePopup(hwnd)
            windows.append(
                {
                    "title": title,
                    "pid": win32process.GetWindowThreadProcessId(hwnd)[1],
                    "popup": win32gui.GetWindowText(popup)
                    if popup != hwnd and win32gui.IsWindowVisible(popup)
                    else None,
                }
            )

        win32gui.EnumWindows(collect, None)
        # GetSystemMetrics is DPI-virtualized and can change when another
        # component enables DPI awareness. Display modes use physical pixels.
        display = win32api.EnumDisplaySettings(None, -1)
        return {
            "session": session,
            "resolution": {"width": display.PelsWidth, "height": display.PelsHeight},
            "windows": windows,
        }
    except DesktopError:
        raise
    except Exception:
        raise DesktopError("DESKTOP_UNAVAILABLE") from None


class DesktopGuard:
    def __init__(self, contract):
        self.contract = contract
        self.session = None
        try:
            if (
                type(contract["version"]) is not int
                or contract["version"] != 1
                or not isinstance(contract["resolution"], dict)
                or set(contract["resolution"]) != {"width", "height"}
                or any(type(v) is not int or not 320 <= v <= 16384 for v in contract["resolution"].values())
                or contract["humanMode"] not in ("none", "attended")
                or not isinstance(contract["programPaths"], dict)
                or not contract["programPaths"]
                or not isinstance(contract["programs"], list)
                or set(contract["programs"]) != set(contract["programPaths"])
                or not isinstance(contract["targets"], list)
                or not contract["targets"]
                or any(not isinstance(v, str) or not v for v in contract["targets"])
            ):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            raise DesktopError("DESKTOP_CONTRACT_INVALID") from None

    def check(self, *, initial=False):
        state = probe()
        if self.session is not None and state["session"] != self.session:
            raise DesktopError("DESKTOP_SESSION_CHANGED")
        if state["resolution"] != self.contract["resolution"]:
            raise DesktopError("DESKTOP_RESOLUTION_MISMATCH")
        if initial:
            for path in self.contract["programPaths"].values():
                if not isinstance(path, str) or not Path(path).is_file():
                    raise DesktopError("DESKTOP_SOFTWARE_UNAVAILABLE")
            self.session = state["session"]
        targets = self.contract["targets"]
        for window in state["windows"]:
            if window["title"] in targets and window["popup"] is not None and window["popup"] not in targets:
                raise DesktopError("DESKTOP_POPUP_BLOCKED")
