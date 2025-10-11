from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class BrowserType(Enum):
    CHROME = "CHROME"
    MICROSOFT_EDGE = "MICROSOFT_EDGE"
    FIREFOX = "FIREFOX"
    BROWSER_360 = "360"
    BROWSER_360X = "360X"

    @classmethod
    def init(cls, name: str):
        name = name.upper()
        return cls(name)


class OP(Enum):
    INSTALL = "INSTALL"
    UNINSTALL = "UNINSTALL"
    UPGRADE = "UPGRADE"
    CHECK = "CHECK"

    @classmethod
    def init(cls, name: str):
        name = name.upper()
        return cls(name)


@dataclass
class PluginStatus:
    installed: bool = False
    latest: bool = False
    installed_version: str = ""
    latest_version: str = ""


@dataclass
class PluginData:
    plugin_path: str = ""
    plugin_name: str = ""
    plugin_id: str = ""
    plugin_version: str = ""


class PluginManagerCore(ABC):
    @abstractmethod
    def check_browser(self) -> bool:
        pass

    @abstractmethod
    def check_plugin(self) -> PluginStatus:
        pass

    @abstractmethod
    def install_plugin(self):
        pass

    @abstractmethod
    def close_browser(self):
        pass


class PluginManager(ABC):
    @staticmethod
    @abstractmethod
    def get_support_browser() -> list[BrowserType]:
        pass

    @staticmethod
    @abstractmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        pass
