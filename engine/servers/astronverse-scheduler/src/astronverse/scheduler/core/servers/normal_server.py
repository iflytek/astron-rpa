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

        self.proc = SubPopen(
            name="trigger",
            cmd=[self.svc.config.python_core, "-m", "astronverse.trigger"],
        )
        self.proc.set_param("port", self.port)
        self.proc.set_param("gateway_port", self.svc.rpa_route_port)
        self.proc.set_param("terminal_mode", "y" if self.svc.terminal_mod else "n")
        self.proc.set_param("terminal_id", terminal_id)
        self.proc.run()

    def health(self) -> bool:
        if not self.proc.is_alive():
            return False

        response = requests.get(
            "http://127.0.0.1:{}/{}/task/health".format(self.svc.rpa_route_port, ComponentType.TRIGGER.name.lower())
        )
        status_code = response.status_code
        if status_code != 200:
            self.err_time += 1
        else:
            self.err_time = 0

        if self.err_time >= self.err_max_time:
            return False

        return True

    def close(self):
        if self.proc:
            self.proc.kill()

    def recover(self):
        # 先关闭
        if self.proc:
            self.proc.kill()

        # 再重启
        self.run()

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
            self.svc.logger.error("update_config error: %s", e)


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
            return
        if not self.svc.start_watch:
            return

        try:
            from astronverse.scheduler.core.terminal.vnc import VNC

            self.vnc = VNC(self.svc, self.vnc_port, self.vnc_ws_port, pwd=self.vnc_pwd)
            if not self.vnc.start():
                self.vnc = None
        except Exception as e:
            self.vnc = None

    def close(self):
        if self.vnc:
            self.vnc.stop()

    def health(self) -> bool:
        if not self.svc.terminal_mod:
            return True
        if not self.svc.start_watch:
            return True

        # 如果端口可用说明系统已经挂了
        if check_port(self.vnc_port) or check_port(self.vnc_ws_port):
            return False
        return True

    def recover(self):
        """监控检查恢复"""
        if self.vnc:
            self.vnc.stop()
        self.run()
