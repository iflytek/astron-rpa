import json
import os
import subprocess

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin import PluginData, PluginManagerCore, PluginStatus
from astronverse.browser_plugin.config import Config
from astronverse.browser_plugin.unix import common


# Extension install via external_crx JSON:
# https://developer.chrome.com/docs/extensions/how-to/distribute/install-extensions#preference-linux
# https://learn.microsoft.com/zh-cn/microsoft-edge/extensions-chromium/developer-guide/alternate-distribution-options#using-a-preferences-json-file-macos-and-linux


class ChromiumPluginManager(PluginManagerCore):

    def __init__(self, plugin_data: PluginData) -> None:
        self.plugin_data = plugin_data
        self.old_extension_ids = Config.OLD_EXTENSIONS_IDS

        if common.is_macos():
            self.browser_cmd = ["open", "-a", "Google Chrome"]
            self.process_name = "Google Chrome"
            self.extension_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/External Extensions")
            self.native_messaging_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/NativeMessagingHosts")
            self.policy_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/policies/managed")
            self.user_data_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
            self.secure_preferences = os.path.join(self.user_data_path, "Default", "Secure Preferences")
        else:
            self.browser_cmd = ["google-chrome"]
            self.process_name = "chrome"
            self.extension_dir = "/opt/google/chrome/extensions"
            self.native_messaging_dir = "/etc/opt/chrome/native-messaging-hosts"
            self.policy_dir = "/etc/opt/chrome/policies/managed"
            self.user_data_path = os.path.expanduser("~/.config/google-chrome")
            self.secure_preferences = os.path.join(self.user_data_path, "Default", "Secure Preferences")

        self.preferences_path_list = common.get_profile_list(self.user_data_path)
        logger.info(f"Chrome preferences_path_list: {self.preferences_path_list}")

    # ------------------------------------------------------------------
    # PluginManagerCore interface
    # ------------------------------------------------------------------

    def check_browser(self) -> bool:
        if common.is_macos():
            return os.path.exists("/Applications/Google Chrome.app")
        try:
            result = subprocess.run(
                ["which", "google-chrome"],
                check=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_plugin(self) -> PluginStatus:
        browser_installed = self.check_browser()
        installed, installed_version = common.check_chrome_plugin(
            preferences_path_list=self.preferences_path_list,
            extension_id=self.plugin_data.plugin_id,
        )
        latest_version = self.plugin_data.plugin_version
        latest = installed_version == latest_version
        logger.info(f"Chrome plugin installed: {installed}, installed_version: {installed_version}")
        return PluginStatus(
            installed=installed,
            installed_version=installed_version,
            latest_version=latest_version,
            latest=latest,
            browser_installed=browser_installed,
        )

    def close_browser(self):
        common.kill_process(self.process_name)

    def open_browser(self):
        common.start_browser(self.browser_cmd)

    def check_browser_running(self) -> bool:
        return common.is_browser_running(self.process_name)

    def install_plugin(self):
        self.close_browser()
        import time
        time.sleep(2)
        common.remove_browser_setting(
            preferences_path_list=self.preferences_path_list,
            secure_preferences=self.secure_preferences,
            extension_id=self.plugin_data.plugin_id,
            old_extension_ids=self.old_extension_ids,
        )
        common.remove_old_extensions(
            extension_dir=self.extension_dir,
            old_extension_ids=self.old_extension_ids,
        )
        self._install_extension()
        self._install_native_messaging()
        self._install_policy()
        try:
            common.start_browser(self.browser_cmd)
        except Exception as e:
            logger.error(f"open chrome after install failed: {e}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _install_extension(self):
        common.ensure_dir(self.extension_dir)
        plugin_json = {
            "external_crx": self.plugin_data.plugin_path,
            "external_version": self.plugin_data.plugin_version,
        }
        dest = os.path.join(self.extension_dir, f"{self.plugin_data.plugin_id}.json")
        common.write_json(dest, plugin_json)
        logger.info(f"chrome extension json written: {dest}")

    def _install_native_messaging(self):
        """Place a native messaging host JSON with the correct binary path."""
        src_json = self.plugin_data.plugin_native_message_host_json_path
        src_dir = os.path.dirname(src_json)
        exe_path = os.path.join(src_dir, Config.NATIVE_MESSAGE_HOST_FILE_NAME)

        with open(src_json, encoding="utf-8") as f:
            host_json = json.load(f)
        host_json["path"] = exe_path

        common.ensure_dir(self.native_messaging_dir)
        dest = os.path.join(self.native_messaging_dir, Config.NATIVE_MESSAGE_HOST_NAME + ".json")
        common.write_json(dest, host_json)
        logger.info(f"native messaging host json written: {dest}")

    def _install_policy(self):
        """Write Chrome managed policy to force install the extension."""
        force_install_entry = f"{self.plugin_data.plugin_id};https://clients2.google.com/service/update2/crx"
        policy = {
            "ExtensionInstallAllowlist": [self.plugin_data.plugin_id],
            "ExtensionInstallForcelist": [force_install_entry],
        }
        common.ensure_dir(self.policy_dir)
        dest = os.path.join(self.policy_dir, "astronrpa_policy.json")
        common.write_json(dest, policy)
        logger.info(f"chrome policy written: {dest}")
