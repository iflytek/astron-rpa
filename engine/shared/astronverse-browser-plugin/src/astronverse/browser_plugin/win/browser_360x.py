import getpass
import os
import subprocess
import sys
import winreg

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import (
    Registry,
    check_chrome_plugin,
    get_profile_list,
    is_browser_running,
    kill_process,
)


class Browser360XPluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data

        self.browser_path = r"Software\360ChromeX\Chrome"
        self.extension_path = r"Software\360ChromeX\Chrome\Extensions"
        self.user_data_path = r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\User Data".format(getpass.getuser())
        self.preferences_path_list = get_profile_list(self.user_data_path)
        self.secure_preferences = (
            r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\User Data\Default\Secure Preferences".format(
                getpass.getuser()
            )
        )
        logger.info(f"360X preferences_path_list: {self.preferences_path_list}")

    @staticmethod
    def get_browser_path():
        default_path = r"C:\Users\{}\AppData\Local\360ChromeX\Chrome\Application\360ChromeX.exe".format(
            getpass.getuser()
        )
        if os.path.exists(default_path):
            return default_path

        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths\360ChromeX.exe"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "")
            return value
        except FileNotFoundError:
            raise FileNotFoundError("360X is not installed or the registry key is not found.")

    def check_browser(self):
        browser_registry = Registry.exist(self.browser_path)
        if browser_registry:
            try:
                self.get_browser_path()
                return True
            except FileNotFoundError:
                return False
        return browser_registry

    def check_plugin(self):
        installed, installed_version = check_chrome_plugin(self.preferences_path_list, self.plugin_data.plugin_id)
        logger.info(f"360X plugin installed: {installed}, installed_version: {installed_version}")
        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version
        browser_installed = self.check_browser()
        return PluginStatus(
            installed=installed,
            installed_version=installed_version,
            latest_version=latest_version,
            latest=latest,
            browser_installed=browser_installed,
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

    def check_browser_running(self):
        """
        check browser running
        """
        return is_browser_running("360ChromeX")
