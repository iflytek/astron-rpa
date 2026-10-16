import threading
from abc import ABC, abstractmethod

from astronverse.scheduler import ServerLevel
from astronverse.scheduler.logger import logger


class IServer(ABC):
    def __init__(
        self,
        svc=None,
        name: str = "",
        level: ServerLevel = ServerLevel.NORMAL,
        run_is_async: bool = False,
    ):
        # 名称
        self.name = name
        # 等级
        self.level = level
        # 业务上下文
        self.svc = svc
        # run是否需要异步执行
        self.run_is_async = run_is_async
        # recover
        self.recover_ing = False

    @abstractmethod
    def run(self):
        """启动服务，不能包含阻塞"""
        pass

    def health(self) -> bool:
        """健康检擦 10s 触发一次 健康就返回True"""
        return True

    def recover(self):
        """监控检查恢复"""
        return None

    def stop(self):
        """Stop resources owned by this server."""
        close = getattr(self, "close", None)
        if close:
            close()


class ServerManager:
    """服务管理"""

    def __init__(self, svc):
        self.server_list = []
        self.svc = svc
        self.stop_event = threading.Event()
        self.threads = []
        self.svc.stop_event = self.stop_event

    def register(self, server: IServer):
        """注册"""
        self.server_list.append(server)
        return self

    def check(self):
        """检测"""
        while not self.stop_event.wait(10):
            try:
                for server in self.server_list:
                    if self.stop_event.is_set():
                        return
                    if not server.health() and server.recover_ing is False:
                        logger.info(f"{server.name} is not health, start recover")
                        server.recover_ing = True
                        server.recover()
                        server.recover_ing = False
            except Exception as e:
                pass

    def _run_server(self, server):
        try:
            server.run()
        except Exception:
            if not self.stop_event.is_set():
                logger.exception("{} stopped unexpectedly".format(server.name))

    def _start_thread(self, target, *args):
        thread = threading.Thread(target=target, args=args, daemon=True)
        self.threads.append(thread)
        thread.start()

    def run(self):
        # 1. 先启动code核心的非异步
        for c_server in self.server_list:
            if self.stop_event.is_set():
                return self
            if not c_server.run_is_async and c_server.level == ServerLevel.CORE:
                c_server.run()

        def async_run():
            while not self.svc.route_server_is_start and not self.stop_event.wait(1):
                pass
            if self.stop_event.is_set():
                return

            # 2. 启动普通的的非异步
            for n_server in self.server_list:
                if self.stop_event.is_set():
                    return
                if not n_server.run_is_async and n_server.level == ServerLevel.NORMAL:
                    self._run_server(n_server)

            # 3. 启动异步
            for a_server in self.server_list:
                if self.stop_event.is_set():
                    return
                if a_server.run_is_async:
                    self._start_thread(self._run_server, a_server)

        self._start_thread(async_run)
        self._start_thread(self.check)
        return self

    def stop(self):
        if self.stop_event.is_set():
            return

        self.stop_event.set()
        for server in reversed(self.server_list):
            try:
                server.stop()
            except Exception:
                logger.exception("{} stop failed".format(server.name))

        try:
            self.svc.stop()
        except Exception:
            logger.exception("scheduler resources stop failed")

        current_thread = threading.current_thread()
        for thread in self.threads:
            if thread is not current_thread:
                thread.join(timeout=2)
