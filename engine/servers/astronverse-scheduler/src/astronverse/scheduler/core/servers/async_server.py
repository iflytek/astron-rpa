import time

from astronverse.scheduler import ServerLevel
from astronverse.scheduler.core.schduler.venv import VenvManager
from astronverse.scheduler.core.server import IServer
from astronverse.scheduler.core.setup.setup import Process
from astronverse.scheduler.core.terminal.terminal import Terminal
from astronverse.scheduler.logger import logger


class RpaSchedulerAsyncServer(IServer):
    def __init__(self, svc):
        super().__init__(
            svc=svc,
            name="astronverse.scheduler_async",
            level=ServerLevel.NORMAL,
            run_is_async=True,
        )

    def run(self):
        logger.debug("[RpaSchedulerAsync] 守护循环已启动")
        i = 1
        while True:
            try:
                # 创建空的虚拟环境
                try:
                    if not self.svc.is_venv:
                        VenvManager().create_new(self.svc)
                except Exception as e:
                    logger.exception("VenvManager error: {}".format(e))

                # 定时注册服务
                try:
                    if i % 30 == 0:
                        logger.debug(f"[RpaSchedulerAsync] register_server tick={i}")
                        self.svc.register_server()
                except Exception as e:
                    logger.exception("register_server error: {}".format(e))
            except Exception as e:
                pass
            finally:
                i += 1
                if i > 60:
                    i = 0
                time.sleep(1)


class TerminalAsyncServer(IServer):
    def __init__(self, svc):
        super().__init__(svc=svc, name="terminal_async", level=ServerLevel.NORMAL, run_is_async=True)

    def run(self):
        logger.debug("[TerminalAsync] 守护循环已启动")
        i = 1
        while True:
            try:
                if i % 10 == 0:
                    res = Terminal.upload(self.svc)
                    if res == "TERMINAL_NOT_FOUND":
                        logger.info("[TerminalAsync] 终端未注册，执行 Terminal.register")
                        Terminal.register(self.svc)
            except Exception as e:
                logger.exception("Terminal upload error: {}".format(e))
            finally:
                i += 1
                if i > 60:
                    i = 0
                time.sleep(1)


class CheckPickProcessAliveServer(IServer):
    def __init__(self, svc):
        super().__init__(
            svc=svc,
            name="check_pick_process_alive",
            level=ServerLevel.NORMAL,
            run_is_async=True,
        )

    def run(self):
        logger.debug("[CheckPickProcessAlive] 已启动")
        while True:
            try:
                if self.svc.picker.start:
                    if self.svc.picker.vision_picker:
                        if not self.svc.picker.vision_picker.is_alive():
                            logger.debug("[CheckPickProcessAlive] 重启 vision_picker")
                            self.svc.picker.vision_picker.run()
                    if self.svc.picker.app_picker:
                        if not self.svc.picker.app_picker.is_alive():
                            logger.debug("[CheckPickProcessAlive] 重启 app_picker")
                            self.svc.picker.app_picker.run()
                    if self.svc.picker.highlighter:
                        if not self.svc.picker.highlighter.is_alive():
                            logger.debug("[CheckPickProcessAlive] 重启 highlighter")
                            self.svc.picker.highlighter.run()
            except Exception as e:
                logger.exception("check_pick_process error: {}".format(e))
            finally:
                time.sleep(1)


class CheckStartPidExitsServer(IServer):
    def __init__(self, svc):
        super().__init__(
            svc=svc,
            name="check_start_pid",
            level=ServerLevel.NORMAL,
            run_is_async=True,
        )

    def run(self):
        logger.debug("[CheckStartPidExits] 已启动")
        Process.pid_exist_check()
