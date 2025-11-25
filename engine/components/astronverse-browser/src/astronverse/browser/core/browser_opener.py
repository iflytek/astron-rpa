"""浏览器打开"""

import platform
import subprocess
import webbrowser

from astronverse.baseline.logger.logger import logger


class BrowserOpener:
    """浏览器打开工具类"""

    @staticmethod
    def open_browser(
        url: str, browser: str = "default", new_window: bool = False, private: bool = False, open_args: str = ""
    ) -> bool:
        system = platform.system().lower()
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
                if browser == "chrome":
                    cmd += ["chrome"]
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == "firefox":
                    cmd += ["firefox"]
                    if private:
                        cmd += ["-private-window"]
                    if new_window:
                        cmd += ["-new-window"]
                elif browser == "edge":
                    cmd += ["msedge"]
                    if private:
                        cmd += ["--inprivate"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == "360se":
                    cmd += ["360se6"]
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                elif browser == "360ChromeX":
                    if private:
                        cmd += ["--incognito"]
                    if new_window:
                        cmd += ["--new-window"]
                # Add open_args if provided
                if open_args:
                    cmd += open_args.split()
                cmd += [url, "--new-tab"]
                logger.info(f"Executing command: {' '.join(cmd)}")
                subprocess.run(" ".join(cmd), shell=True)
                return True

            # macOS
            elif system == "darwin":
                if browser == "chrome":
                    cmd = ["open", "-a", "Google Chrome"]
                    args = []
                    if private:
                        args += ["--incognito"]
                    if open_args:
                        args += open_args.split()
                    if args:
                        cmd += ["--args"] + args
                    cmd += [url]
                elif browser == "firefox":
                    cmd = ["open", "-a", "Firefox"]
                    args = []
                    if private:
                        args += ["-private-window"]
                    if open_args:
                        args += open_args.split()
                    if args:
                        cmd += ["--args"] + args
                    cmd += [url]
                elif browser == "edge":
                    cmd = ["open", "-a", "Microsoft Edge"]
                    args = []
                    if private:
                        args += ["--inprivate"]
                    if open_args:
                        args += open_args.split()
                    if args:
                        cmd += ["--args"] + args
                    cmd += [url]
                elif browser == "safari":
                    cmd = ["open", "-a", "Safari", url]
                else:
                    webbrowser.open(url)
                    return True
                subprocess.run(cmd)
                return True

            # Linux
            else:
                browser_cmd = {"chrome": "google-chrome", "firefox": "firefox", "edge": "microsoft-edge"}
                exe = browser_cmd.get(browser)
                if not exe:
                    webbrowser.open(url)
                    return True
                cmd = [exe]
                if browser == "chrome" and private:
                    cmd += ["--incognito"]
                if browser == "firefox" and private:
                    cmd += ["-private-window"]
                if browser == "edge" and private:
                    cmd += ["--inprivate"]
                if browser == "opera" and private:
                    cmd += ["--private"]
                if open_args:
                    cmd += open_args.split()
                cmd += [url]
                subprocess.Popen(cmd)
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