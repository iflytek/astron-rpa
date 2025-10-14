import requests
from astronverse.scheduler import ComponentType, ServerLevel
from astronverse.scheduler.core.server import IServer
from astronverse.scheduler.core.terminal.terminal import terminal_id
from astronverse.scheduler.utils.subprocess import SubPopen


class TriggerServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        self.err_time = 0
        self.err_max_time = 3
        super().__init__(svc=svc, name="rpa_trigger", level=ServerLevel.NORMAL, run_is_async=False)

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
