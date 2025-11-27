import getpass

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.utils import (
    Registry,
    check_chrome_plugin,
    get_app_path,
    kill_process,
    remove_browser_setting,
    start_browser,
)
from astronverse.browser_plugin.win.reg import run_reg_file


class ChromePluginManager(PluginManagerCore):
    def __init__(self, plugin_data: PluginData):
        self.plugin_data = plugin_data

        self.browser_path = r"Software\Google\Chrome"
        self.extension_path = f"{self.browser_path}\\Extensions\\{plugin_data.plugin_id}"
        self.preferences_path_list = [
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default\Preferences".format(getpass.getuser()),
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Profile 1\Preferences".format(getpass.getuser()),
        ]
        self.secure_preferences = (
            r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default\Secure Preferences".format(getpass.getuser())
        )

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
