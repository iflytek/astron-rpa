"""
Windows 自启动：当前用户 Run 注册表项。
目录约定与 autostart_darwin 一致：conf 的上两级为安装根目录，其下 astron-rpa.exe。
"""

import os

import winreg as reg

from astronverse.scheduler.error import AUTOSTART_EXE_NOT_FOUND_WIN, BizException

SUPPORTED = True


class Registry:
    """注册表操作"""

    @staticmethod
    def exist(key_path):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
            reg.CloseKey(key)
            return True
        except Exception:
            return False

    @staticmethod
    def create(key_path):
        keys = key_path.split("\\")
        head_key = reg.OpenKey(reg.HKEY_CURRENT_USER, keys[0], 0, reg.KEY_ALL_ACCESS)
        opened_keys = list()
        opened_keys.append(head_key)
        for key in keys[1:]:
            head_key = reg.CreateKey(head_key, key)
            opened_keys.append(head_key)
        opened_keys.reverse()
        for opened_key in opened_keys:
            reg.CloseKey(opened_key)

    @staticmethod
    def delete(key_path, sub_key):
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.DeleteKey(key, sub_key)
        reg.CloseKey(key)

    @staticmethod
    def add_string_value(key_path, value_name, value):
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, value_name, 0, reg.REG_SZ, value)
        reg.CloseKey(key)

    @staticmethod
    def get_registry_value(key_path, value_name):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path)
            value, regtype = reg.QueryValueEx(key, value_name)
            reg.CloseKey(key)
            return value
        except Exception:
            return None


def resolve_windows_binary(conf_file: str) -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(conf_file)))
    exe = os.path.join(base, "astron-rpa.exe")
    if os.path.isfile(exe):
        return os.path.normpath(exe)
    return ""


class AutoStart:
    AUTO_START_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def check(conf_file: str, name="astron-rpa") -> bool:
        expected = resolve_windows_binary(conf_file)
        if not expected:
            return False
        registered = Registry.get_registry_value(AutoStart.AUTO_START_KEY_PATH, name)
        if not registered:
            return False
        reg_norm = os.path.normpath(str(registered).strip().strip('"'))
        return reg_norm.lower() == expected.lower()

    @staticmethod
    def enable(conf_file: str, name="astron-rpa") -> None:
        expected = resolve_windows_binary(conf_file)
        if not expected:
            raise BizException(AUTOSTART_EXE_NOT_FOUND_WIN, AUTOSTART_EXE_NOT_FOUND_WIN.message)
        if AutoStart.check(conf_file, name):
            return
        Registry.create(AutoStart.AUTO_START_KEY_PATH)
        Registry.add_string_value(AutoStart.AUTO_START_KEY_PATH, name, expected)

    @staticmethod
    def disable(conf_file: str, name="astron-rpa") -> None:
        if not AutoStart.check(conf_file, name):
            return
        Registry.add_string_value(AutoStart.AUTO_START_KEY_PATH, name, "")


def check(conf_file: str) -> bool:
    return AutoStart.check(conf_file)


def enable(conf_file: str) -> None:
    AutoStart.enable(conf_file)


def disable(conf_file: str) -> None:
    AutoStart.disable(conf_file)
