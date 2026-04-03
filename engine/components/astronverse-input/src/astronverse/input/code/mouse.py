import random
import sys
import time

import pyautogui
from astronverse.input import Speed

if sys.platform == "darwin":
    import AppKit
    import Quartz
else:
    AppKit = None
    Quartz = None


speed_to_int = {Speed.SLOW: 0.5, Speed.NORMAL: 1, Speed.FAST: 2}
_DARWIN_ACTIVE_BUTTON: str | None = None
_DARWIN_MOUSE_EVENT_TAP = Quartz.kCGHIDEventTap if Quartz is not None else None


class Mouse:
    def __int__(self):
        pyautogui.FAILSAFE = False

    @staticmethod
    def _is_darwin_native_available() -> bool:
        return sys.platform == "darwin" and Quartz is not None

    @staticmethod
    def _current_position() -> tuple[int, int]:
        if Mouse._is_darwin_native_available():
            loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
            return int(loc.x), int(loc.y)
        point = pyautogui.position()
        return point.x, point.y

    @staticmethod
    def _normalize_point(x=None, y=None) -> tuple[int, int]:
        current_x, current_y = Mouse._current_position()
        return int(current_x if x is None else x), int(current_y if y is None else y)

    @staticmethod
    def _mouse_event_spec(button: str):
        normalized = (button or "left").lower()
        if normalized == "primary":
            normalized = "left"
        elif normalized == "secondary":
            normalized = "right"
        if normalized == "right":
            return (
                Quartz.kCGMouseButtonRight,
                Quartz.kCGEventRightMouseDown,
                Quartz.kCGEventRightMouseUp,
                Quartz.kCGEventRightMouseDragged,
            )
        if normalized == "middle":
            return (
                Quartz.kCGMouseButtonCenter,
                Quartz.kCGEventOtherMouseDown,
                Quartz.kCGEventOtherMouseUp,
                Quartz.kCGEventOtherMouseDragged,
            )
        return (
            Quartz.kCGMouseButtonLeft,
            Quartz.kCGEventLeftMouseDown,
            Quartz.kCGEventLeftMouseUp,
            Quartz.kCGEventLeftMouseDragged,
        )

    @staticmethod
    def _post_mouse_event(event_type, x: int, y: int, button_code):
        source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateCombinedSessionState)
        event = Quartz.CGEventCreateMouseEvent(source, event_type, (x, y), button_code)
        if event_type in {
            Quartz.kCGEventLeftMouseDown,
            Quartz.kCGEventLeftMouseUp,
            Quartz.kCGEventRightMouseDown,
            Quartz.kCGEventRightMouseUp,
            Quartz.kCGEventOtherMouseDown,
            Quartz.kCGEventOtherMouseUp,
        }:
            Quartz.CGEventSetIntegerValueField(event, Quartz.kCGMouseEventClickState, 1)
        Quartz.CGEventPost(_DARWIN_MOUSE_EVENT_TAP, event)

    @staticmethod
    def _darwin_pid_at_point(x: int, y: int) -> int:
        if not Mouse._is_darwin_native_available():
            return 0
        try:
            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
                Quartz.kCGNullWindowID,
            )
            for window in window_list or []:
                layer = int(window.get("kCGWindowLayer", 999))
                if layer >= 25:
                    continue
                bounds = window.get("kCGWindowBounds", {})
                wx = int(bounds.get("X", 0))
                wy = int(bounds.get("Y", 0))
                ww = int(bounds.get("Width", 0))
                wh = int(bounds.get("Height", 0))
                if wx <= x <= wx + ww and wy <= y <= wy + wh:
                    pid = int(window.get("kCGWindowOwnerPID", 0))
                    if pid > 1:
                        return pid
        except Exception:
            return 0
        return 0

    @staticmethod
    def _darwin_activate_pid(pid: int):
        if AppKit is None or pid <= 1:
            return
        try:
            app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
            if app is not None:
                app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
        except Exception:
            return

    @staticmethod
    def _darwin_activate_app_at_point(x: int, y: int):
        pid = Mouse._darwin_pid_at_point(x, y)
        if pid > 1:
            Mouse._darwin_activate_pid(pid)
            time.sleep(0.12)

    @staticmethod
    def calculate_movement_duration(start_x: int, start_y: int, end_x: int, end_y: int, speed: Speed) -> float:
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        base_speed = 1000
        speed_multiplier = speed_to_int[speed]
        duration = distance / (base_speed * speed_multiplier)
        return max(0.1, duration)

    @staticmethod
    def position() -> tuple:
        return Mouse._current_position()

    @staticmethod
    def move(x=None, y=None, duration: float = 0.0, tween=pyautogui.linear) -> None:
        if not Mouse._is_darwin_native_available():
            return pyautogui.moveTo(x=x, y=y, duration=duration, tween=tween)

        target_x, target_y = Mouse._normalize_point(x, y)
        start_x, start_y = Mouse._current_position()
        event_type = Quartz.kCGEventMouseMoved
        button_code = Quartz.kCGMouseButtonLeft
        if _DARWIN_ACTIVE_BUTTON is not None:
            button_code, _, _, drag_event = Mouse._mouse_event_spec(_DARWIN_ACTIVE_BUTTON)
            event_type = drag_event
        if duration <= 0:
            Mouse._post_mouse_event(event_type, target_x, target_y, button_code)
            return None

        steps = max(1, int(duration / 0.01))
        for index in range(1, steps + 1):
            progress = index / steps
            next_x = int(start_x + (target_x - start_x) * progress)
            next_y = int(start_y + (target_y - start_y) * progress)
            Mouse._post_mouse_event(event_type, next_x, next_y, button_code)
            time.sleep(duration / steps)
        return None

    @staticmethod
    def move_simulate(x=None, y=None, duration: float = 0.0, tween=pyautogui.linear) -> None:
        start_x, start_y = Mouse.position()
        distance = ((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5

        if distance < 300:
            steps = 1
        elif distance < 800:
            steps = 2
        else:
            steps = 3

        interval = duration / steps if steps else 0
        ease_param = random.uniform(1.5, 2.5)
        time.sleep(random.uniform(0.02, 0.05))

        for i in range(steps):
            t = i / steps
            ease_t = t**ease_param / (t**ease_param + (1 - t) ** ease_param)
            new_x = start_x + (x - start_x) * ease_t
            new_y = start_y + (y - start_y) * ease_t
            if i < steps - 1:
                new_x += random.uniform(-1, 1)
                new_y += random.uniform(-1, 1)
            Mouse.move(new_x, new_y, duration=interval, tween=tween)

        Mouse.move(x=x, y=y)

    @staticmethod
    def click(
        x=None,
        y=None,
        clicks=1,
        interval=0.0,
        button=pyautogui.PRIMARY,
        duration=0.0,
        tween=pyautogui.linear,
    ) -> None:
        if x is None or y is None:
            pos = pyautogui.position()
            x, y = pos.x, pos.y
        if not Mouse._is_darwin_native_available():
            return pyautogui.click(
                x=x,
                y=y,
                clicks=clicks,
                interval=interval,
                button=button,
                duration=duration,
                tween=tween,
            )
        target_x, target_y = Mouse._normalize_point(x, y)
        Mouse._darwin_activate_app_at_point(target_x, target_y)
        if duration > 0:
            Mouse.move(target_x, target_y, duration=duration, tween=tween)
        else:
            Mouse.move(target_x, target_y, duration=0)
        time.sleep(0.05)

        button_code, down_event, up_event, _ = Mouse._mouse_event_spec(button)

        for _ in range(clicks):
            Mouse._post_mouse_event(down_event, target_x, target_y, button_code)
            time.sleep(max(0.05, interval / 2 if interval > 0 else 0.05))
            Mouse._post_mouse_event(up_event, target_x, target_y, button_code)
            if interval > 0:
                time.sleep(interval)
        return None

    @staticmethod
    def down(x=None, y=None, button=pyautogui.PRIMARY, duration=0.0, tween=pyautogui.linear):
        if not Mouse._is_darwin_native_available():
            return pyautogui.mouseDown(x=x, y=y, button=button, duration=duration, tween=tween)

        target_x, target_y = Mouse._normalize_point(x, y)
        Mouse._darwin_activate_app_at_point(target_x, target_y)
        if duration > 0:
            Mouse.move(target_x, target_y, duration=duration, tween=tween)
        else:
            Mouse.move(target_x, target_y, duration=0)
        button_code, down_event, _, _ = Mouse._mouse_event_spec(button)
        global _DARWIN_ACTIVE_BUTTON
        _DARWIN_ACTIVE_BUTTON = (button or "left").lower()
        Mouse._post_mouse_event(down_event, target_x, target_y, button_code)
        time.sleep(0.08)
        return None

    @staticmethod
    def up(x=None, y=None, button=pyautogui.PRIMARY, duration=0.0, tween=pyautogui.linear):
        if not Mouse._is_darwin_native_available():
            return pyautogui.mouseUp(x=x, y=y, button=button, duration=duration, tween=tween)

        target_x, target_y = Mouse._normalize_point(x, y)
        Mouse._darwin_activate_app_at_point(target_x, target_y)
        if duration > 0:
            Mouse.move(target_x, target_y, duration=duration, tween=tween)
        else:
            Mouse.move(target_x, target_y, duration=0)
        button_code, _, up_event, _ = Mouse._mouse_event_spec(button)
        time.sleep(0.05)
        Mouse._post_mouse_event(up_event, target_x, target_y, button_code)
        global _DARWIN_ACTIVE_BUTTON
        _DARWIN_ACTIVE_BUTTON = None
        return None

    @staticmethod
    def scroll(clicks, x=None, y=None):
        if not Mouse._is_darwin_native_available():
            return pyautogui.scroll(clicks=clicks, x=x, y=y)

        event = Quartz.CGEventCreateScrollWheelEvent(None, Quartz.kCGScrollEventUnitLine, 1, int(clicks))
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        return None

    @staticmethod
    def screen_size() -> tuple:
        if Mouse._is_darwin_native_available():
            bounds = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
            return int(bounds.size.width), int(bounds.size.height)
        return pyautogui.size()
