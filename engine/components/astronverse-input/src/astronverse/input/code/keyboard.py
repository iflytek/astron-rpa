import os
import subprocess
import sys
import time

import pyautogui
from astronverse.baseline.logger.logger import logger
from pynput.keyboard import Controller

if sys.platform == "darwin":
    import AppKit
    import Quartz
    from ApplicationServices import (
        AXUIElementCopyAttributeValue,
        AXUIElementCopyElementAtPosition,
        AXUIElementCreateSystemWide,
        AXUIElementGetPid,
        kAXErrorSuccess,
    )
else:
    AppKit = None
    Quartz = None
    AXUIElementCopyAttributeValue = None
    AXUIElementCopyElementAtPosition = None
    AXUIElementCreateSystemWide = None
    AXUIElementGetPid = None
    kAXErrorSuccess = None


_DARWIN_ACTIVE_MODIFIERS: set[str] = set()
_DARWIN_MODIFIER_FLAGS = (
    {
        "command": Quartz.kCGEventFlagMaskCommand,
        "ctrl": Quartz.kCGEventFlagMaskControl,
        "control": Quartz.kCGEventFlagMaskControl,
        "alt": Quartz.kCGEventFlagMaskAlternate,
        "option": Quartz.kCGEventFlagMaskAlternate,
        "shift": Quartz.kCGEventFlagMaskShift,
    }
    if Quartz is not None
    else {}
)
_DARWIN_KEYCODES = {
    "a": 0,
    "s": 1,
    "d": 2,
    "f": 3,
    "h": 4,
    "g": 5,
    "z": 6,
    "x": 7,
    "c": 8,
    "v": 9,
    "b": 11,
    "q": 12,
    "w": 13,
    "e": 14,
    "r": 15,
    "y": 16,
    "t": 17,
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "6": 22,
    "5": 23,
    "=": 24,
    "9": 25,
    "7": 26,
    "-": 27,
    "8": 28,
    "0": 29,
    "]": 30,
    "o": 31,
    "u": 32,
    "[": 33,
    "i": 34,
    "p": 35,
    "l": 37,
    "j": 38,
    "'": 39,
    "k": 40,
    ";": 41,
    "\\": 42,
    ",": 43,
    "/": 44,
    "n": 45,
    "m": 46,
    ".": 47,
    "tab": 48,
    "space": 49,
    "`": 50,
    "backspace": 51,
    "enter": 36,
    "return": 36,
    "esc": 53,
    "escape": 53,
    "command": 55,
    "shift": 56,
    "capslock": 57,
    "option": 58,
    "alt": 58,
    "ctrl": 59,
    "control": 59,
    "rightshift": 60,
    "rightoption": 61,
    "rightctrl": 62,
    "function": 63,
    "f17": 64,
    "volumeup": 72,
    "volumedown": 73,
    "mute": 74,
    "f18": 79,
    "f19": 80,
    "f20": 90,
    "f5": 96,
    "f6": 97,
    "f7": 98,
    "f3": 99,
    "f8": 100,
    "f9": 101,
    "f11": 103,
    "f13": 105,
    "f16": 106,
    "f14": 107,
    "f10": 109,
    "f12": 111,
    "f15": 113,
    "help": 114,
    "home": 115,
    "pageup": 116,
    "delete": 117,
    "f4": 118,
    "end": 119,
    "f2": 120,
    "pagedown": 121,
    "f1": 122,
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
}
_DARWIN_FLAGS_CHANGED_KEYCODES = {
    "command": 55,
    "shift": 56,
    "capslock": 57,
    "option": 58,
    "alt": 58,
    "ctrl": 59,
    "control": 59,
    "rightshift": 60,
    "rightoption": 61,
    "rightctrl": 62,
}
_DARWIN_EVENT_TAP = Quartz.kCGAnnotatedSessionEventTap if Quartz is not None else None

def _darwin_ax_attr(element, attr_name: str):
    if AXUIElementCopyAttributeValue is None:
        return None
    try:
        err, value = AXUIElementCopyAttributeValue(element, attr_name, None)
        if err == kAXErrorSuccess:
            return value
    except Exception:
        return None
    return None


def _darwin_ax_pid(element) -> int:
    if AXUIElementGetPid is None:
        return 0
    try:
        result = AXUIElementGetPid(element, None)
        if isinstance(result, (tuple, list)) and len(result) == 2:
            err, pid = result
            if err == kAXErrorSuccess and isinstance(pid, int) and pid > 1:
                return pid
    except Exception:
        pass
    try:
        import ctypes
        pid = ctypes.c_int32(0)
        err = AXUIElementGetPid(element, ctypes.byref(pid))
        if err == kAXErrorSuccess and pid.value > 1:
            return pid.value
    except Exception:
        pass
    return 0


def _darwin_pid_from_ax_element(element) -> int:
    cur = element
    visited = 0
    while cur is not None and visited < 64:
        visited += 1
        role = _darwin_ax_attr(cur, "AXRole")
        if role == "AXApplication":
            pid = _darwin_ax_pid(cur)
            if pid > 1:
                return pid
            break
        parent = _darwin_ax_attr(cur, "AXParent")
        if parent is None:
            break
        cur = parent
    return _darwin_ax_pid(element)



class Keyboard:
    def __init__(self):
        pyautogui.FAILSAFE = False

    @staticmethod
    def platform() -> str:
        return sys.platform

    @staticmethod
    def change_language(language: int):
        if sys.platform == "win32":
            import win32api
            import win32gui
            from win32con import WM_INPUTLANGCHANGEREQUEST

            hwnd = win32gui.GetForegroundWindow()
            win32api.SendMessage(hwnd, WM_INPUTLANGCHANGEREQUEST, 0, language)
            return

        if sys.platform.startswith("linux"):
            try:
                result = subprocess.run(
                    ["fcitx-remote"],
                    timeout=5,
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding="utf-8",
                    errors="replace",
                )
                if result.returncode != 0:
                    logger.info("Unable to query fcitx status.")
                    return

                current_status = int(result.stdout.strip())
                if language == 0x0409:
                    expected_status = 1
                elif language == 0x0804:
                    expected_status = 2
                else:
                    logger.info(f"Unsupported language code: {hex(language)}")
                    return

                if current_status != expected_status:
                    subprocess.run(
                        ["fcitx-remote", "-t"],
                        timeout=5,
                        check=False,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            except Exception as exc:
                logger.info(f"Failed to switch input method: {exc}")
            return

        logger.info("Input method switching is not implemented on this platform yet.")

    @staticmethod
    def _normalize_key(key: str) -> str:
        normalized = key.lower().strip()
        if normalized.startswith("command"):
            normalized = "command"
        aliases = {
            "win": "command",
            "super": "command",
            "cmd": "command",
            "control": "ctrl",
            "option": "alt",
            "arrowleft": "left",
            "arrowright": "right",
            "arrowup": "up",
            "arrowdown": "down",
        }
        normalized = aliases.get(normalized, normalized)
        if sys.platform == "darwin" and normalized == "alt":
            return "option"
        return normalized

    @staticmethod
    def _is_darwin_native_available() -> bool:
        return sys.platform == "darwin" and Quartz is not None

    @staticmethod
    def _darwin_flags() -> int:
        flags = 0
        for key in _DARWIN_ACTIVE_MODIFIERS:
            flags |= _DARWIN_MODIFIER_FLAGS.get(key, 0)
        return flags

    @staticmethod
    def _darwin_keycode(key: str):
        return _DARWIN_KEYCODES.get(Keyboard._normalize_key(key))

    @staticmethod
    def _darwin_is_modifier(key: str) -> bool:
        normalized = Keyboard._normalize_key(key)
        return normalized in _DARWIN_MODIFIER_FLAGS

    @staticmethod
    def _darwin_post_keycode(keycode: int, is_down: bool, flags: int | None = None):
        event = Quartz.CGEventCreateKeyboardEvent(None, keycode, is_down)
        if flags is None:
            flags = Keyboard._darwin_flags()
        Quartz.CGEventSetFlags(event, flags)
        Quartz.CGEventPost(_DARWIN_EVENT_TAP, event)

    @staticmethod
    def _darwin_post_modifier(key: str, is_down: bool):
        normalized = Keyboard._normalize_key(key)
        keycode = _DARWIN_FLAGS_CHANGED_KEYCODES.get(normalized)
        if keycode is None:
            raise ValueError(f"Unsupported macOS modifier key: {normalized}")

        event = Quartz.CGEventCreateKeyboardEvent(None, keycode, is_down)
        Quartz.CGEventSetType(event, Quartz.kCGEventFlagsChanged)
        Quartz.CGEventSetFlags(event, Keyboard._darwin_flags())
        Quartz.CGEventPost(_DARWIN_EVENT_TAP, event)

    @staticmethod
    def _darwin_post_unicode(text: str, is_down: bool):
        event = Quartz.CGEventCreateKeyboardEvent(None, 0, is_down)
        Quartz.CGEventSetFlags(event, Keyboard._darwin_flags())
        Quartz.CGEventKeyboardSetUnicodeString(event, len(text), text)
        Quartz.CGEventPost(_DARWIN_EVENT_TAP, event)

    @staticmethod
    def _darwin_pid_at_cursor() -> int:
        if not Keyboard._is_darwin_native_available():
            return 0
        try:
            loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
            logger.info(f"[mouse-diag] Keyboard._darwin_pid_at_cursor loc=({int(loc.x)}, {int(loc.y)})")
            x, y = int(loc.x), int(loc.y)

            if AXUIElementCreateSystemWide is not None and AXUIElementCopyElementAtPosition is not None:
                try:
                    sys_el = AXUIElementCreateSystemWide()
                    err, el = AXUIElementCopyElementAtPosition(sys_el, float(x), float(y), None)
                    if err == kAXErrorSuccess and el is not None:
                        pid = _darwin_pid_from_ax_element(el)
                        if pid > 1:
                            logger.info(f"[mouse-diag] Keyboard._darwin_pid_at_cursor ax pid={pid}")
                            return pid
                except Exception as e:
                    logger.info(f"[mouse-diag] Keyboard._darwin_pid_at_cursor ax error={e}")

            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
                Quartz.kCGNullWindowID,
            )
            for window in window_list or []:
                layer = int(window.get("kCGWindowLayer", 999))
                if layer >= 20:
                    continue
                owner_name = str(window.get("kCGWindowOwnerName", "") or "")
                if owner_name in {"程序坞", "Dock", "控制中心", "SystemUIServer"}:
                    continue
                bounds = window.get("kCGWindowBounds", {})
                wx = int(bounds.get("X", 0))
                wy = int(bounds.get("Y", 0))
                ww = int(bounds.get("Width", 0))
                wh = int(bounds.get("Height", 0))
                if wx <= x <= wx + ww and wy <= y <= wy + wh:
                    pid = int(window.get("kCGWindowOwnerPID", 0))
                    if pid > 1:
                        logger.info(f"[mouse-diag] Keyboard._darwin_pid_at_cursor quartz pid={pid} owner={owner_name} bounds=({wx},{wy},{ww},{wh}) layer={layer}")
                        return pid
        except Exception as e:
            logger.info(f"[mouse-diag] Keyboard._darwin_pid_at_cursor error={e}")
            return 0
        return 0

    @staticmethod
    def _darwin_activate_target_app():
        if AppKit is None:
            logger.info('[mouse-diag] Keyboard._darwin_activate_target_app AppKit unavailable')
            return
        pid = Keyboard._darwin_pid_at_cursor()
        if pid <= 1:
            logger.info(f"[mouse-diag] Keyboard._darwin_activate_target_app invalid pid={pid}")
            return
        try:
            logger.info(f"[mouse-diag] Keyboard._darwin_activate_target_app pid={pid}")
            app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
            if app is not None:
                logger.info(f"[mouse-diag] Keyboard._darwin_activate_target_app app={app.localizedName() if hasattr(app, 'localizedName') else app}")
                app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
                time.sleep(0.12)
                logger.info('[mouse-diag] Keyboard._darwin_activate_target_app done')
        except Exception as e:
            logger.info(f"[mouse-diag] Keyboard._darwin_activate_target_app error={e}")
            return

    @staticmethod
    def _darwin_hotkey_applescript(modifiers: list[str], normal_keys: list[str]) -> bool:
        if "command" not in modifiers or len(normal_keys) != 1:
            return False

        key = normal_keys[0]
        if len(key) != 1:
            return False

        modifier_map = {
            "command": "command down",
            "shift": "shift down",
            "option": "option down",
            "alt": "option down",
            "ctrl": "control down",
            "control": "control down",
        }
        using_parts = [modifier_map[m] for m in modifiers if m in modifier_map]
        if not using_parts:
            return False

        script = f'tell application "System Events" to keystroke "{key}" using {{{", ".join(using_parts)}}}'
        try:
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            return False

    @staticmethod
    def paste_hotkey():
        if sys.platform == "darwin":
            return Keyboard.hotkey("command", "v")
        return Keyboard.hotkey("ctrl", "v")

    @staticmethod
    def write_char(char: str):
        return Keyboard.write_unicode(char)

    @staticmethod
    def write_unicode(text: str, delay: float = 0):
        if sys.platform == "win32":
            from astronverse.input.code.windows_input import type_text

            return type_text(text, delay=delay)

        if Keyboard._is_darwin_native_available():
            for char in str(text):
                Keyboard._darwin_post_unicode(char, True)
                Keyboard._darwin_post_unicode(char, False)
                if delay > 0:
                    time.sleep(delay)
            return None

        keyboard = Controller()
        return keyboard.type(text)

    @staticmethod
    def press(keys, presses: int = 1, interval: float = 0.0):
        if Keyboard._is_darwin_native_available():
            sequence = [keys] if isinstance(keys, str) else list(keys)
            for _ in range(presses):
                for key in sequence:
                    normalized = Keyboard._normalize_key(key)
                    Keyboard.key_down(normalized)
                    Keyboard.key_up(normalized)
                    if interval > 0:
                        time.sleep(interval)
            return None

        if isinstance(keys, str):
            keys = Keyboard._normalize_key(keys)
        elif isinstance(keys, list):
            keys = [Keyboard._normalize_key(key) for key in keys]
        return pyautogui.press(keys=keys, presses=presses, interval=interval)

    @staticmethod
    def hotkey(*args, **kwargs):
        if Keyboard._is_darwin_native_available():
            Keyboard._darwin_activate_target_app()
            interval = kwargs.get("interval", 0.0)
            normalized_keys = [Keyboard._normalize_key(arg) if isinstance(arg, str) else arg for arg in args]
            modifiers = [key for key in normalized_keys if isinstance(key, str) and Keyboard._darwin_is_modifier(key)]
            normal_keys = [key for key in normalized_keys if key not in modifiers]

            if Keyboard._darwin_hotkey_applescript(modifiers, normal_keys):
                return None

            for modifier in modifiers:
                Keyboard.key_down(modifier)
                if interval > 0:
                    time.sleep(interval)

            for key in normal_keys:
                Keyboard.key_down(key)
                if interval > 0:
                    time.sleep(interval)
                Keyboard.key_up(key)
                if interval > 0:
                    time.sleep(interval)

            for modifier in reversed(modifiers):
                Keyboard.key_up(modifier)
                if interval > 0:
                    time.sleep(interval)
            return None

        keys = [Keyboard._normalize_key(arg) if isinstance(arg, str) else arg for arg in args]
        return pyautogui.hotkey(*keys, **kwargs)

    @staticmethod
    def key_down(key):
        normalized = Keyboard._normalize_key(key)
        if Keyboard._is_darwin_native_available():
            Keyboard._darwin_activate_target_app()
            keycode = Keyboard._darwin_keycode(normalized)
            if keycode is None:
                if len(normalized) == 1:
                    return Keyboard.write_unicode(normalized)
                raise ValueError(f"Unsupported macOS key: {normalized}")

            if Keyboard._darwin_is_modifier(normalized):
                _DARWIN_ACTIVE_MODIFIERS.add(normalized)
                Keyboard._darwin_post_modifier(normalized, True)
                return None
            Keyboard._darwin_post_keycode(keycode, True)
            return None

        return pyautogui.keyDown(key=normalized)

    @staticmethod
    def key_up(key):
        normalized = Keyboard._normalize_key(key)
        if Keyboard._is_darwin_native_available():
            keycode = Keyboard._darwin_keycode(normalized)
            if keycode is None:
                if len(normalized) == 1:
                    return None
                raise ValueError(f"Unsupported macOS key: {normalized}")

            if Keyboard._darwin_is_modifier(normalized):
                _DARWIN_ACTIVE_MODIFIERS.discard(normalized)
                Keyboard._darwin_post_modifier(normalized, False)
                return None
            Keyboard._darwin_post_keycode(keycode, False)
            return None

        return pyautogui.keyUp(key=normalized)

    @staticmethod
    def get_drive_path():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        relative_dir = os.path.join("VK", "bin", "Debug", "VK.exe")
        drive_path = os.path.join(parent_dir, relative_dir)
        return drive_path
