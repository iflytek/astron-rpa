from abc import abstractmethod, ABC
from enum import Enum
from dataclasses import dataclass
from typing import List


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
    """
    插件的安装状态
    """

    installed: bool = False  # 插件是否安装
    latest: bool = False  # 插件是否是最新版本
    installed_version: str = None  # 插件安装的版本
    latest_version: str = None  # 插件最新版本


@dataclass
class PluginData:
    """
    插件的相关数据
    """

    plugin_path: str = None  # 插件的路径
    plugin_name: str = None  # 插件的名称
    plugin_id: str = None  # 插件的id
    plugin_version: str = None  # 插件的版本


class PluginManagerCore(ABC):
    @abstractmethod
    def check_browser(self) -> bool:
        """
        检查浏览器是否安装
        :return:
        """
        pass

    @abstractmethod
    def check_plugin(self) -> PluginStatus:
        """
        检查插件的安装状态
        """
        pass

    @abstractmethod
    def install_plugin(self):
        """
        安装插件
        """
        pass

    @abstractmethod
    def close_browser(self):
        """
        关闭浏览器
        """
        pass


class PluginManager(ABC):
    @staticmethod
    @abstractmethod
    def get_support_browser() -> List[BrowserType]:
        """
        获取支持的浏览器类型
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        """
        获取插件管理器
        :param plugin_data: 插件信息
        :param browser_type: 浏览器类型
        :return:
        """
        pass
