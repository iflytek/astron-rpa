import json
import requests
from astronverse.executor.logger import logger


class LogTool:
    def __init__(self, svc):
        self.svc = svc
        self.starting = False

    def _send_msg(self, action: str):
        icon = self.svc.start_project_icon
        if icon:
            from urllib.parse import quote

            icon = quote(icon)
        sub_window = {
            "action": action,
            "name": "logwin",
            "params": {
                "title": self.svc.start_project_name,
                "icon": icon,
                "ws": "ws://127.0.0.1:{}/?tag=tip".format(self.svc.port),
            },
            "pos": "right_bottom",
            "width": "360",
            "height": "128",
            "top": "true",
        }
        url = "http://127.0.0.1:{}/scheduler/send/sub_window".format(self.svc.gateway_port)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(sub_window))
        logger.info(f"当前调度器返回的结果的Json是：{response.json()}")
        if int(response.status_code) == 200 and response.json()["code"] == "0000":
            return response.json()
        else:
            return None

    def close(self):
        if self.starting:
            self._send_msg(action="close")
            self.starting = False

    def start(self):
        self.starting = True
        self._send_msg(action="open")
