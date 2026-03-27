"""
RPA Highlighter 鈥?macOS PyQt5 瀹炵幇
鍔熻兘瀵归綈 Windows C# UI 搴擄紙HighlightForm / OverlayForm / ScreenshotForm / ToolbarForm锛?

鐢ㄦ硶: python pyqt.py <port>
"""

import json
import os
import sys
import threading
import time

from PyQt5.QtCore import (
    QEvent,
    QPoint,
    QRect,
    QRectF,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QColor,
    QCursor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt5.QtNetwork import QHostAddress, QUdpSocket
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if sys.platform == "darwin":
    try:
        import Quartz
    except Exception:
        Quartz = None
else:
    Quartz = None

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyqt_debug.log")


def debug_log(*parts):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        message = " ".join(str(part) for part in parts)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


# ─────────────────────────────────────────────
# Localization
# ─────────────────────────────────────────────


class Strings:
    _lang = "zh_CN"

    _data = {
        "en_US": {
            "capture_element": "Capture Element",
            "mouse_left_click": "Left Click",
            "exit": "Exit",
            "screenshot_pick": "Screenshot Pick",
            "smart_pick": "Smart Pick",
            "position": "Position",
            "smart_image_pick": "Smart Image Pick",
            "click_element": "Click Element",
            "back_to_interaction": "Back to Interaction",
            "manual_image_pick": "Manual Image Pick",
            "draw_to_capture": "Draw to Capture",
            "calculating": "Calculating, please wait...",
            "target_image": "Target Image",
            "select_unique_element": "Please select a unique element!",
            "notice": "Notice",
            "repick": "Repick",
            "confirm": "Confirm",
            "cancel": "Cancel",
            "save": "Save",
        },
        "zh_CN": {
            "capture_element": "捕获元素",
            "mouse_left_click": "鼠标左键",
            "exit": "退出",
            "screenshot_pick": "截图拾取",
            "smart_pick": "智能拾取",
            "position": "位置",
            "smart_image_pick": "智能图像拾取",
            "click_element": "单击元素",
            "back_to_interaction": "返回交互界面",
            "manual_image_pick": "普通图像拾取",
            "draw_to_capture": "绘框截图",
            "calculating": "计算中，请稍候...",
            "target_image": "目标图片",
            "select_unique_element": "请选择不重复的元素！",
            "notice": "提示",
            "repick": "重拾",
            "confirm": "确定",
            "cancel": "取消",
            "save": "保存",
        },
    }

    @classmethod
    def set_language(cls, lang):
        if lang in cls._data:
            cls._lang = lang

    @classmethod
    def get(cls, key):
        return cls._data.get(cls._lang, cls._data["en_US"]).get(key, key)


# ─────────────────────────────────────────────
# macOS window helpers
# ─────────────────────────────────────────────


def _get_nswindow(widget):
    """鑾峰彇 QWidget 瀵瑰簲鐨?NSWindow 瀵硅薄锛堜粎 macOS锛?"""
    if sys.platform != "darwin":
        return None
    try:
        import ctypes

        import objc

        return objc.objc_object(
            c_void_p=ctypes.c_void_p(int(widget.winId()))
        ).window()
    except Exception:
        return None


def set_macos_window_level(widget, level="screensaver"):
    """璁剧疆 macOS 绐楀彛灞傜骇"""
    if sys.platform != "darwin":
        return
    try:
        import AppKit

        win = _get_nswindow(widget)
        if win:
            levels = {
                "screensaver": AppKit.NSScreenSaverWindowLevel,
                "floating": AppKit.NSFloatingWindowLevel,
                "normal": AppKit.NSNormalWindowLevel,
            }
            win.setLevel_(levels.get(level, AppKit.NSScreenSaverWindowLevel))
            # NSWindowCollectionBehaviorCanJoinAllSpaces
            win.setCollectionBehavior_(1 << 3)
            debug_log("set_macos_window_level", type(widget).__name__, level)
    except Exception:
        pass


def set_ignore_mouse_events(widget, ignore=True):
    """璁剧疆绐楀彛鏄惁蹇界暐榧犳爣浜嬩欢锛堢┛閫忥級"""
    if sys.platform != "darwin":
        return
    try:
        win = _get_nswindow(widget)
        if win:
            win.setIgnoresMouseEvents_(ignore)
            debug_log("set_ignore_mouse_events", type(widget).__name__, "ignore=", ignore)
    except Exception:
        pass


def apply_overlay_flags(widget, mouse_passthrough=True):
    """涓€娆℃€у簲鐢?overlay 绐楀彛鏍囧織锛氱疆椤?+ 榧犳爣绌块€?"""
    if sys.platform == "darwin":
        set_macos_window_level(widget)
        set_ignore_mouse_events(widget, mouse_passthrough)


def apply_non_activating_flags(widget):
    try:
        widget.setAttribute(Qt.WA_ShowWithoutActivating, True)
        if hasattr(Qt, "WA_MacAlwaysShowToolWindow"):
            widget.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        debug_log("apply_non_activating_flags", type(widget).__name__)
    except Exception:
        pass


# ─────────────────────────────────────────────
# ToolbarForm（重拾 / 确定 按钮）
# ─────────────────────────────────────────────s


class ToolbarForm(QWidget):
    """浮动工具栏：承载 重拾/确定 按钮，避免受透明窗口影响"""

    repick_clicked = pyqtSignal()
    confirm_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        apply_non_activating_flags(self)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._btn_repick = self._make_button(
            Strings.get("repick"), "#141414", border_color="#424242"
        )
        self._btn_confirm = self._make_button(
            Strings.get("confirm"), "#F39D09", border_color=None
        )

        self._btn_repick.clicked.connect(self.repick_clicked)
        self._btn_confirm.clicked.connect(self.confirm_clicked)

        layout.addWidget(self._btn_repick)
        layout.addWidget(self._btn_confirm)
        self.adjustSize()

    @staticmethod
    def _make_button(text, bg_color, border_color=None):
        btn = QPushButton(text)
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        border_css = (
            f"border: 1px solid {border_color};" if border_color else "border: none;"
        )
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-family: "Microsoft YaHei", "PingFang SC", Arial;
                {border_css}
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """
        )
        return btn

    def refresh_labels(self):
        """语言切换后刷新按钮文字"""
        self._btn_repick.setText(Strings.get("repick"))
        self._btn_confirm.setText(Strings.get("confirm"))


# ─────────────────────────────────────────────
# HighlightForm（全屏透明高亮窗口）
# ─────────────────────────────────────────────


class HighlightForm(QWidget):
    """
    全屏透明 overlay，绘制圆角矩形高亮框 + 元素标签。
    支持：单/多元素高亮、锚点高亮、闪烁校验、工具栏定位。
    """

    toolbar_repick = pyqtSignal()
    toolbar_confirm = pyqtSignal()

    # 颜色常量（对齐 C# #726FFF / #F39D09）
    COLOR_HIGHLIGHT_FILL = QColor(114, 111, 255, 89)  # 35% opacity
    COLOR_HIGHLIGHT_BORDER = QColor(114, 111, 255)
    COLOR_ANCHOR_FILL = QColor(243, 157, 9, 50)
    COLOR_ANCHOR_BORDER = QColor(243, 157, 9)

    def __init__(self):
        super().__init__()

        # 状态
        self._mode = "normal"  # normal / picking / CV_ALT / designate / validate
        self._boxes = []  # list[QRect]
        self._labels = []  # list[str]
        self._rect_visible = True
        self._anchor_box = None  # QRect | None
        self._anchor_label = ""

        # 普通消隐计时器
        self.clear_timer = QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.clear_rect)

        # 闪烁计时器
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._on_blink_tick)
        self._blink_count = 0
        self._blink_total = 0

        # 工具栏
        self._toolbar = None

        # 窗口标志
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        apply_non_activating_flags(self)

        self._full_screen()

        # 【关键修改】始终启用鼠标穿透，保证底层窗口能接收所有鼠标事件
        apply_overlay_flags(self, mouse_passthrough=True)

    # ── 窗口管理 ────────────────────────────

    def _full_screen(self):
        screen = QGuiApplication.primaryScreen()
        geo = screen.geometry()
        self.setGeometry(geo)
        self.show()
        debug_log("HighlightForm full_screen_show")
        # 确保穿透生效
        apply_overlay_flags(self, mouse_passthrough=True)

    def _ensure_visible(self, mouse_passthrough=True):
        if not self.isVisible():
            self.show()

        apply_overlay_flags(self, mouse_passthrough=True)
        debug_log("HighlightForm ensure_visible", self._mode, self.isVisible(), len(self._boxes))

    #  ── 清除 / 初始化 ───────────────────────

    def clear_rect(self):
        """清除所有高亮"""
        self._boxes = []
        self._labels = []
        self._rect_visible = True
        self._hide_toolbar()
        self.update()

    def initialize(self):
        """完全重置状态（对应 C# Initialize）"""
        self._stop_blink()
        self.clear_timer.stop()
        self._mode = "normal"
        self._boxes = []
        self._labels = []
        self._anchor_box = None
        self._anchor_label = ""
        self._rect_visible = True
        self._hide_toolbar()
        apply_overlay_flags(self, mouse_passthrough=True)
        self.update()

    # 鈹€鈹€ 楂樹寒鎿嶄綔 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def update_rect(self, boxes, labels=None, mode="picking"):
        """普通高亮：显示 800ms 后自动消失"""
        self._stop_blink()
        self.clear_timer.stop()
        self._mode = mode
        self._boxes = self._pad_boxes(boxes)
        self._labels = labels or [""] * len(boxes)
        self._rect_visible = True
        self._ensure_visible(mouse_passthrough=True)
        self.update()
        self.clear_timer.start(800)

    def show_rect_with_toolbar(self, boxes, labels=None):
        """designate 模式：高亮 + 立即显示重拾/确定工具栏"""
        self._stop_blink()
        self.clear_timer.stop()
        self._mode = "designate"
        self._boxes = self._pad_boxes(boxes)
        self._labels = labels or [""] * len(boxes)
        self._rect_visible = True

        self._ensure_visible(mouse_passthrough=True)
        self.update()
        if self._boxes:
            self.show_toolbar(self._boxes[0])

    def show_rect_cv_alt(self, boxes, labels=None):
        """CV_ALT 模式：高亮 + 等待点击显示工具栏（通过全局事件过滤器实现）"""
        self._stop_blink()
        self.clear_timer.stop()
        self._mode = "CV_ALT"
        self._boxes = self._pad_boxes(boxes)
        self._labels = labels or [""] * len(boxes)
        self._rect_visible = True
        self._ensure_visible(mouse_passthrough=True)
        self.update()

    def blink_rect(self, boxes, labels=None, times=3, interval=500):
        """校验用：闪烁 times 次后消失"""
        self._stop_blink()
        self.clear_timer.stop()
        self._mode = "validate"
        self._boxes = self._pad_boxes(boxes)
        self._labels = labels or [""] * len(boxes)
        self._rect_visible = True
        self._blink_count = 0
        self._blink_total = times * 2
        self._ensure_visible(mouse_passthrough=True)
        self.update()
        self._blink_timer.start(interval)

    def set_anchor(self, box, label=""):
        """设置锚点矩形（橙色）"""
        self._anchor_box = box
        self._anchor_label = label
        self.update()

    # ── 工具栏 ───────────────────────────────

    def show_toolbar(self, rect):
        """公共方法：在指定矩形附近显示工具栏"""
        if self._toolbar is None:
            self._toolbar = ToolbarForm()
            self._toolbar.repick_clicked.connect(self.toolbar_repick)
            self._toolbar.confirm_clicked.connect(self.toolbar_confirm)

        self._toolbar.refresh_labels()

        screen = QGuiApplication.primaryScreen().geometry()
        tb_w = self._toolbar.sizeHint().width()
        tb_h = 32

        x = rect.left()
        y = rect.bottom() + 5
        if y + tb_h > screen.height():
            y = rect.top() - tb_h - 5

        x = max(0, min(x, screen.width() - tb_w))
        y = max(0, min(y, screen.height() - tb_h))

        self._toolbar.move(x, y)
        self._toolbar.show()
        self._toolbar.raise_()

    def _hide_toolbar(self):
        if self._toolbar and self._toolbar.isVisible():
            self._toolbar.hide()

    # ── 辅助 ─────────────────────────────────

    @staticmethod
    def _pad_boxes(boxes, padding=4):
        return [
            QRect(
                r.left() - padding,
                r.top() - padding,
                r.width() + padding * 2,
                r.height() + padding * 2,
            )
            for r in boxes
        ]

    # ── 绘制 ─────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        if self._anchor_box is not None:
            self._draw_rounded_rect(
                painter,
                self._anchor_box,
                QColor(0, 0, 0, 0),
                self.COLOR_HIGHLIGHT_BORDER,
            )
            self._draw_label(
                painter,
                self._anchor_box,
                Strings.get("target_image"),
                text_color=self.COLOR_HIGHLIGHT_BORDER,
            )

        if self._boxes and self._rect_visible:
            is_anchor_mode = self._mode == "designate" and self._anchor_box is not None
            fill = self.COLOR_ANCHOR_FILL if is_anchor_mode else self.COLOR_HIGHLIGHT_FILL
            border = (
                self.COLOR_ANCHOR_BORDER if is_anchor_mode else self.COLOR_HIGHLIGHT_BORDER
            )

            for i, box in enumerate(self._boxes):
                self._draw_rounded_rect(painter, box, fill, border)
                label_text = self._labels[i] if i < len(self._labels) else ""
                if label_text:
                    label_color = (
                        self.COLOR_ANCHOR_BORDER if is_anchor_mode else QColor(240, 240, 240)
                    )
                    self._draw_label(painter, box, label_text, text_color=label_color)

    @staticmethod
    def _draw_rounded_rect(painter, rect, fill_color, border_color, radius=4):
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(fill_color)
        painter.drawPath(path)

    @staticmethod
    def _draw_label(painter, rect, text, text_color=None):
        """在矩形上方（空间不足则下方）绘制文字徽章"""
        if not text:
            return

        font = QFont("PingFang SC", 14)
        font.setStyleStrategy(QFont.PreferAntialias)
        painter.setFont(font)
        fm = QFontMetrics(font)

        h_pad = 8
        text_w = fm.horizontalAdvance(text) + h_pad * 2
        text_h = fm.height() + h_pad * 2

        x = rect.left()
        y = rect.top() - text_h - 5
        if y < 0:
            y = rect.bottom() + 5

        badge_rect = QRectF(x, y, text_w, text_h)

        bg_path = QPainterPath()
        bg_path.addRoundedRect(badge_rect, 4, 4)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 255))
        painter.drawPath(bg_path)

        painter.setPen(text_color or QColor(240, 240, 240))
        painter.drawText(badge_rect, Qt.AlignCenter, text)

    # ── 闪烁 ────────────────────────────────

    def _on_blink_tick(self):
        self._blink_count += 1
        self._rect_visible = not self._rect_visible
        self.update()
        if self._blink_count >= self._blink_total:
            self._stop_blink()
            self.clear_rect()

    def _stop_blink(self):
        if self._blink_timer.isActive():
            self._blink_timer.stop()


# ─────────────────────────────────────────────
# OverlayForm（操作指引面板）
# ─────────────────────────────────────────────


class OverlayForm(QWidget):
    """
    黑色半透明圆角面板，显示当前操作模式的快捷键提示。
    支持 6 种模式：normal / point / CV / CV_ALT / CV_CTRL / waiting
    鼠标进入时自动切换到屏幕对角位置。
    """

    def __init__(self):
        super().__init__()
        self._alert_type = "normal"
        self._mouse_x = 0
        self._mouse_y = 0
        self._at_default_pos = True

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)
        apply_non_activating_flags(self)

        self.hide()

    def show_panel(self, alert_type):
        self._alert_type = alert_type
        self._at_default_pos = True
        self._update_geometry()
        self.show()
        self.raise_()
        if sys.platform == "darwin":
            apply_overlay_flags(self, mouse_passthrough=True)
        debug_log("OverlayForm show_panel", alert_type, self.geometry().getRect())

    def hide_panel(self):
        debug_log("OverlayForm hide_panel")
        self.hide()

    def update_cursor(self, x, y):
        if self._mouse_x == x and self._mouse_y == y:
            return
        self._mouse_x = x
        self._mouse_y = y
        if self.isVisible() and self.geometry().contains(x, y):
            debug_log("OverlayForm cursor_inside_geometry", (x, y), self.geometry().getRect())
        if self.isVisible() and self._alert_type in ("CV", "CV_ALT", "CV_CTRL"):
            self.update()

    # ── 自动避让 ─────────────────────────────

    def enterEvent(self, event):
        debug_log("OverlayForm enterEvent")
        self._at_default_pos = not self._at_default_pos
        self._update_geometry()
        super().enterEvent(event)

    def _update_geometry(self):
        lines = self._get_lines()
        line_h = 32
        has_title = self._alert_type in ("CV_ALT", "CV_CTRL")
        title_h = 36 if has_title else 0
        padding = 16
        h = len(lines) * line_h + padding * 2 + title_h
        w = 300

        font = QFont("PingFang SC", 12)
        fm = QFontMetrics(font)
        for label, key in lines:
            needed = fm.horizontalAdvance(label) + (fm.horizontalAdvance(key) if key else 0) + 80
            w = max(w, needed)
        w = min(w, 400)

        self.setFixedSize(w, h)

        screen = QGuiApplication.primaryScreen().geometry()
        if self._at_default_pos:
            self.move(10, 10)
        else:
            self.move(screen.right() - w - 10, screen.bottom() - h - 10)

    # ── 内容定义 ──────────────────────────────

    def _get_lines(self):
        """返回 [(label, key_or_None), ...] 列表"""
        s = Strings.get
        t = self._alert_type

        if t in ("normal", "point"):
            return [
                (s("capture_element"), "Ctrl + " + s("mouse_left_click")),
                (s("exit"), "Esc"),
            ]
        elif t == "CV":
            return [
                (s("screenshot_pick"), "Ctrl"),
                (s("smart_pick"), "Alt"),
                (s("exit"), "Esc"),
                (s("position"), f"{self._mouse_x},{self._mouse_y}"),
            ]
        elif t == "CV_ALT":
            return [
                (s("smart_image_pick") + " / " + s("click_element"), None),
                (s("back_to_interaction"), "Shift"),
                (s("exit"), "Esc"),
                (s("position"), f"{self._mouse_x},{self._mouse_y}"),
            ]
        elif t == "CV_CTRL":
            return [
                (s("manual_image_pick") + " / " + s("draw_to_capture"), None),
                (s("back_to_interaction"), "Shift"),
                (s("exit"), "Esc"),
                (s("position"), f"{self._mouse_x},{self._mouse_y}"),
            ]
        elif t == "waiting":
            return [(s("calculating"), None)]
        return []

    def _get_title(self):
        """CV_ALT / CV_CTRL 模式的标题行文字"""
        s = Strings.get
        if self._alert_type == "CV_ALT":
            return s("smart_image_pick") + "  " + s("click_element")
        elif self._alert_type == "CV_CTRL":
            return s("manual_image_pick") + "  " + s("draw_to_capture")
        return None

    # ── 绘制 ──────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        radius = 16
        has_title = self._alert_type in ("CV_ALT", "CV_CTRL")
        title_h = 36 if has_title else 0
        accent = QColor(114, 111, 255) if has_title else None

        # ─ 背景 ─
        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 30, 30, 230))
        painter.drawPath(bg_path)

        # ─ 标题色条（CV_ALT / CV_CTRL） ─
        if accent:
            clip_path = QPainterPath()
            clip_path.addRoundedRect(QRectF(0, 0, w, title_h + radius), radius, radius)
            bottom_rect = QPainterPath()
            bottom_rect.addRect(QRectF(0, title_h, w, radius))
            title_path = clip_path.united(bottom_rect)
            # 只画顶部
            painter.save()
            painter.setClipRect(QRectF(0, 0, w, title_h))
            painter.setBrush(accent)
            painter.drawPath(bg_path)
            painter.restore()

            # 标题文字
            title_text = self._get_title()
            if title_text:
                title_font = QFont("PingFang SC", 12, QFont.Bold)
                painter.setFont(title_font)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(
                    QRectF(0, 0, w, title_h), Qt.AlignCenter, title_text
                )

        # ─ 内容行 ─
        lines = self._get_lines()
        # CV_ALT/CV_CTRL 的第一行已经在标题中显示了
        if has_title and lines:
            lines = lines[1:]

        font = QFont("PingFang SC", 12)
        painter.setFont(font)
        fm = QFontMetrics(font)

        padding = 16
        line_h = 32
        y = title_h + padding

        for label, key in lines:
            if key is None:
                # 无快捷键，仅标签
                painter.setPen(QColor(220, 220, 220))
                painter.drawText(
                    QRectF(padding, y, w - padding * 2, line_h),
                    Qt.AlignVCenter | Qt.AlignLeft,
                    label,
                )
            else:
                # 左侧标签
                painter.setPen(QColor(180, 180, 180))
                painter.drawText(
                    QRectF(padding, y, w * 0.5, line_h),
                    Qt.AlignVCenter | Qt.AlignLeft,
                    label,
                )
                # 右侧快捷键徽章
                key_w = fm.horizontalAdvance(key) + 16
                key_x = w - padding - key_w
                key_rect = QRectF(key_x, y + 4, key_w, line_h - 8)

                key_bg = QPainterPath()
                key_bg.addRoundedRect(key_rect, 6, 6)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(255, 255, 255, 41))
                painter.drawPath(key_bg)

                painter.setPen(QColor(255, 255, 255))
                painter.drawText(key_rect, Qt.AlignCenter, key)

            y += line_h


# ─────────────────────────────────────────────
# ScreenshotForm（全屏截图选区）
# ─────────────────────────────────────────────


class ScreenshotForm(QWidget):
    """
    全屏截图：暗色蒙版 + 拖拽选区 + Save/Cancel 工具栏。
    截图完成后通过 signal 返回选区坐标。
    """

    screenshot_confirmed = pyqtSignal(QRect)  # 纭閫夊尯
    screenshot_cancelled = pyqtSignal()  # 鍙栨秷

    def __init__(self):
        super().__init__()
        self._pixmap = None
        self._start = None
        self._end = None
        self._drawing = False
        self._finished = False
        self._toolbar_widget = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.hide()

    def capture_and_show(self):
        """鎴彇褰撳墠灞忓箷骞舵樉绀洪€夊尯鐣岄潰"""
        screen = QGuiApplication.primaryScreen()
        self._pixmap = screen.grabWindow(0)
        self._start = None
        self._end = None
        self._drawing = False
        self._finished = False

        geo = screen.geometry()
        self.setGeometry(geo)
        self.show()
        self.raise_()
        self.activateWindow()
        if sys.platform == "darwin":
            set_macos_window_level(self, "screensaver")

    # ── 鼠标事件 ──────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self._finished:
            self._start = event.pos()
            self._end = event.pos()
            self._drawing = True
            self._hide_toolbar()
            self.update()

    def mouseMoveEvent(self, event):
        if self._drawing:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._drawing:
            self._end = event.pos()
            self._drawing = False
            sel = QRect(self._start, self._end).normalized()
            if sel.width() > 5 and sel.height() > 5:
                self._finished = True
                self.setCursor(Qt.ArrowCursor)
                self.update()
                self._show_toolbar(sel)
            else:
                # 閫夊尯澶皬锛岄噸缃?
                self._start = None
                self._end = None
                self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._cancel()

    # ── 绘制 ──────────────────────────────────

    def paintEvent(self, event):
        if self._pixmap is None:
            return

        painter = QPainter(self)

        # 原始屏幕
        painter.drawPixmap(0, 0, self._pixmap)

        # 暗色蒙版（60% 黑色）
        painter.fillRect(self.rect(), QColor(0, 0, 0, 153))

        # 选区：显示原始内容 + 边框
        if self._start and self._end:
            sel = QRect(self._start, self._end).normalized()
            painter.drawPixmap(sel, self._pixmap, sel)
            painter.setPen(QPen(QColor(114, 111, 255), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(sel)

    # ── 工具栏 ────────────────────────────────

    def _show_toolbar(self, sel_rect):
        if self._toolbar_widget is None:
            self._toolbar_widget = QWidget(self)
            layout = QHBoxLayout(self._toolbar_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            btn_cancel = self._make_btn(Strings.get("cancel"), "#141414", "#424242")
            btn_save = self._make_btn(Strings.get("save"), "#726FFF", None)

            btn_cancel.clicked.connect(self._cancel)
            btn_save.clicked.connect(self._save)

            layout.addWidget(btn_cancel)
            layout.addWidget(btn_save)
            self._toolbar_widget.adjustSize()

        screen = QGuiApplication.primaryScreen().geometry()
        tb = self._toolbar_widget
        tb_w = tb.width()
        tb_h = tb.height()

        x = sel_rect.right() - tb_w
        y = sel_rect.bottom() + 10
        if y + tb_h > screen.height():
            y = sel_rect.top() - tb_h - 10
        x = max(0, min(x, screen.width() - tb_w))
        y = max(0, y)

        tb.move(x, y)
        tb.show()
        tb.raise_()

    def _hide_toolbar(self):
        if self._toolbar_widget and self._toolbar_widget.isVisible():
            self._toolbar_widget.hide()

    @staticmethod
    def _make_btn(text, bg_color, border_color):
        btn = QPushButton(text)
        btn.setFixedSize(65, 32)
        btn.setCursor(Qt.PointingHandCursor)
        border_css = (
            f"border: 1px solid {border_color};" if border_color else "border: none;"
        )
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-family: "PingFang SC", Arial;
                {border_css}
            }}
        """
        )
        return btn

    def _cancel(self):
        self._hide_toolbar()
        self._start = None
        self._end = None
        self._drawing = False
        self._finished = False
        self.setCursor(Qt.CrossCursor)
        self.update()

    def _save(self):
        if self._start and self._end:
            sel = QRect(self._start, self._end).normalized()
            self._hide_toolbar()
            self.hide()
            self.screenshot_confirmed.emit(sel)
        else:
            self._cancel()

    def dismiss(self):
        """部调用：关闭截图窗口"""
        self._hide_toolbar()
        self.hide()
        self._start = None
        self._end = None
        self._drawing = False
        self._finished = False


# ─────────────────────────────────────────────
# CustomMessageBox（无效元素警告）
# ─────────────────────────────────────────────


class CustomMessageBox(QDialog):
    def __init__(self, message, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 150)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px;")
        layout.addWidget(label)

        layout.addStretch()

        btn = QPushButton(Strings.get("confirm"))
        btn.setFixedSize(80, 30)
        btn.setStyleSheet(
            """
            QPushButton {
                background-color: #726FFF;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
        """
        )
        btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)


# ─────────────────────────────────────────────
# ConsoleApp（UDP 通信主控）
# ─────────────────────────────────────────────


class ConsoleApp(QMainWindow):
    global_mouse_click = pyqtSignal(int, int)
    """
    主控台：监听 UDP 端口，根据 JSON 消息调度各个 UI 组件。

    协议对齐 C#：
    - start: 初始化模式，显示提示窗口/截图窗口
    - picking: 更新高亮框
    - validate: 闪烁校验
    - initialize: 重置（ESC 退出 / SHIFT 回到 CV 模式）
    - exit: 退出程序
    """

    def __init__(self, port):
        super().__init__()
        self.hide()
        debug_log("ConsoleApp starting", "port=", port, "platform=", sys.platform)

        self._port = int(port)
        self._current_mode = "normal"
        self._sender_host = None
        self._sender_port = None
        self._cv_alt_locked = False
        self._click_tap = None
        self._click_tap_src = None
        self._click_tap_rl = None
        self._click_tap_thread = None
        self._click_tap_callback = None

        # UDP
        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.Any, self._port)
        self.socket.readyRead.connect(self._read)

        # UI 组件
        self.highlight = HighlightForm()
        self.overlay = OverlayForm()
        self.screenshot = ScreenshotForm()

        # 鼠标跟踪定时器（200ms 间隔，对齐 C#）s
        self._mouse_timer = QTimer(self)
        self._mouse_timer.timeout.connect(self._update_cursor)
        self._mouse_timer.start(200)

        # 信号连接
        self.highlight.toolbar_repick.connect(self._on_repick)
        self.highlight.toolbar_confirm.connect(self._on_confirm)
        self.screenshot.screenshot_confirmed.connect(self._on_screenshot_confirmed)
        self.screenshot.screenshot_cancelled.connect(self._on_screenshot_cancelled)
        self.global_mouse_click.connect(self._on_global_mouse_click)

        # 安装事件过滤器：复用现有 CV_ALT 点击确认逻辑，但不拦截事件本身
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self._start_global_click_monitor()

        debug_log("ConsoleApp event filters installed")
        print(f"Server started, listening on port {self._port}...")

    # ── 全局事件过滤器（处理 CV_ALT 模式下的点击） ──

    def eventFilter(self, obj, event):
        # 只处理鼠标按下事件
        if event.type() == QEvent.MouseButtonPress:
            # 仅在 CV_ALT 模式下且高亮窗口可见、存在高亮框时检查
            if (self.highlight.isVisible() and
                    self.highlight._mode == "CV_ALT" and
                    self.highlight._boxes):
                # 获取全局点击位置
                pos = QCursor.pos()
                # 检查是否落在任意高亮框内（带扩展区域）
                for box in self.highlight._boxes:
                    expanded = box.adjusted(-10, -10, 10, 10)
                    if expanded.contains(pos):
                        self.highlight.show_toolbar(self.highlight._boxes[0])
                        break
        # 始终允许事件继续传递，不拦截
        return super().eventFilter(obj, event)

    def _on_global_mouse_click(self, x, y):
        """处理 macOS 全局左键点击；只观察，不拦截底层应用事件"""
        if not (
            self.highlight.isVisible()
            and self.highlight._mode == "CV_ALT"
            and self.highlight._boxes
            and not self._cv_alt_locked
        ):
            return

        pos = QPoint(int(x), int(y))
        for box in self.highlight._boxes:
            expanded = box.adjusted(-10, -10, 10, 10)
            if expanded.contains(pos):
                self._cv_alt_locked = True
                self.highlight.show_toolbar(self.highlight._boxes[0])
                break

    def _start_global_click_monitor(self):
        """macOS 使用 CGEventTap 监听全局左键，保持 overlay 穿透不变。"""
        if sys.platform != "darwin" or Quartz is None or self._click_tap_thread is not None:
            return

        def callback(proxy, event_type, event, refcon):
            if event_type == Quartz.kCGEventLeftMouseDown:
                loc = Quartz.CGEventGetLocation(event)
                self.global_mouse_click.emit(int(loc.x), int(loc.y))
            return event

        self._click_tap_callback = callback

        def run_tap():
            mask = Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown)
            tap = Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap,
                Quartz.kCGHeadInsertEventTap,
                Quartz.kCGEventTapOptionListenOnly,
                mask,
                self._click_tap_callback,
                None,
            )

            if tap is None:
                debug_log("ConsoleApp global click monitor unavailable")
                return

            rl = Quartz.CFRunLoopGetCurrent()
            src = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
            Quartz.CFRunLoopAddSource(rl, src, Quartz.kCFRunLoopCommonModes)
            Quartz.CGEventTapEnable(tap, True)

            self._click_tap = tap
            self._click_tap_src = src
            self._click_tap_rl = rl
            debug_log("ConsoleApp global click monitor started")
            Quartz.CFRunLoopRun()
            debug_log("ConsoleApp global click monitor stopped")

        self._click_tap_thread = threading.Thread(target=run_tap, daemon=True)
        self._click_tap_thread.start()

    def _stop_global_click_monitor(self):
        if sys.platform != "darwin" or Quartz is None:
            return
        try:
            if self._click_tap:
                Quartz.CGEventTapEnable(self._click_tap, False)
        except Exception:
            pass
        try:
            if self._click_tap_src and self._click_tap_rl:
                Quartz.CFRunLoopRemoveSource(
                    self._click_tap_rl, self._click_tap_src, Quartz.kCFRunLoopCommonModes
                )
        except Exception:
            pass
        try:
            if self._click_tap_rl:
                Quartz.CFRunLoopStop(self._click_tap_rl)
        except Exception:
            pass
        self._click_tap = None
        self._click_tap_src = None
        self._click_tap_rl = None
        self._click_tap_thread = None

    # ── 鼠标跟踪 ─────────────────────────────

    def _update_cursor(self):
        pos = QCursor.pos()
        self.overlay.update_cursor(pos.x(), pos.y())

    # ── UDP 通信 ──────────────────────────────

    def _send_response(self, msg_dict):
        """向发送方回复 JSON"""
        if self._sender_host is None:
            return
        data = json.dumps(msg_dict, ensure_ascii=False).encode("utf-8")
        self.socket.writeDatagram(data, self._sender_host, self._sender_port)
        print(f"Response sent to {self._sender_host.toString()}:{self._sender_port}: {msg_dict}")

    def _read(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(
                self.socket.pendingDatagramSize()
            )
            # 记录发送方地址（用于回复）
            self._sender_host = QHostAddress(host)
            self._sender_port = port

            try:
                msg = json.loads(data.decode("utf-8"))
            except Exception:
                continue

            print(f"Received from {host.toString()}:{port}: {msg}")
            self._handle(msg)

    # ── 消息解析 ──────────────────────────────

    @staticmethod
    def _parse_boxes(msg):
        """从 msg["Boxes"] 解析 QRect 列表和标签列表"""
        boxes = []
        labels = []
        for box in msg.get("Boxes") or []:
            rect = QRect(
                box["Left"],
                box["Top"],
                box["Right"] - box["Left"],
                box["Bottom"] - box["Top"],
            )
            boxes.append(rect)
            labels.append(box.get("Msg", ""))
        return boxes, labels

    # ── 消息处理 ──────────────────────────────

    def _handle(self, msg):
        op = msg.get("Operation", "")
        mode = msg.get("Type", "")
        lang = msg.get("Language", "")
        debug_log("ConsoleApp handle", "op=", op, "mode=", mode, "msg=", msg)

        if lang:
            Strings.set_language(lang)

        # ── start ──
        if op == "start":
            self._current_mode = mode
            self._cv_alt_locked = False
            self.highlight.initialize()
            boxes, labels = self._parse_boxes(msg)

            if mode == "CV_CTRL":
                # 截图拾取模式
                self.overlay.show_panel("CV_CTRL")
                self.screenshot.capture_and_show()

            elif mode == "CV_ALT":
                # 智能拾取模式s
                self.overlay.show_panel("CV_ALT")
                # 不再设置鼠标穿透为 False，始终保持穿透
                if boxes:
                    self.highlight.show_rect_cv_alt(boxes, labels)

            elif mode in ("normal", "record"):
                self.overlay.show_panel("normal")
                # 始终穿透，无需额外设置

            elif mode == "point":
                self.overlay.show_panel("point")
                # 始终穿透

            elif mode == "CV":
                self.overlay.show_panel("CV")

            elif mode == "validate":
                if boxes:
                    self.highlight.blink_rect(boxes, labels)

            elif mode == "designate":
                # 锚点拾取
                if boxes:
                    anchor_box = QRect(
                        msg["Boxes"][0]["Left"],
                        msg["Boxes"][0]["Top"],
                        msg["Boxes"][0]["Right"] - msg["Boxes"][0]["Left"],
                        msg["Boxes"][0]["Bottom"] - msg["Boxes"][0]["Top"],
                    )
                    self.highlight.set_anchor(anchor_box)
                # 保持穿透，工具栏通过 show_rect_with_toolbar 立即显示
                self.highlight.show_rect_with_toolbar(boxes, labels)

            elif mode == "hide":
                self.overlay.hide_panel()
                self.highlight.clear_rect()

        # ── picking ──
        elif op == "picking":
            if msg.get("Type") == "invalid":
                # 弹出"请选择不重复的元素"
                self._cv_alt_locked = False
                self.highlight._hide_toolbar()
                dlg = CustomMessageBox(
                    Strings.get("select_unique_element"),
                    Strings.get("notice"),
                )
                dlg.exec_()
                self._send_response({"Operation": "continue"})
                return

            boxes, labels = self._parse_boxes(msg)

            if self._current_mode == "CV_ALT":
                self.overlay.show_panel("CV_ALT")

            if boxes:
                if self._current_mode in ("CV_ALT",):
                    if self._cv_alt_locked:
                        return
                    self.highlight.show_rect_cv_alt(boxes, labels)
                elif self._current_mode == "designate":
                    self.highlight.show_rect_with_toolbar(boxes, labels)
                else:
                    self.highlight.update_rect(boxes, labels, self._current_mode)

        #  ── validate ──
        elif op == "validate":
            boxes, labels = self._parse_boxes(msg)
            if boxes:
                self.highlight.blink_rect(boxes, labels)

        # ── initialize ──
        elif op == "initialize":
            init_type = msg.get("Type", "")

            # SHIFT 只在 CV 模式系列有效
            if init_type == "SHIFT" and self._current_mode not in (
                    "CV_CTRL",
                    "CV_ALT",
            ):
                return

            self.highlight.initialize()
            self.screenshot.dismiss()
            self._cv_alt_locked = False

            if init_type == "SHIFT":
                # 回到 CV 模式
                self.overlay.show_panel("CV")
                self._current_mode = "CV"
            elif init_type == "ESC":
                self.overlay.hide_panel()
                self._current_mode = "normal"
                # 无需设置穿透

        # ── exit ──
        elif op == "exit":
            self._stop_global_click_monitor()
            self.highlight.clear_rect()
            self.overlay.hide_panel()
            self.screenshot.dismiss()
            QApplication.quit()

    # ── 工具栏回调 ────────────────────────────

    def _on_repick(self):
        """重拾按钮"""
        self._cv_alt_locked = False
        self.highlight._hide_toolbar()
        self.highlight._boxes = []
        self.highlight.update()
        self._send_response({"Operation": "continue"})

    def _on_confirm(self):
        """确定按钮"""
        self._cv_alt_locked = False
        if self.highlight._boxes:
            box = self.highlight._boxes[0]
            self._send_response(
                {
                    "Operation": "confirm",
                    "Boxes": [
                        {
                            "Left": box.left(),
                            "Top": box.top(),
                            "Right": box.right(),
                            "Bottom": box.bottom(),
                        }
                    ],
                }
            )
        self.highlight.clear_rect()

    def _on_screenshot_confirmed(self, sel_rect):
        """截图确认"""
        self._send_response(
            {
                "Operation": "confirm",
                "Boxes": [
                    {
                        "Left": sel_rect.left(),
                        "Top": sel_rect.top(),
                        "Right": sel_rect.right(),
                        "Bottom": sel_rect.bottom(),
                    }
                ],
            }
        )
        self.overlay.hide_panel()

    def _on_screenshot_cancelled(self):
        """截图取消"""
        self._send_response({"Operation": "continue"})
        self.overlay.show_panel("CV")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pyqt.py <port>")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    console = ConsoleApp(sys.argv[1])
    sys.exit(app.exec_())
