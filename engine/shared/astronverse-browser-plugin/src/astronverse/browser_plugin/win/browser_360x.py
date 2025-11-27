import getpass
import os
import subprocess
import sys
import winreg

from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import Registry, check_chrome_plugin, kill_process


class Browser360XPluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data

        self.browser_path = r"Software\360ChromeX\Chrome"
        self.extension_path = r"Software\360ChromeX\Chrome\Extensions"
        self.preferences_path_list = [
            r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\User Data\Profile 1\Preferences".format(getpass.getuser()),
        ]
        self.secure_preferences = (
            r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\User Data\Default\Secure Preferences".format(
                getpass.getuser()
            )
        )

    @staticmethod
    def get_browser_path():
        default_path = r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\Application\360ChromeX.exe".format(
            getpass.getuser()
        )
        if os.path.exists(default_path):
            return default_path

        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths\360chromeX.exe"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "")
            return value
        except FileNotFoundError:
            raise FileNotFoundError("360X is not installed or the registry key is not found.")

    def check_browser(self):
        return Registry.exist(self.browser_path)

    def check_plugin(self):
        installed, installed_version = check_chrome_plugin(self.preferences_path_list, self.plugin_data.plugin_id)

        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version

        return PluginStatus(
            installed=installed, installed_version=installed_version, latest_version=latest_version, latest=latest
        )

    def close_browser(self):
        kill_process("360chromex")

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
