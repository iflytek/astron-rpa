import subprocess

from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import FirefoxUtils


class FirefoxPluginManager(PluginManagerCore):
    firefox_command: str = ""

    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data
        self.firefox_command = FirefoxUtils.get_firefox_command()

    def check_browser(self):
        return self.firefox_command is not None

    def check_plugin(self):
        installed, installed_version = FirefoxUtils.check(self.firefox_command)

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed, installed_version=installed_version, latest_version=latest_version, latest=latest
        )

    def close_browser(self):
        try:
            subprocess.run(
                ["killall", self.firefox_command],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            pass

    def open_browser(self):
        pass

    def install_plugin(self):
        subprocess.Popen(
            [self.firefox_command, self.plugin_data.plugin_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
