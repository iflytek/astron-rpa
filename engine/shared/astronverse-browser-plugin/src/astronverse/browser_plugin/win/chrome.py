import getpass
import winreg

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import (
    Registry,
    check_chrome_plugin,
    get_app_path,
    get_profile_list,
    is_browser_running,
    kill_process,
    remove_browser_setting,
    remove_old_extensions,
    start_browser,
)
from astronverse.browser_plugin.win.reg import run_reg_file

from ..config import Config


class ChromePluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data
        self.old_extension_ids = Config.OLD_EXTENSIONS_IDS
        self.browser_path = r"Software\Google\Chrome"
        self.extension_path = f"{self.browser_path}\\Extensions\\{plugin_data.plugin_id}"
        self.user_data_path = r"C:\Users\{}\AppData\Local\Google\Chrome\User Data".format(getpass.getuser())
        self.preferences_path_list = get_profile_list(self.user_data_path)
        self.secure_preferences = (
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default\Secure Preferences".format(getpass.getuser())
        )
        logger.info(f"Chrome preferences_path_list: {self.preferences_path_list}")

    @staticmethod
    def get_browser_path():
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "")
            return value
        except FileNotFoundError:
            try:
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
                value, _ = winreg.QueryValueEx(key, "")
                return value
            except FileNotFoundError:
                raise FileNotFoundError("Chrome is not installed or the registry key is not found.")

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
        installed, installed_version = check_chrome_plugin(
            preferences_path_list=self.preferences_path_list,
            extension_id=self.plugin_data.plugin_id,
        )
        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version
        browser_installed = self.check_browser()
        logger.info(f"Chrome plugin installed: {installed}, installed_version: {installed_version}")
        return PluginStatus(
            installed=installed,
            installed_version=installed_version,
            latest_version=latest_version,
            latest=latest,
            browser_installed=browser_installed,
        )

    def close_browser(self):
        kill_process("chrome")

    def open_browser(self):
        app_path = get_app_path("chrome")
        if app_path:
            start_browser(app_path)

    def install_plugin(self):
        self.close_browser()
        remove_browser_setting(
            preferences_path_list=self.preferences_path_list,
            secure_preferences=self.secure_preferences,
            extension_id=self.plugin_data.plugin_id,
            old_extension_ids=self.old_extension_ids,
        )
        remove_old_extensions(
            extension_path=f"{self.browser_path}\\Extensions",
            old_extension_ids=self.old_extension_ids,
        )

        Registry.create(self.extension_path)
        Registry.add_string_value(self.extension_path, "path", self.plugin_data.plugin_path)
        Registry.add_string_value(self.extension_path, "version", self.plugin_data.plugin_version)

        # https://chromeenterprise.google/policies/?policy=ExtensionInstallAllowlist
        try:
            if not Registry.exist(r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist"):
                Registry.create(r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist")

            Registry.add_string_value(
                r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", "1", self.plugin_data.plugin_id
            )
            Registry.add_string_value(
                r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist",
                "1",
                self.plugin_data.plugin_id,
                key_type="machine",
            )

            logger.info("set chrome plugin allowlist success")
        except Exception as e:
            logger.error(f"set chrome plugin allowlist failed: {e}")
            self.register_policy()
            pass

        try:
            self.open_browser()
        except Exception as e:
            logger.error(f"open chrome browser failed: {e}")
            pass

    def register_policy(self):
        return run_reg_file(self.plugin_data.plugin_id)

    def check_browser_running(self):
        """
        check browser running
        """
        return is_browser_running("chrome")
