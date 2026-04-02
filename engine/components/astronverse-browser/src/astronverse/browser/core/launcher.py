import shlex
import subprocess
import sys
from astronverse.baseline.logger.logger import logger
from astronverse.browser.error import *


class BrowserLauncher:
    """浏览器启动工具类，类似 webbrowser 的功能，但不依赖 webbrowser 模块"""

    @staticmethod
    def open(path: str, url: str = "", open_args: str = "") -> bool:
        """打开浏览器"""
        open_arg_list = shlex.split(open_args) if open_args else []
        if sys.platform == "darwin" and path.lower().endswith(".app"):
            cmd_parts = ["open", "-a", path]
            browser_args = [*open_arg_list, *( [url] if url else [] )]
            if browser_args:
                cmd_parts.extend(["--args", *browser_args])
        else:
            cmd_parts = [path, *open_arg_list]
            if url:
                cmd_parts.append(url)

        logger.info(f"启动浏览器命令: {cmd_parts}")

        try:
            if sys.platform[:3] == "win":
                p = subprocess.Popen(cmd_parts)
            else:
                p = subprocess.Popen(cmd_parts, close_fds=True, start_new_session=True)
            return p.poll() is None
        except Exception as e:
            raise BizException(BROWSER_OPEN_ERROR, "浏览器打开失败{}".format(e))
