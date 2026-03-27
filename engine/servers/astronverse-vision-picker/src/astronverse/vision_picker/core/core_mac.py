from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    kAXFocusedWindowAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    AXValueGetValue,
    kAXValueCGPointType,
    kAXValueCGSizeType,
)
from AppKit import NSWorkspace, NSScreen
from astronverse.vision_picker.core.core import IPickCore, IRectHandler
from pynput.mouse import Controller


class RectHandler(IRectHandler):
    @staticmethod
    def get_foreground_window_rect():
        """
        获取当前前台窗口的信息和矩形区域
        返回: (window_id, window_title, rect)
        rect格式: (x, y, width, height)
        """
        try:
            # 获取前台应用
            import pyautogui
            width, height = pyautogui.size()
            return None, "Unknown", (0, 0, width, height)

        except Exception as e:
            return None, None, None


class PickCore(IPickCore):
    mouse = Controller()

    @staticmethod
    def get_mouse_position():
        """
        获取当前鼠标位置
        返回: (x, y)
        """
        position = PickCore.mouse.position
        return position

    @staticmethod
    def get_current_dpi():
        """
        获取当前显示设备的 DPI
        返回: (dpi_x, dpi_y)
        """
        try:
            screen = NSScreen.mainScreen()

            if not screen:
                # 如果无法获取屏幕信息，返回标准 DPI
                return 72, 72

            # 获取缩放因子（Retina 显示屏为 2.0，普通显示屏为 1.0）
            scale = screen.backingScaleFactor()

            # macOS 基准 DPI 为 72，实际 DPI = 72 * scale
            dpi = 72 * scale

            return dpi, dpi
        except Exception as e:
            # 发生异常时返回标准 DPI
            return 72, 72
