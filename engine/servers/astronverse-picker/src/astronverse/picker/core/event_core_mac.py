import threading
import time

import Quartz
from astronverse.picker import IEventCore, MKSign
from astronverse.picker.logger import logger


class EventCore(IEventCore):
    """macOS 键鼠事件核心，对应 event_core_win.py

    使用 CGEventTap 替代 pyWinhook：
    - Ctrl 键    → kCGEventFlagMaskControl
    - Ctrl+左击  → is_focus() = True（对应 Windows Ctrl+左键）
    - ESC 键     → is_cancel() = True
    - F4 键      → is_f4_pressed() = True
    """

    def __init__(self):
        self.__tap = None
        self.__tap_src = None
        self.__tap_rl = None
        self.__closed = True
        self.__control_down = False
        self.__esc = False
        self.__control_left_down = False
        self.__init = False
        self.__f4_pressed = False
        self.domain = None
        self.__thread = None

    # ── 内部 CGEventTap 回调 ────────────────────────────────────────────────

    def __event_callback__(self, proxy, event_type, event, refcon):
        flags = Quartz.CGEventGetFlags(event)
        ctrl = Quartz.kCGEventFlagMaskControl

        # 鼠标左键按下 + Ctrl → is_focus
        if event_type == Quartz.kCGEventLeftMouseDown:
            if flags & ctrl:
                self.__control_left_down = True
                return None  # 拦截，不传给目标应用
            return event

        # 键盘按下
        if event_type == Quartz.kCGEventKeyDown:
            keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            # kVK_Escape = 53, kVK_F4 = 118, kVK_Control = 59
            if keycode == 53:  # ESC
                self.__esc = True
            elif keycode == 118:  # F4
                self.__f4_pressed = True
            elif keycode == 59:  # Left Control
                self.__control_down = True
            return event

        # 键盘释放
        if event_type == Quartz.kCGEventKeyUp:
            keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            if keycode == 59:  # Left Control
                self.__control_down = False
            return event

        return event

    # ── CGEventTap RunLoop（后台线程）───────────────────────────────────────

    def __hook__(self):
        logger.info("EventCore __hook__ start")

        mask = (
            Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown)
            | Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
            | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)
        )

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            mask,
            self.__event_callback__,
            None,
        )

        if tap is None:
            logger.error("CGEventTap 创建失败，请在「系统设置→隐私→辅助功能」中授权")
            self.__init = True  # 解除 start() 的等待
            return

        rl = Quartz.CFRunLoopGetCurrent()
        src = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        Quartz.CFRunLoopAddSource(rl, src, Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(tap, True)

        self.__tap = tap
        self.__tap_src = src
        self.__tap_rl = rl
        self.__init = True

        logger.info("EventCore __hook__ running")
        Quartz.CFRunLoopRun()
        logger.info("EventCore __hook__ end")

    def __un_hook__(self):
        try:
            if self.__tap:
                Quartz.CGEventTapEnable(self.__tap, False)
        except Exception:
            pass
        try:
            if self.__tap_src and self.__tap_rl:
                Quartz.CFRunLoopRemoveSource(self.__tap_rl, self.__tap_src, Quartz.kCFRunLoopCommonModes)
        except Exception:
            pass
        try:
            if self.__tap_rl:
                Quartz.CFRunLoopStop(self.__tap_rl)
        except Exception:
            pass
        self.__tap = None
        self.__tap_src = None
        self.__tap_rl = None
        logger.info("EventCore __un_hook__")

    # ── IEventCore 接口 ─────────────────────────────────────────────────────

    def start(self, domain=MKSign.PICKER):
        if not self.__closed:
            return False

        logger.info("EventCore start")
        self.__init = False
        self.__control_down = False
        self.__control_left_down = False
        self.__esc = False
        self.__f4_pressed = False
        self.__closed = False

        self.__thread = threading.Thread(target=self.__hook__, daemon=True)
        self.__thread.start()

        # 等待 tap 初始化完成
        while not self.__init:
            time.sleep(0.01)

        self.domain = domain
        return True

    def close(self):
        if self.__closed:
            return False

        logger.info("EventCore close")
        self.__un_hook__()
        self.__control_down = False
        self.__control_left_down = False
        self.__esc = False
        self.__f4_pressed = False
        self.__closed = True
        self.domain = None
        return True

    def is_cancel(self) -> bool:
        return self.__esc

    def is_focus(self) -> bool:
        return self.__control_left_down

    def is_f4_pressed(self) -> bool:
        return self.__f4_pressed

    def reset_f4_flag(self):
        self.__f4_pressed = False

    def reset_cancel_flag(self):
        self.__esc = False
