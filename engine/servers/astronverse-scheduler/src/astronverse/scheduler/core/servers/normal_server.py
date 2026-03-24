import requests
from astronverse.scheduler import ComponentType, ServerLevel
from astronverse.scheduler.core.server import IServer
from astronverse.scheduler.core.terminal.terminal import terminal_id, terminal_pwd
from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.subprocess import SubPopen
from astronverse.scheduler.utils.utils import check_port


class TriggerServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        self.err_time = 0
        self.err_max_time = 3
        super().__init__(svc=svc, name="trigger", level=ServerLevel.NORMAL, run_is_async=False)

    def run(self):
        self.port = self.svc.trigger_port
        logger.info(f"[TriggerServer] 启动 trigger port={self.port} gateway={self.svc.rpa_route_port}")

        self.proc = SubPopen(
            name="trigger",
            cmd=[self.svc.config.python_core, "-m", "astronverse.trigger"],
        )
        self.proc.set_param("port", self.port)
        self.proc.set_param("gateway_port", self.svc.rpa_route_port)
        self.proc.set_param("terminal_mode", "y" if self.svc.terminal_mod else "n")
        self.proc.set_param("terminal_id", terminal_id)
        self.proc.run()
        self.err_time = 0
        alive = self.proc.is_alive() if self.proc else False
        logger.info(f"[TriggerServer] 子进程 alive={alive}")

    def health(self) -> bool:
        if not self.proc or not self.proc.is_alive():
            logger.debug("[TriggerServer] 健康检查 子进程未存活")
            return False

        url = "http://127.0.0.1:{}/{}/task/health".format(self.svc.rpa_route_port, ComponentType.TRIGGER.name.lower())
        try:
            response = requests.get(url, timeout=5)
        except Exception as e:
            self.err_time += 1
            logger.debug(f"[TriggerServer] health 请求失败 {self.err_time}/{self.err_max_time} {e}")
            if self.err_time >= self.err_max_time:
                logger.error("[TriggerServer] 健康检查失败(连续请求异常)")
                return False
            return True

        status_code = response.status_code
        if status_code != 200:
            self.err_time += 1
            logger.debug(f"[TriggerServer] health HTTP {status_code} 失败 {self.err_time}/{self.err_max_time}")
        else:
            if self.err_time:
                logger.info("[TriggerServer] health 已恢复 HTTP 200")
            self.err_time = 0

        if self.err_time >= self.err_max_time:
            logger.error("[TriggerServer] 健康检查失败(连续非200)")
            return False

        return True

    def close(self):
        if self.proc:
            self.proc.kill()

    def recover(self):
        logger.debug("[TriggerServer] recover kill+run")
        if self.proc:
            self.proc.kill()
        self.run()
        logger.debug("[TriggerServer] recover 结束")

    def update_config(self, terminal_mod: bool):
        try:
            response = requests.post(
                "http://127.0.0.1:{}/{}/config/update".format(
                    self.svc.rpa_route_port, ComponentType.TRIGGER.name.lower()
                ),
                json={"terminal_mode": terminal_mod},
            )
            status_code = response.status_code
            if status_code != 200:
                self.err_time += 1
            else:
                self.err_time = 0

            if self.err_time >= self.err_max_time:
                return False
            return True
        except Exception as e:
            self.svc.logger.error(f"update_config error: {e}")


class VNCServer(IServer):
    def __init__(self, svc):
        self.svc = svc
        self.vnc_port: int = svc.get_validate_port(None)
        self.vnc_ws_port: int = svc.get_validate_port(None)
        self.vnc_pwd: str = terminal_pwd
        self.vnc = None
        super().__init__(svc=svc, name="vnc", level=ServerLevel.NORMAL, run_is_async=False)
        logger.info(f"VNCServer init: {self.vnc_port}, {self.vnc_ws_port}, {self.vnc_pwd}")

    def run(self):
        if not self.svc.terminal_mod:
            logger.info("[VNCServer] 跳过启动 terminal_mod=False")
            return
        if not self.svc.start_watch:
            logger.info("[VNCServer] 跳过启动 start_watch=False")
            return

        logger.info(
            "[VNCServer] 启动 VNC port=%s ws_port=%s",
            self.vnc_port,
            self.vnc_ws_port,
        )
        try:
            from astronverse.scheduler.core.terminal.vnc import VNC

            self.vnc = VNC(self.svc, self.vnc_port, self.vnc_ws_port, pwd=self.vnc_pwd)
            if not self.vnc.start():
                logger.error("[VNCServer] VNC.start() 返回 False")
                self.vnc = None
            else:
                logger.info("[VNCServer] VNC 已启动")
        except Exception as e:
            logger.exception(f"[VNCServer] 启动异常: {e}")
            self.vnc = None

    def close(self):
        if self.vnc:
            self.vnc.stop()

    def health(self) -> bool:
        if not self.svc.terminal_mod:
            return True
        if not self.svc.start_watch:
            return True

        if check_port(self.vnc_port) or check_port(self.vnc_ws_port):
            logger.debug(f"[VNCServer] 健康检查 端口不可连 vnc={self.vnc_port} ws={self.vnc_ws_port}")
            return False
        return True

    def recover(self):
        logger.debug("[VNCServer] recover stop+run")
        if self.vnc:
            self.vnc.stop()
        self.run()
        logger.debug("[VNCServer] recover 结束")
