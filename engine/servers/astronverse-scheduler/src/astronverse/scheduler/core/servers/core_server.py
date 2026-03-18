from urllib.parse import urlparse

import requests
from astronverse.scheduler import ComponentType, ServerLevel
from astronverse.scheduler.core.router.proxy import get_cmd
from astronverse.scheduler.core.server import IServer
from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.subprocess import SubPopen


class RpaRouteServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        super().__init__(svc=svc, name="rpa_route", level=ServerLevel.CORE, run_is_async=False)

    def run(self):
        self.port = self.svc.rpa_route_port
        logger.info(f"[RpaRouteServer] 启动 astron_router port={self.port}")

        self.proc = SubPopen(name="rpa_route", cmd=[get_cmd()])
        self.proc.set_param("port", self.port)

        from astronverse.baseline.i18n.i18n import i18n

        self.proc.set_param("language", i18n.getlanguage())

        remote_parsed_url = urlparse(self.svc.config.remote_addr)

        if remote_parsed_url.scheme.lower() == "https":
            self.proc.set_param("httpProtocol", "https")
            self.proc.set_param("wsProtocol", "wss")
        else:
            self.proc.set_param("httpProtocol", "http")
            self.proc.set_param("wsProtocol", "ws")

        self.proc.set_param(
            "remoteHost",
            f"{remote_parsed_url.hostname}:{remote_parsed_url.port}"
            if remote_parsed_url.port
            else f"{remote_parsed_url.hostname}",
        )
        self.proc.run()
        alive = self.proc.is_alive() if self.proc else False
        logger.info(
            f"[RpaRouteServer] 子进程 alive={alive} port={self.port}"
        )

    def health(self) -> bool:
        if not self.proc or not self.proc.is_alive():
            logger.debug("[RpaRouteServer] 健康检查 子进程未存活")
            return False
        return True

    def recover(self):
        logger.debug("[RpaRouteServer] recover kill+run")
        self.proc.kill()
        self.run()
        logger.debug("[RpaRouteServer] recover 结束")


class RpaBrowserConnectorServer(IServer):
    def __init__(self, svc):
        self.proc = None
        self.port = 0
        self.err_time = 0
        self.err_max_time = 3
        super().__init__(
            svc=svc, name="browser_connector", level=ServerLevel.CORE, run_is_async=False
        )

    def run(self):
        self.port = self.svc.connector_port
        logger.info(
            f"[BrowserConnector] 启动 browser_bridge port={self.port} gateway={self.svc.rpa_route_port}"
        )

        self.proc = SubPopen(
            name="browser_bridge",
            cmd=[self.svc.config.python_core, "-m", "astronverse.browser_bridge"],
        )
        self.proc.set_param("port", self.port)
        self.proc.run()
        self.err_time = 0
        alive = self.proc.is_alive() if self.proc else False
        logger.info(
            f"[BrowserConnector] 子进程 alive={alive} port={self.port}"
        )

    def health(self) -> bool:
        if not self.proc or not self.proc.is_alive():
            logger.debug("[BrowserConnector] 健康检查 子进程未存活")
            return False

        url = "http://127.0.0.1:{}/{}/browser/health".format(
            self.svc.rpa_route_port, ComponentType.BROWSER_CONNECTOR.name.lower()
        )
        try:
            response = requests.get(url, timeout=5)
        except Exception as e:
            self.err_time += 1
            logger.debug(
                f"[BrowserConnector] health 请求失败 {self.err_time}/{self.err_max_time} {e}"
            )
            if self.err_time >= self.err_max_time:
                logger.error(
                    "[BrowserConnector] 健康检查判定失败(连续请求异常达阈值)"
                )
                return False
            return True

        status_code = response.status_code
        if status_code != 200:
            self.err_time += 1
            logger.debug(
                f"[BrowserConnector] health HTTP {status_code} 失败 {self.err_time}/{self.err_max_time}"
            )
        else:
            if self.err_time:
                logger.info("[BrowserConnector] health 已恢复 HTTP 200，计数清零")
            self.err_time = 0

        if self.err_time >= self.err_max_time:
            logger.error(
                "[BrowserConnector] 健康检查判定失败(连续非200达阈值)"
            )
            return False

        return True

    def recover(self):
        logger.debug("[BrowserConnector] recover kill+run")
        self.proc.kill()
        self.run()
        logger.debug("[BrowserConnector] recover 结束")
