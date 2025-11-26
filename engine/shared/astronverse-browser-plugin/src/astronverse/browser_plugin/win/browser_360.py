import getpass
import subprocess
import sys
import winreg

from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import Registry, check_chrome_plugin, kill_process


class Browser360PluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data

        self.browser_path = r"Software\360\360se6\Chrome"
        self.preferences_path_list = [
            r"C:\Users\{}\AppData\Local\360Chrome\Chrome\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Local\360Chrome\Chrome\User Data\Profile 1\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Roaming\360se6\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Roaming\360se6\User Data\Default\Profile 1\Preferences".format(getpass.getuser()),
        ]

    @staticmethod
    def get_browser_path():
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\360se6.exe"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "")
            return value
        except FileNotFoundError:
            try:
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\360se6.exe"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
                value, _ = winreg.QueryValueEx(key, "")
                return value
            except FileNotFoundError:
                raise FileNotFoundError("360 is not installed or the registry key is not found.")

    def check_browser(self):
        return Registry.exist(self.browser_path)

    def check_plugin(self):
        installed, installed_version = check_chrome_plugin(self.preferences_path_list, self.plugin_data.plugin_id)

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed,
            installed_version=installed_version,
            latest_version=latest_version,
            latest=latest,
        )

    def close_browser(self):
        kill_process("360se")

    def open_browser(self):
        pass

    def install_plugin(self):
        browser_path = self.get_browser_path()
        subprocess.Popen(
            [browser_path, self.plugin_data.plugin_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0,
        )
