from abc import ABC, abstractmethod
from typing import List

from .constants import BrowserType, PluginData, PluginStatus


class PluginManagerCore(ABC):
    @abstractmethod
    def check_browser(self) -> bool:
        """
        check browser exist
        :return:
        """
        pass

    @abstractmethod
    def check_plugin(self) -> PluginStatus:
        """
        check plugin status
        """
        pass

    @abstractmethod
    def install_plugin(self):
        """
        install plugin
        """
        pass

    @abstractmethod
    def close_browser(self):
        """
        close browser
        """
        pass

    @abstractmethod
    def open_browser(self):
        """
        open browser
        """
        pass


class PluginManager(ABC):
    @staticmethod
    @abstractmethod
    def get_support_browser() -> List[BrowserType]:
        """
        get support browsers
        """
        pass

    @staticmethod
    @abstractmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        """
        get plugin manager
        """
        pass
