import win32con
from astronverse.software.core import ISoftwareCore
from astronverse.software.registry_windows import WindowsRegistryManager


class SoftwareCore(ISoftwareCore):
    @staticmethod
    def get_app_path(app_name: str = "") -> str:
        return SoftwareCore.get_app_path_by_registry(app_name)

    @staticmethod
    def get_app_path_by_registry(app_name: str = "") -> str:
        """通过注册表查找软件地址"""

        try:
            registry_manager = WindowsRegistryManager(
                r"Software\Microsoft\Windows\CurrentVersion\App Paths",
                win32con.HKEY_LOCAL_MACHINE,
                "r",
            )
            path = getattr(registry_manager, app_name)[None]
        except OSError:
            try:
                registry_manager = WindowsRegistryManager(
                    r"Software\Microsoft\Windows\CurrentVersion\App Paths",
                    win32con.HKEY_CURRENT_USER,
                    "r",
                )
                path = getattr(registry_manager, app_name)[None]
            except OSError:
                return ""
        return path
