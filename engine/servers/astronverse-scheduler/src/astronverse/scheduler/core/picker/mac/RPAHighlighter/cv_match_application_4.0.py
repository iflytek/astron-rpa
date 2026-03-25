import json
import os
import sys
import time

from PyQt5.QtCore import QRect, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QGuiApplication, QPainter
from PyQt5.QtNetwork import QHostAddress, QUdpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


# ─────────────────────────────────────────────
# debug
# ─────────────────────────────────────────────

def debug_log(msg):
    try:
        with open("highlight.log", "a") as f:
            f.write(msg + "\n")
    except:
        pass


# ─────────────────────────────────────────────
# macOS window control
# ─────────────────────────────────────────────

def _get_nswindow(widget):
    try:
        import ctypes, objc
        return objc.objc_object(
            c_void_p=ctypes.c_void_p(int(widget.winId()))
        ).window()
    except:
        return None


def set_macos_window_level(widget):
    if sys.platform != "darwin":
        return
    try:
        import AppKit
        win = _get_nswindow(widget)
        if win:
            win.setLevel_(AppKit.NSScreenSaverWindowLevel)
            win.setCollectionBehavior_(1 << 3)
    except:
        pass


def set_ignore_mouse_events(widget):
    if sys.platform != "darwin":
        return
    try:
        win = _get_nswindow(widget)
        if win:
            win.setIgnoresMouseEvents_(True)
    except:
        pass


def apply_overlay_flags(widget):
    if sys.platform == "darwin":
        set_macos_window_level(widget)
        set_ignore_mouse_events(widget)


# ─────────────────────────────────────────────
# HighlightForm
# ─────────────────────────────────────────────

class HighlightForm(QWidget):
    message_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.draw_rect = QRect(0, 0, 1, 1)

        # ✅ 单一计时器（核心修复）
        self.clear_timer = QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.clear_rect)

        self.full_screen()

    def safe_grab_screen(self):
        self.hide()
        QApplication.processEvents()

        screen = QGuiApplication.primaryScreen()
        shot = screen.grabWindow(0)

        self.show()
        apply_overlay_flags(self)

        return shot

    def full_screen(self):
        screen = QGuiApplication.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())
        self.show()
        apply_overlay_flags(self)

    def clear_rect(self):
        self.draw_rect = QRect(0, 0, 1, 1)
        self.update()   # ✅ 不再用 repaint

    def update_rect(self, rect):
        padding = 4
        self.draw_rect = QRect(
            rect.left() - padding,
            rect.top() - padding,
            rect.width() + padding * 2,
            rect.height() + padding * 2,
        )

        # ✅ 避免频繁 show 导致闪烁
        if not self.isVisible():
            self.show()
            apply_overlay_flags(self)

        self.raise_()

        self.update()  # ✅ 替代 repaint()

        # ✅ 重置计时器（不会叠加）
        self.clear_timer.start(800)

    def paintEvent(self, event):
        painter = QPainter(self)

        # 清空透明背景
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # 蓝色高亮（DevTools风格）
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(59, 158, 255, 80))
        painter.drawRect(self.draw_rect)


# ─────────────────────────────────────────────
# ConsoleApp
# ─────────────────────────────────────────────

class ConsoleApp(QMainWindow):
    def __init__(self, port):
        super().__init__()

        self.socket = QUdpSocket(self)
        self.socket.bind(QHostAddress.Any, int(port))
        self.socket.readyRead.connect(self.read)

        self.highlight = HighlightForm()

    def read(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(
                self.socket.pendingDatagramSize()
            )
            msg = json.loads(data.decode())

            if msg["Operation"] == "picking":
                box = msg["Boxes"][0]

                self.highlight.update_rect(QRect(
                    box["Left"],
                    box["Top"],
                    box["Right"] - box["Left"],
                    box["Bottom"] - box["Top"],
                ))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) < 2:
        print("Usage: python highlight.py <port>")
        sys.exit(1)

    console = ConsoleApp(sys.argv[1])
    sys.exit(app.exec_())