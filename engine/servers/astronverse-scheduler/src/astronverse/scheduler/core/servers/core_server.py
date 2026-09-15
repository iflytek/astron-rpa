from pathlib import Path

import requests
from astronverse.scheduler import ComponentType, ServerLevel
from astronverse.scheduler.core.executor.managed_execution import ManagedExecution
from astronverse.scheduler.core.route.proxy import get_cmd
from astronverse.scheduler.core.route.remote_transport import RemoteTransport
from astronverse.scheduler.core.server import IServer
from astronverse.scheduler.utils.subprocess import SubPopen


class RpaRouteServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.remote_transport = None
        self.port = 0
        super().__init__(svc=svc, name="rpa_route", level=ServerLevel.CORE, run_is_async=False)

    def run(self):
        self.port = self.svc.rpa_route_port
        if not hasattr(self.svc, "managed_execution"):
            self.svc.managed_execution = ManagedExecution(
                self.svc.executor_mg, Path.cwd() / ".executions", self.svc.config.remote_addr
            )
        self.remote_transport = RemoteTransport(self.svc.config.remote_addr, self.svc.managed_execution.handle)
        remote_port = self.remote_transport.start()

        self.proc = SubPopen(name="rpa_route", cmd=[get_cmd()])
        self.proc.set_param("port", self.port)

        # The binary routes local modules; verified upstream HTTPS/WSS and
        # origin-scoped sessions are owned by RemoteTransport.
        self.proc.set_param("httpProtocol", "http")
        self.proc.set_param("wsProtocol", "ws")
        self.proc.set_param("remoteHost", f"127.0.0.1:{remote_port}")
        try:
            self.proc.run()
        except Exception:
            self.remote_transport.close()
            raise

    def health(self) -> bool:
        if not self.proc.is_alive() or not self.remote_transport.is_alive():
            return False
        return True

    def recover(self):
        # 先关闭
        self.proc.kill()
        self.remote_transport.close()

        # 再重启
        self.run()
        self.svc.register_server()


class RpaBrowserConnectorServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        self.err_time = 0
        self.err_max_time = 3
        super().__init__(svc=svc, name="rpa_route", level=ServerLevel.CORE, run_is_async=False)

    def run(self):
        self.port = self.svc.connector_port

        self.proc = SubPopen(
            name="browser_bridge",
            cmd=[self.svc.config.python_core, "-m", "astronverse.browser_bridge"],
        )
        self.proc.set_param("port", self.port)
        self.proc.run()

    def health(self) -> bool:
        if not self.proc.is_alive():
            return False

        response = requests.get(
            "http://127.0.0.1:{}/{}/browser/health".format(
                self.svc.rpa_route_port, ComponentType.BROWSER_CONNECTOR.name.lower()
            )
        )
        status_code = response.status_code
        if status_code != 200:
            self.err_time += 1
        else:
            self.err_time = 0

        if self.err_time >= self.err_max_time:
            return False

        return True

    def recover(self):
        # 先关闭
        self.proc.kill()

        # 再重启
        self.run()
