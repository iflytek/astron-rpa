import subprocess

from astronverse.browser_plugin import PluginData, PluginStatus, PluginManagerCore
from astronverse.browser_plugin.utils import FirefoxUtils


class FirefoxPluginManager(PluginManagerCore):
    # 可执行的 firefox 命令
    firefox_command: str = None

    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data
        self.firefox_command = FirefoxUtils.get_firefox_command()

    def check_browser(self):
        return self.firefox_command is not None

    def check_plugin(self):
        installed, installed_version = FirefoxUtils.check(self.firefox_command)

        print(installed, installed_version)

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed, installed_version=installed_version, latest_version=latest_version, latest=latest
        )

    def close_browser(self):
        try:
            # 使用 killall 命令终止所有名为 firefox 的进程
            subprocess.run(["killall", self.firefox_command], check=True)
            print("Firefox has been closed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to close Firefox. It may not be running.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def install_plugin(self):
        command = [self.firefox_command, self.plugin_data.plugin_path, "&"]
        # 启动进程
        process = subprocess.Popen(command)

        print("Firefox 已启动：{0}".format(process.pid))
