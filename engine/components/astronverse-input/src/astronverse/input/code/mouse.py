import random
import sys
import time

import pyautogui
from astronverse.baseline.logger.logger import logger
from astronverse.input import Speed
from astronverse.input.code.keyboard import Keyboard

if sys.platform == "darwin":
    from pynput.mouse import Button, Controller as MouseController
else:
    Button = None
    MouseController = None


speed_to_int = {Speed.SLOW: 0.5, Speed.NORMAL: 1, Speed.FAST: 2}
_DARWIN_ACTIVE_BUTTON: str | None = None
_DARWIN_MOUSE = MouseController() if MouseController is not None else None
_DARWIN_BUTTON_MAP = (
    {
        "left": Button.left,
        "middle": Button.middle,
        "right": Button.right,
    }
    if Button is not None
    else {}
)


class Mouse:
    def __int__(self):
        pyautogui.FAILSAFE = False

    @staticmethod
    def _is_darwin_native_available() -> bool:
        return sys.platform == "darwin" and _DARWIN_MOUSE is not None

    @staticmethod
    def _current_position() -> tuple[int, int]:
        if Mouse._is_darwin_native_available():
            x, y = _DARWIN_MOUSE.position
            return int(x), int(y)
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
        mapped = _DARWIN_BUTTON_MAP.get(normalized)
        if mapped is None:
            mapped = _DARWIN_BUTTON_MAP.get("left")
        return mapped

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

        Keyboard._darwin_activate_target_app()
        target_x, target_y = Mouse._normalize_point(x, y)
        start_x, start_y = Mouse._current_position()
        if duration <= 0:
            _DARWIN_MOUSE.position = (target_x, target_y)
            return None

        steps = max(1, int(duration / 0.01))
        for index in range(1, steps + 1):
            progress = index / steps
            next_x = int(start_x + (target_x - start_x) * progress)
            next_y = int(start_y + (target_y - start_y) * progress)
            _DARWIN_MOUSE.position = (next_x, next_y)
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
        logger.info(
            f"[mouse-diag] Mouse.click x={x} y={y} clicks={clicks} interval={interval} button={button} duration={duration} darwin_native={Mouse._is_darwin_native_available()}"
        )
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
        Keyboard._darwin_activate_target_app()
        target_x, target_y = Mouse._normalize_point(x, y)
        if duration > 0:
            Mouse.move(target_x, target_y, duration=duration, tween=tween)
        else:
            Mouse.move(target_x, target_y, duration=0)
        button_code = Mouse._mouse_event_spec(button)
        for index in range(clicks):
            logger.info(f"[mouse-diag] Mouse.click.press idx={index + 1}/{clicks} pos={(target_x, target_y)} button={button}")
            _DARWIN_MOUSE.press(button_code)
            time.sleep(0.02)
            _DARWIN_MOUSE.release(button_code)
            logger.info(f"[mouse-diag] Mouse.click.release idx={index + 1}/{clicks} pos={(target_x, target_y)} button={button}")
            if interval > 0:
                time.sleep(interval)
        return None

    @staticmethod
    def down(x=None, y=None, button=pyautogui.PRIMARY, duration=0.0, tween=pyautogui.linear):
        logger.info(f"[mouse-diag] Mouse.down x={x} y={y} button={button} duration={duration} darwin_native={Mouse._is_darwin_native_available()}")
        if not Mouse._is_darwin_native_available():
            return pyautogui.mouseDown(x=x, y=y, button=button, duration=duration, tween=tween)

        Keyboard._darwin_activate_target_app()
        target_x, target_y = Mouse._normalize_point(x, y)
        if duration > 0:
            Mouse.move(target_x, target_y, duration=duration, tween=tween)
        else:
            Mouse.move(target_x, target_y, duration=0)
        button_code = Mouse._mouse_event_spec(button)
        global _DARWIN_ACTIVE_BUTTON
        _DARWIN_ACTIVE_BUTTON = (button or "left").lower()
        _DARWIN_MOUSE.press(button_code)
        logger.info(f"[mouse-diag] Mouse.down.press pos={(target_x, target_y)} button={button}")
        return None

    @staticmethod
    def up(x=None, y=None, button=pyautogui.PRIMARY, duration=0.0, tween=pyautogui.linear):
        logger.info(f"[mouse-diag] Mouse.up x={x} y={y} button={button} duration={duration} darwin_native={Mouse._is_darwin_native_available()}")
        if not Mouse._is_darwin_native_available():
            return pyautogui.mouseUp(x=x, y=y, button=button, duration=duration, tween=tween)

        target_x, target_y = Mouse._normalize_point(x, y)
        if duration > 0:
            Mouse.move(target_x, target_y, duration=duration, tween=tween)
        else:
            Mouse.move(target_x, target_y, duration=0)
        button_code = Mouse._mouse_event_spec(button)
        _DARWIN_MOUSE.release(button_code)
        logger.info(f"[mouse-diag] Mouse.up.release pos={(target_x, target_y)} button={button}")
        global _DARWIN_ACTIVE_BUTTON
        _DARWIN_ACTIVE_BUTTON = None
        return None

    @staticmethod
    def scroll(clicks, x=None, y=None):
        if not Mouse._is_darwin_native_available():
            return pyautogui.scroll(clicks=clicks, x=x, y=y)

        if x is not None or y is not None:
            target_x, target_y = Mouse._normalize_point(x, y)
            _DARWIN_MOUSE.position = (target_x, target_y)
        _DARWIN_MOUSE.scroll(0, int(clicks))
        return None

    @staticmethod
    def screen_size() -> tuple:
        return pyautogui.size()
