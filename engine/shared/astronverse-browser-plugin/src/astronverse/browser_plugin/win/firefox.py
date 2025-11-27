import subprocess
import sys
import winreg

from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import FirefoxUtils, Registry, kill_process


class FirefoxPluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data
        self.browser_path = r"Software\Mozilla\Mozilla Firefox"

    @staticmethod
    def get_browser_path():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Mozilla\\Mozilla Firefox") as key:
                version, _ = winreg.QueryValueEx(key, "CurrentVersion")
                with winreg.OpenKey(key, f"{version}\\Main") as main_key:
                    path, _ = winreg.QueryValueEx(main_key, "PathToExe")
                    return path
        except FileNotFoundError:
            raise FileNotFoundError("Firefox is not installed or the registry key is not found.")

    def check_browser(self):
        return Registry.exist(self.browser_path)

    def check_plugin(self):
        installed, installed_version = FirefoxUtils.check()

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed, installed_version=installed_version, latest_version=latest_version, latest=latest
        )

    def close_browser(self):
        kill_process("firefox")

    def open_browser(self):
        pass

    def install_plugin(self):
        firefox_path = self.get_browser_path()
        subprocess.Popen(
            [firefox_path, self.plugin_data.plugin_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0,
            start_new_session=True,
        )
