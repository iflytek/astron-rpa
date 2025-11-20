import sys
import threading
from astronverse.tools.tools import RpaTools
from astronverse.executor.utils.utils import exec_run


class LogTool:
    def __init__(self, svc):
        self.svc = svc
        self.thread = None

    def __tool__(self):
        if sys.platform == "win32":
            url = RpaTools.get_window_dir()
        else:
            url = RpaTools.get_window_dir()
        exec_run(
            [
                url,
                "--url=tauri://localhost/logwin.html?title={}&ws=ws://127.0.0.1:{}/?tag=tip".format(
                    self.svc.conf.project_name, self.svc.conf.port
                ),
                "--pos=right_bottom",
                "--width=288",
                "--height=102",
                "--top=true",
            ],
            True,
        )

    def start(self):
        self.thread = threading.Thread(target=self.__tool__, daemon=True)
        self.thread.start()
