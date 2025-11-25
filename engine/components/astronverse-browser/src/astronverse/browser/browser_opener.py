"""浏览器打开"""

import platform
import subprocess
import webbrowser

from astronverse.baseline.logger.logger import logger
from astronverse.browser import CommonForBrowserType


class BrowserOpener:
    """浏览器打开工具类"""

    @staticmethod
    def open_browser(
        url: str,
        browser: str = "default",
        new_window: bool = False,
        private: bool = False,
        open_args: str = "",
        browser_path: str = "",
    ):
        system = platform.system().lower()
        logger.info(f"Opening browser: {browser}, URL: {url}, New Window: {new_window}, Private: {private}, Open Args: {open_args} Browser Path: {browser_path}")
        logger.info(f"Detected operating system: {system}")
        try:
            if browser == "default":
                if new_window:
                    webbrowser.open_new(url)
                else:
                    webbrowser.open(url)
                return True

            # Windows: use 'start' command
            if system == "windows":
                cmd = ["start", ""]
                if browser == CommonForBrowserType.BTChrome.value:
                    cmd += ["chrome"]
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == CommonForBrowserType.BTFirefox.value:
                    cmd += ["firefox"]
                    if private:
                        cmd += ["-private-window"]
                    if new_window:
                        cmd += ["-new-window"]
                elif browser == CommonForBrowserType.BTEdge.value:
                    cmd += ["msedge"]
                    if private:
                        cmd += ["--inprivate"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == CommonForBrowserType.BT360SE.value:
                    cmd += ["360se6"]
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == CommonForBrowserType.BT360X.value:
                    cmd += ["360ChromeX"]
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == CommonForBrowserType.BTChromium.value:
                    cmd = ["start", browser_path]
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                else:
                    raise Exception(f"不支持的浏览器类型: {browser}")
                # Add open_args if provided
                if open_args:
                    cmd += open_args.split()
                cmd += [url, "--new-tab"]
                logger.info(f"Executing command: {' '.join(cmd)}")
                subprocess.run(" ".join(cmd), shell=True)
                return True

        except Exception as e:
            raise Exception(f"打开浏览器失败: {e}")


# test
if __name__ == "__main__":
    BrowserOpener.open_browser(
        url="https://www.baidu.com",
        browser="chrome",
        new_window=False,
        private=False,
        open_args="",
    )
