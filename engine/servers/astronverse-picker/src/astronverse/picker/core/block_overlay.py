"""
全屏透明覆盖窗口模块

在智能组件拾取完成后，创建一个全屏、置顶、透明的覆盖窗口，
拦截除"星辰RPA"客户端窗口以外的所有鼠标操作，
直到元素保存完成后销毁覆盖窗口。

技术方案: Win32 Layered Window + SetWindowRgn 区域挖洞
- 创建全屏 TOPMOST 透明 Layered Window（alpha=1，几乎不可见）
- 通过 SetWindowRgn 设置窗口区域为 "全屏 - 星辰RPA窗口区域"
- "星辰RPA"区域无覆盖窗口，点击自然穿透到客户端
- 其他区域有覆盖窗口，点击被拦截吞掉
- 定时器定期刷新区域以适应窗口移动/缩放

调试支持:
- Ctrl+Shift+F12 全局热键: 强制关闭覆盖窗口
"""

import ctypes
import threading
import traceback

import win32api
import win32con
import win32gui
import win32process

from astronverse.picker.logger import logger

# Win32 常量
LWA_ALPHA = 0x02
WS_EX_NOACTIVATE = 0x08000000
WM_HOTKEY = 0x0312
RGN_DIFF = 4  # win32con.RGN_DIFF 可能不存在，直接定义

# GDI32 函数句柄
_gdi32 = ctypes.windll.gdi32
_user32 = ctypes.windll.user32


def _create_rect_rgn(left: int, top: int, right: int, bottom: int) -> int:
    """调用 GDI32 CreateRectRgn 创建矩形区域"""
    return _gdi32.CreateRectRgn(left, top, right, bottom)


def _combine_rgn(dest, src1, src2, mode: int) -> int:
    """调用 GDI32 CombineRgn 合并区域"""
    return _gdi32.CombineRgn(dest, src1, src2, mode)


def _delete_object(obj) -> bool:
    """调用 GDI32 DeleteObject 删除 GDI 对象"""
    return _gdi32.DeleteObject(obj)


class BlockOverlay:
    """
    全屏透明覆盖窗口 - 拦截除"星辰RPA"窗口外的所有鼠标操作。

    使用方式::

        from astronverse.picker.core.block_overlay import block_overlay

        block_overlay.show()   # 显示覆盖窗口，开始拦截
        block_overlay.hide()   # 隐藏覆盖窗口，停止拦截

    调试热键: Ctrl+Shift+F12 可强制关闭覆盖窗口
    """

    _CLASS_NAME = "AstronRPABlockOverlay"
    _RPA_WINDOW_KEYWORD = "星辰RPA"

    # 区域刷新间隔（毫秒）
    _REGION_UPDATE_MS = 300

    # 调试热键 & 定时器 ID
    _HOTKEY_ID = 9901
    _TIMER_ID = 9901

    def __init__(self):
        self._hwnd: int | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._class_registered = False

        # 虚拟屏幕起始坐标（用于坐标转换）
        self._vx = 0
        self._vy = 0

        # 首次搜索标志（控制日志级别）
        self._first_search = True

    def show(self):
        """显示覆盖窗口，开始拦截所有非"星辰RPA"区域的鼠标操作"""
        with self._lock:
            if self._hwnd is not None:
                logger.info("[BlockOverlay] 覆盖窗口已存在，跳过创建")
                return

        self._first_search = True
        self._thread = threading.Thread(
            target=self._window_thread,
            daemon=True,
            name="BlockOverlayThread",
        )
        self._thread.start()
        logger.info("[BlockOverlay] 覆盖窗口线程已启动")

    def hide(self):
        """隐藏并销毁覆盖窗口，恢复所有区域的鼠标操作"""
        with self._lock:
            hwnd = self._hwnd

        if not hwnd:
            return

        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception as e:
            logger.error(f"[BlockOverlay] 发送关闭消息失败: {e}")

        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

        logger.info("[BlockOverlay] 覆盖窗口已关闭")

    @property
    def is_active(self) -> bool:
        """覆盖窗口是否处于活动状态"""
        return self._hwnd is not None

    # ───────────── 窗口线程 ─────────────

    def _window_thread(self):
        """在独立线程中创建覆盖窗口并运行消息循环"""
        try:
            self._ensure_class_registered()
            self._create_overlay_window()

            # 消息循环（阻塞直到 PostQuitMessage）
            win32gui.PumpMessages()
        except Exception as e:
            logger.error(f"[BlockOverlay] 窗口线程异常: {e}\n{traceback.format_exc()}")
        finally:
            with self._lock:
                self._hwnd = None
            logger.info("[BlockOverlay] 窗口线程已退出")

    def _ensure_class_registered(self):
        """注册窗口类（幂等）"""
        if self._class_registered:
            return

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = self._CLASS_NAME
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = 0

        try:
            win32gui.RegisterClass(wc)
            self._class_registered = True
        except Exception as e:
            # ERROR_CLASS_ALREADY_EXISTS (1410)
            if getattr(e, "winerror", 0) == 1410:
                self._class_registered = True
            else:
                raise

    def _create_overlay_window(self):
        """创建全屏透明覆盖窗口并注册热键/定时器"""
        # 虚拟屏幕尺寸（多显示器全覆盖）
        self._vx = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self._vy = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        vw = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        vh = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        ex_style = (
            win32con.WS_EX_LAYERED  # 分层窗口（支持透明）
            | win32con.WS_EX_TOPMOST  # 始终置顶
            | win32con.WS_EX_TOOLWINDOW  # 不在任务栏显示
            | WS_EX_NOACTIVATE  # 不抢夺焦点
        )

        hwnd = win32gui.CreateWindowEx(
            ex_style,
            self._CLASS_NAME,
            "",  # 无标题
            win32con.WS_POPUP,  # 无边框弹出窗口
            self._vx,
            self._vy,
            vw,
            vh,
            0,
            0,
            0,
            None,
        )

        if not hwnd:
            raise RuntimeError("CreateWindowEx 创建覆盖窗口失败")

        # 设置透明度 1/255 ≈ 0.4%，肉眼不可见
        _user32.SetLayeredWindowAttributes(hwnd, 0, 1, LWA_ALPHA)

        # 显示但不激活
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
        win32gui.UpdateWindow(hwnd)

        with self._lock:
            self._hwnd = hwnd

        # ── 注册调试热键: Ctrl+Shift+F12──
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        VK_F12 = 0x7B
        hotkey_ok = _user32.RegisterHotKey(hwnd, self._HOTKEY_ID, MOD_CONTROL | MOD_SHIFT, VK_F12)
        if hotkey_ok:
            logger.info("[BlockOverlay] 调试热键 Ctrl+Shift+F12 已注册（可强制关闭覆盖窗口）")
        else:
            logger.warning("[BlockOverlay] 调试热键注册失败（可能已被占用）")

        # ── 设置定时器，定期刷新区域 ──
        _user32.SetTimer(hwnd, self._TIMER_ID, self._REGION_UPDATE_MS, None)

        # ── 首次更新区域 ──
        self._update_window_region(hwnd)

        logger.info(f"[BlockOverlay] 覆盖窗口已创建 hwnd={hwnd}, 虚拟屏幕=({self._vx}, {self._vy}, {vw}x{vh})")

    # ───────────── 窗口过程 ─────────────

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """窗口过程 - 处理热键、定时器、关闭事件"""
        try:
            if msg == WM_HOTKEY and wparam == self._HOTKEY_ID:
                logger.info("[BlockOverlay] 收到调试热键 Ctrl+Shift+F12，强制关闭覆盖窗口")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                return 0

            elif msg == win32con.WM_TIMER and wparam == self._TIMER_ID:
                self._update_window_region(hwnd)
                return 0

            elif msg == win32con.WM_CLOSE:
                # 清理定时器和热键
                _user32.KillTimer(hwnd, self._TIMER_ID)
                _user32.UnregisterHotKey(hwnd, self._HOTKEY_ID)
                win32gui.DestroyWindow(hwnd)
                return 0

            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
                return 0

        except Exception as e:
            logger.error(f"[BlockOverlay] WndProc 异常: {e}")

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # ───────────── 区域更新（核心逻辑） ─────────────

    def _update_window_region(self, hwnd):
        """
        更新窗口区域: 全屏区域 - RPA 窗口区域。

        将 RPA 窗口所在的矩形从覆盖窗口上"挖掉"，
        使该区域物理上不存在覆盖窗口，鼠标点击直接穿透到下方的 RPA 客户端。

        使用 ctypes 直接调用 GDI32 的 CreateRectRgn / CombineRgn / DeleteObject，
        因为 pywin32 的 win32gui 模块不一定导出这些 GDI 函数。
        """
        try:
            vw = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            vh = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

            # 创建全屏区域（窗口相对坐标，从 0,0 开始）
            full_rgn = _create_rect_rgn(0, 0, vw, vh)
            if not full_rgn:
                logger.error("[BlockOverlay] CreateRectRgn(全屏) 返回 NULL")
                return

            # 查找 RPA 窗口并在区域上挖洞
            rpa_rects = self._find_rpa_window_rects()

            for rect in rpa_rects:
                # 屏幕坐标 → 窗口相对坐标（减去窗口起始位置）
                rx1 = rect[0] - self._vx
                ry1 = rect[1] - self._vy
                rx2 = rect[2] - self._vx
                ry2 = rect[3] - self._vy

                rpa_rgn = _create_rect_rgn(rx1, ry1, rx2, ry2)
                if rpa_rgn:
                    _combine_rgn(full_rgn, full_rgn, rpa_rgn, RGN_DIFF)
                    _delete_object(rpa_rgn)

            # 应用区域（系统接管 full_rgn 的生命周期，不需要 DeleteObject）
            _user32.SetWindowRgn(hwnd, full_rgn, True)

        except Exception as e:
            logger.error(f"[BlockOverlay] 更新窗口区域失败: {e}\n{traceback.format_exc()}")

    # ───────────── RPA 窗口查找 ─────────────

    def _find_rpa_window_rects(self) -> list[tuple]:
        """
        查找所有"星辰RPA"相关窗口的屏幕矩形。

        策略:
        1. 枚举所有可见顶层窗口
        2. 找到标题包含"星辰RPA"的窗口，记录其进程 ID
        3. 收集属于这些进程的所有可见窗口矩形（含弹窗/对话框）
        """
        window_list: list[tuple[int, int, str]] = []  # (hwnd, pid, title)

        def _enum_callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            # 排除自己
            if hwnd == self._hwnd:
                return True
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                title = win32gui.GetWindowText(hwnd)
                window_list.append((hwnd, pid, title))
            except Exception:
                pass
            return True

        try:
            win32gui.EnumWindows(_enum_callback, None)
        except Exception as e:
            logger.error(f"[BlockOverlay] 枚举窗口失败: {e}")
            return []

        # ── 阶段1: 收集 RPA 进程 ID ──
        rpa_pids: set[int] = set()
        for _, pid, title in window_list:
            if self._RPA_WINDOW_KEYWORD in title:
                rpa_pids.add(pid)

        # ── 首次搜索或未找到时输出详细日志 ──
        if self._first_search or not rpa_pids:
            self._first_search = False
            if rpa_pids:
                matched = [(t, p) for _, p, t in window_list if self._RPA_WINDOW_KEYWORD in t]
                for title, pid in matched:
                    logger.info(f"[BlockOverlay] 匹配到RPA窗口: title='{title}', pid={pid}")
            else:
                logger.warning(
                    f"[BlockOverlay] 未找到包含'{self._RPA_WINDOW_KEYWORD}'的窗口! 共扫描 {len(window_list)} 个可见窗口"
                )
                # 输出有标题的窗口帮助调试
                titled = [(t, p) for _, p, t in window_list if t.strip()]
                for title, pid in titled[:15]:
                    logger.warning(f"[BlockOverlay]   可见窗口: title='{title}', pid={pid}")

        if not rpa_pids:
            return []

        # ── 阶段2: 收集 RPA 进程的所有可见窗口矩形 ──
        rects: list[tuple] = []
        for hwnd, pid, _ in window_list:
            if pid in rpa_pids:
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    rects.append(rect)
                except Exception:
                    pass

        return rects


# 模块级单例
block_overlay = BlockOverlay()
