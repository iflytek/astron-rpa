import asyncio
import os
import time
from typing import AsyncGenerator, Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from astronverse.scheduler.logger import logger


class ExcelFileHandler(FileSystemEventHandler):
    """Excel 文件变更处理器"""

    def __init__(
        self,
        target_file: str,
        on_modified: Optional[Callable[[str], None]] = None,
        on_deleted: Optional[Callable[[str], None]] = None,
        debounce_seconds: float = 0.5,
    ):
        """
        初始化文件变更处理器

        Args:
            target_file: 要监听的目标文件路径
            on_modified: 文件修改时的回调函数
            on_deleted: 文件删除时的回调函数
            debounce_seconds: 防抖时间（秒），避免短时间内重复触发
        """
        super().__init__()
        # Windows 路径不区分大小写，统一转为小写比较
        self.target_file = os.path.normpath(target_file).lower()
        self._on_modified_callback = on_modified
        self._on_deleted_callback = on_deleted
        self.debounce_seconds = debounce_seconds

        # 防抖控制
        self._last_modified_time = 0
        self._ignore_until = 0  # 用于忽略自己写入导致的变更

    def pause_watching(self, duration: float = 1.0):
        """
        暂停监听一段时间，用于避免自己写入触发的变更

        Args:
            duration: 暂停时间（秒）
        """
        self._ignore_until = time.time() + duration

    def _should_process(self, event_path: str) -> bool:
        """检查是否应该处理此事件"""
        # Windows 路径不区分大小写，统一转为小写比较
        normalized_path = os.path.normpath(event_path).lower()

        # 检查是否是目标文件
        if normalized_path != self.target_file:
            return False

        # 检查是否在忽略期间
        if time.time() < self._ignore_until:
            logger.debug(f"Ignoring event during pause period: {event_path}")
            return False

        return True

    def _debounce_check(self) -> bool:
        """防抖检查"""
        current_time = time.time()
        if current_time - self._last_modified_time < self.debounce_seconds:
            return False
        self._last_modified_time = current_time
        return True

    def on_modified(self, event: FileSystemEvent):
        """文件修改事件"""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        if not self._debounce_check():
            return

        logger.info(f"File modified: {event.src_path}")
        if self._on_modified_callback:
            self._on_modified_callback(event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """文件删除事件"""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        logger.info(f"File deleted: {event.src_path}")
        if self._on_deleted_callback:
            self._on_deleted_callback(event.src_path)

    def on_created(self, event: FileSystemEvent):
        """文件创建事件 - Excel 保存时可能会先删除再创建"""
        if event.is_directory:
            return

        if not self._should_process(event.src_path):
            return

        if not self._debounce_check():
            return

        logger.info(f"File created (treated as modified): {event.src_path}")
        if self._on_modified_callback:
            self._on_modified_callback(event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """文件移动/重命名事件 - Excel 保存时可能会用临时文件重命名"""
        if event.is_directory:
            return

        # 检查目标路径是否是我们监听的文件
        dest_path = getattr(event, "dest_path", None)
        if dest_path and os.path.normpath(dest_path).lower() == self.target_file:
            if not self._debounce_check():
                return

            logger.info(f"File moved to target (treated as modified): {dest_path}")
            if self._on_modified_callback:
                self._on_modified_callback(dest_path)


class FileWatcher:
    """文件监听器"""

    def __init__(self):
        """初始化文件监听器"""
        self._observers: dict[str, Observer] = {}
        self._handlers: dict[str, ExcelFileHandler] = {}

    def start_watching(
        self,
        file_path: str,
        on_modified: Optional[Callable[[str], None]] = None,
        on_deleted: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        开始监听指定文件

        Args:
            file_path: 要监听的文件路径
            on_modified: 文件修改时的回调函数
            on_deleted: 文件删除时的回调函数

        Returns:
            是否成功开始监听
        """
        file_path = os.path.normpath(file_path)

        # 如果已经在监听，先停止
        if file_path in self._observers:
            self._stop_watching_internal(file_path)

        # 获取文件所在目录
        watch_dir = os.path.dirname(file_path)
        if not watch_dir:
            watch_dir = "."

        if not os.path.exists(watch_dir):
            logger.error(f"Watch directory does not exist: {watch_dir}")
            return False

        # 创建事件处理器
        handler = ExcelFileHandler(
            target_file=file_path,
            on_modified=on_modified,
            on_deleted=on_deleted,
        )

        # 创建并启动观察者
        observer = Observer()
        observer.schedule(handler, watch_dir, recursive=False)
        observer.start()

        self._observers[file_path] = observer
        self._handlers[file_path] = handler

        logger.info(f"Started watching file: {file_path}")
        return True

    def stop_watching(self, file_path: str) -> bool:
        """
        停止监听指定文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功停止
        """
        file_path = os.path.normpath(file_path)
        return self._stop_watching_internal(file_path)

    def _stop_watching_internal(self, file_path: str) -> bool:
        """内部方法：停止监听"""
        if file_path not in self._observers:
            return False

        observer = self._observers.pop(file_path)
        self._handlers.pop(file_path, None)

        observer.stop()
        observer.join(timeout=2)

        logger.info(f"Stopped watching file: {file_path}")
        return True

    def pause_watching(self, file_path: str, duration: float = 1.0):
        """
        暂停监听指定文件一段时间

        Args:
            file_path: 文件路径
            duration: 暂停时间（秒）
        """
        file_path = os.path.normpath(file_path)

        handler = self._handlers.get(file_path)
        if handler:
            handler.pause_watching(duration)

    def is_watching(self, file_path: str) -> bool:
        """
        检查是否正在监听指定文件

        Args:
            file_path: 文件路径

        Returns:
            是否正在监听
        """
        file_path = os.path.normpath(file_path)
        return file_path in self._observers

    def stop_all(self):
        """停止所有监听"""
        for file_path in list(self._observers.keys()):
            self._stop_watching_internal(file_path)

        logger.info("Stopped all file watchers")


class AsyncFileWatcher:
    """异步文件监听器，用于 SSE 流式推送"""

    def __init__(self, file_path: str, debounce_delay: float = 0.5):
        """
        初始化异步文件监听器

        Args:
            file_path: 要监听的文件路径
            debounce_delay: 防抖延迟时间（秒），文件修改完成后等待此时间再触发事件
        """
        self.file_path = os.path.normpath(file_path)
        self._queue: asyncio.Queue = asyncio.Queue()
        self._observer: Optional[Observer] = None
        self._handler: Optional[ExcelFileHandler] = None
        self._running = False
        self._ignore_until = 0
        self._debounce_delay = debounce_delay
        self._pending_task: Optional[asyncio.Task] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def pause_watching(self, duration: float = 1.0):
        """
        暂停监听一段时间

        Args:
            duration: 暂停时间（秒）
        """
        self._ignore_until = time.time() + duration
        if self._handler:
            self._handler.pause_watching(duration)

    async def start(self) -> AsyncGenerator[dict, None]:
        """
        启动监听并异步生成事件

        Yields:
            文件变更事件字典
        """
        if self._running:
            return

        self._running = True
        self._event_loop = asyncio.get_event_loop()

        # 延迟触发任务
        async def _delayed_trigger(event_data: dict):
            """延迟触发事件，等待防抖时间后放入队列"""
            try:
                await asyncio.sleep(self._debounce_delay)
                # 检查是否仍在运行状态
                if self._running:
                    try:
                        self._queue.put_nowait(event_data)
                    except asyncio.QueueFull:
                        logger.warning("Event queue is full, dropping event")
            except asyncio.CancelledError:
                # 任务被取消是正常的，不需要记录
                pass

        # 创建回调函数
        def on_modified(path: str):
            """文件修改回调 - 使用延迟触发机制"""
            if time.time() < self._ignore_until:
                return

            # 取消之前的延迟任务
            if self._pending_task and not self._pending_task.done():
                self._pending_task.cancel()

            # 创建新的延迟任务
            event_data = {"type": "file_changed", "path": path}
            self._pending_task = self._event_loop.create_task(_delayed_trigger(event_data))

        def on_deleted(path: str):
            """文件删除回调 - 立即触发，不需要延迟"""
            try:
                self._queue.put_nowait({"type": "file_deleted", "path": path})
            except asyncio.QueueFull:
                logger.warning("Event queue is full, dropping delete event")

        # 获取文件所在目录
        watch_dir = os.path.dirname(self.file_path)
        if not watch_dir:
            watch_dir = "."

        # 创建事件处理器
        # 注意：ExcelFileHandler 的防抖时间设置为 0.1 秒，主要用于减少事件频率
        # 真正的延迟触发由 AsyncFileWatcher 的延迟机制处理
        self._handler = ExcelFileHandler(
            target_file=self.file_path,
            on_modified=on_modified,
            on_deleted=on_deleted,
            debounce_seconds=0.1,  # 缩短防抖时间，避免过滤掉最后一个事件
        )

        # 创建并启动观察者
        self._observer = Observer()
        self._observer.schedule(self._handler, watch_dir, recursive=False)
        self._observer.start()

        logger.info(f"AsyncFileWatcher started for: {self.file_path}")

        try:
            while self._running:
                try:
                    # 等待事件，设置超时以便定期检查运行状态
                    event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                    yield event
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield {"type": "heartbeat"}
                except Exception as e:
                    logger.error(f"Error in AsyncFileWatcher: {e}")
                    break
        finally:
            self.stop()

    def stop(self):
        """停止监听"""
        self._running = False

        # 取消待处理的延迟任务
        if self._pending_task and not self._pending_task.done():
            self._pending_task.cancel()

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None

        self._handler = None
        self._event_loop = None
        logger.info(f"AsyncFileWatcher stopped for: {self.file_path}")


# 全局文件监听器实例
_file_watcher: Optional[FileWatcher] = None


def get_file_watcher() -> FileWatcher:
    """获取全局文件监听器实例"""
    global _file_watcher
    if _file_watcher is None:
        _file_watcher = FileWatcher()
    return _file_watcher
