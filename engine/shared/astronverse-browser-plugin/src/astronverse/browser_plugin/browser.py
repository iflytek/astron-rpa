import os
import platform
import shutil
import sys

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin import BrowserType, PluginData
from astronverse.browser_plugin.error import UNSUPPORTED_PLATFORM_FORMAT, BizException
from astronverse.browser_plugin.utils import get_latest_plugin, parse_filename_regex

if sys.platform == "win32":
    from astronverse.browser_plugin.win.common import BrowserPluginFactory
elif sys.platform in ("linux", "darwin"):
    from astronverse.browser_plugin.unix.common import BrowserPluginFactory
else:
    raise BizException(UNSUPPORTED_PLATFORM_FORMAT.format(sys.platform), f"不支持的平台: {sys.platform}")

from .config import Config


class ExtensionManager:
    def __init__(self, resource_dir: str, browser_type: BrowserType = BrowserType.CHROME):
        self.browser_type = browser_type

        app_data_path = os.path.abspath(os.path.join(sys.exec_prefix, ".."))
        native_message_path = os.path.join(app_data_path, "external", "native_message")
        os.makedirs(native_message_path, exist_ok=True)

        plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
        plugins = [file for file in os.listdir(plugin_dir) if file.endswith(".xpi") or file.endswith(".crx")]
        logger.info(f"Found plugins: {plugins}")

        latest_plugin = get_latest_plugin(plugins, "firefox" if browser_type == BrowserType.FIREFOX else "chrome")
        plugin_name, plugin_version, plugin_id, _extension = parse_filename_regex(latest_plugin)

        # Get platform-specific resources directory
        if sys.platform == "win32":
            platform_dir = "win-x64"
            exe_ext = ".exe"
        elif sys.platform == "darwin":
            platform_dir = "mac"
            exe_ext = ""
        else:
            platform_dir = "linux-arm64" if platform.machine().lower() in ("aarch64", "arm64") else "linux-amd64"
            exe_ext = ""

        resources_dir = os.path.join(resource_dir, platform_dir)
        source_json_path = os.path.join(resources_dir, Config.NATIVE_MESSAGE_HOST_FILE_NAME + ".json")
        source_exe_path = os.path.join(resources_dir, Config.NATIVE_MESSAGE_HOST_FILE_NAME + exe_ext)

        # copy native message host to external data path
        target_exe_path = os.path.join(native_message_path, Config.NATIVE_MESSAGE_HOST_FILE_NAME + exe_ext)
        target_json_path = os.path.join(native_message_path, Config.NATIVE_MESSAGE_HOST_FILE_NAME + ".json")
        if not os.path.exists(target_json_path):
            shutil.copy(source_exe_path, target_exe_path)
            shutil.copy(source_json_path, target_json_path)

        self.plugin_data = PluginData(
            plugin_path=os.path.join(os.getcwd(), plugin_dir, latest_plugin),
            plugin_id=plugin_id,
            plugin_version=plugin_version,
            plugin_name=plugin_name,
            plugin_native_message_host_json_path=target_json_path,
        )

        self.browser_plugin_manager = BrowserPluginFactory.get_plugin_manager(browser_type, self.plugin_data)

    @staticmethod
    def get_support():
        """
        get support browsers
        """
        return BrowserPluginFactory.get_support_browser()

    def close_browser(self):
        """
        close browser
        """
        self.browser_plugin_manager.close_browser()

    def check_status(self):
        """
        check plugin status
        """
        return self.browser_plugin_manager.check_plugin()

    def install(self):
        """
        install plugin
        """
        return self.browser_plugin_manager.install_plugin()

    def uninstall(self):
        """
        uninstall plugin
        """
        raise NotImplementedError("uninstall method is not implemented yet.")

    def upgrade(self):
        """
        upgrade plugin
        """
        return self.install()

    def check_browser(self):
        """
        check browser installed
        """
        return self.browser_plugin_manager.check_browser()

    def open_browser(self):
        """
        open browser
        """
        self.browser_plugin_manager.open_browser()

    def check_browser_running(self):
        """
        check browser running
        """
        return self.browser_plugin_manager.check_browser_running()


class UpdateManager:
    def __init__(self, resource_dir: str) -> None:
        self.resource_dir = resource_dir
        self.support_browsers = BrowserPluginFactory.get_support_browser()
        self.insalled_plugins = []
        self.installed_update_plugins = []
        for browser_type in self.support_browsers:
            extension_manager = ExtensionManager(resource_dir, browser_type)
            plugin_status = extension_manager.check_status()
            if plugin_status.installed:
                self.insalled_plugins.append(browser_type)
                if not plugin_status.latest:
                    self.installed_update_plugins.append(browser_type)

    def update_installed_plugins(self):
        """
        update installed plugins
        """
        install_results = []
        for browser_type in self.installed_update_plugins:
            try:
                extension_manager = ExtensionManager(self.resource_dir, browser_type)
                extension_manager.install()
                install_results.append({"browser": browser_type.value, "status": 1})
            except Exception as e:
                install_results.append({"browser": browser_type.value, "status": 0, "error": str(e)})
        return install_results
