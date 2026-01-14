import json
import requests
from astronverse.executor.logger import logger


class LogTool:
    def __init__(self, svc):
        self.svc = svc
        self.starting = False

    def _send_msg(self, action: str):
        info = self.svc.get_project_info()
        sub_window = {
            "action": action,
            "name": "logwin",
            "params": {
                "title": info.project_name,
                "icon": info.project_icon,
                "ws": "ws://127.0.0.1:{}/?tag=tip".format(self.svc.conf.port),
            },
            "pos": "right_bottom",
            "width": "360",
            "height": "128",
            "top": "true",
        }
        url = "http://127.0.0.1:{}/scheduler/send/sub_window".format(self.svc.conf.gateway_port)
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(sub_window))
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
