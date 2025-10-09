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
    """
    plugin status
    """

    installed: bool = False
    latest: bool = False
    installed_version: str = ""
    latest_version: str = ""


@dataclass
class PluginData:
    """
    plugin data
    """

    plugin_path: str = ""
    plugin_name: str = ""
    plugin_id: str = ""
    plugin_version: str = ""
