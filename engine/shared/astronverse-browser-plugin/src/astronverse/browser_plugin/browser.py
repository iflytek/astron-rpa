import os
import sys

from astronverse.browser_plugin import BrowserType, PluginData
from astronverse.browser_plugin.utils import parse_filename_regex

if sys.platform == "win32":
    from astronverse.browser_plugin.win import BrowserPluginFactory
elif sys.platform == "linux":
    from astronverse.browser_plugin.unix import BrowserPluginFactory
else:
    raise Exception(f"Unsupported platform: {sys.platform}")


class ExtensionManager:
    def __init__(self, browser_type: BrowserType = BrowserType.CHROME):
        self.browser_type = browser_type

        current_directory = os.path.dirname(os.path.abspath(__file__))
        plugin_dir = os.path.join(current_directory, "plugins")
        browser_name = self.browser_type.value.lower()

        public_chrom_plugin = tuple(name.value.lower() for name in (BrowserType.CHROME, BrowserType.MICROSOFT_EDGE))
        pre_name = "chrome" if browser_name in public_chrom_plugin else browser_name
        plugins = [file for file in os.listdir(plugin_dir) if file.startswith(pre_name + "-")]

        if not plugins:
            raise Exception("plugins not found...")

        # get plugin info from file
        plugin_name, plugin_version, plugin_id, _extension = parse_filename_regex(plugins[-1])

        self.plugin_data = PluginData(
            plugin_path=os.path.join(os.getcwd(), plugin_dir, plugins[-1]),
            plugin_id=plugin_id,
            plugin_version=plugin_version,
            plugin_name=plugin_name,
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
    def __init__(self) -> None:
        self.support_browsers = BrowserPluginFactory.get_support_browser()
        self.insalled_plugins = []
        self.installed_update_plugins = []
        for browser_type in self.support_browsers:
            extension_manager = ExtensionManager(browser_type)
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
                extension_manager = ExtensionManager(browser_type)
                extension_manager.install()
                install_results.append({"browser": browser_type.value, "status": 1})
            except Exception as e:
                install_results.append({"browser": browser_type.value, "status": 0, "error": str(e)})
        return install_results
