import threading
import time

from astronverse.picker.logger import logger


class HoverCore:
    """悬停检测核心 - 类比 EventCore，独立线程监听鼠标位置"""

    def __init__(self):
        self._hover_flag = False
        self._thread: threading.Thread = None
        self._stop = False
        self._closed = True
        self.threshold: float = 0.2  # 悬停阈值（秒）
        self._cur_rect = None  # 外部通过 update_rect 更新
        self._lock = threading.Lock()

    def start(self) -> bool:
        """启动悬停检测线程"""
        if not self._closed:
            return False

        logger.info("HoverCore start")
        self._stop = False
        self._hover_flag = False
        self._closed = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def close(self) -> bool:
        """停止线程"""
        if self._closed:
            return False

        logger.info("HoverCore close")
        self._stop = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self._hover_flag = False
        self._closed = True
        return True

    def is_hover(self) -> bool:
        """主循环调用，检查是否悬停超时（类比 EventCore.is_focus）"""
        return self._hover_flag

    def reset(self):
        """重置悬停状态（每次新拾取开始时调用）"""
        self._hover_flag = False

    def update_rect(self, rect):
        """外部更新当前绘框位置"""
        with self._lock:
            self._cur_rect = rect

    def _loop(self):
        """后台线程：持续检测鼠标位置 vs cur_rect"""
        from astronverse.picker import Point
        from astronverse.picker.engines.uia_picker import UIAOperate

        hover_start_time = None
        last_rect = None

        while not self._stop:
            try:
                with self._lock:
                    cur_rect = self._cur_rect

                if not cur_rect:
                    time.sleep(0.05)
                    continue

                cur_x, cur_y = UIAOperate.get_cursor_pos()
                is_inside = cur_rect.contains(Point(cur_x, cur_y))

                if is_inside:
                    if last_rect != cur_rect:
                        # 绘框变了，重置计时
                        hover_start_time = time.time()
                        last_rect = cur_rect
                    elif hover_start_time and time.time() - hover_start_time >= self.threshold:
                        # 悬停超时，设标志位
                        self._hover_flag = True
                else:
                    # 鼠标移出，重置计时
                    hover_start_time = None
                    last_rect = None

            except Exception as e:
                logger.error(f"HoverCore 检测出错: {e}")

            time.sleep(0.05)
