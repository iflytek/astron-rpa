import subprocess
import sys
from astronverse.baseline.logger.logger import logger
from astronverse.browser import BROWSER_REGISTER_NAME
from astronverse.browser.error import *


class BrowserLauncher:
    """浏览器启动工具类，类似 webbrowser 的功能，但不依赖 webbrowser 模块"""

    @staticmethod
    def open(path: str, url: str = "", open_args: str = "") -> bool:
        """打开浏览器"""

        cmd_parts = [f'"{path}"']
        if open_args:
            cmd_parts.append(open_args)
        if url:
            cmd_parts.append(f'"{url}"')
        cmdline = " ".join(cmd_parts)

        logger.info(f"启动浏览器命令: {cmdline}")

        try:
            if sys.platform[:3] == "win":
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True, start_new_session=True)
            return p.poll() is None
        except Exception as e:
            raise BaseException(BROWSER_OPEN_ERROR, "浏览器打开失败{}".format(e))
