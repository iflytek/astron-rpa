"""浏览器核心接口模块，定义浏览器操作的抽象接口。"""

from abc import ABC, abstractmethod
from typing import Any

from rpabrowser import CommonForBrowserType as BrowserType


class IBrowserCore(ABC):
    """浏览器核心操作抽象接口。"""

    @staticmethod
    @abstractmethod
    def get_browser_path(browser_type: BrowserType) -> str:
        """获取浏览器绝对地址。"""

    @staticmethod
    @abstractmethod
    def get_browser_handler(browser_type: BrowserType) -> Any:
        """获取浏览器的控制器。"""

    @staticmethod
    @abstractmethod
    def get_browser_point(browser_type: BrowserType) -> Any:
        """获取浏览器坐标。"""

    @staticmethod
    @abstractmethod
    def download_window_operate(*args, **kwargs) -> Any:
        """获取浏览器下载文件另存为窗口。"""

    @staticmethod
    @abstractmethod
    def upload_window_operate(*args, **kwargs) -> Any:
        """获取浏览器上传文件窗口。"""
