import configparser
import json
import os
import platform
import re
import subprocess
import winreg as reg

import psutil

from .config import Config


def parse_filename_regex(filename):
    pattern = (
        r"^(?P<browser>[a-zA-Z0-9-]+)-(?P<version>\d+(\.\d+)*)-(?P<hashid>[a-zA-Z0-9]+)\.(?P<extension>[a-zA-Z]+)$"
    )
    match = re.match(pattern, filename)
    if match:
        browser = match.group("browser")
        version = match.group("version")
        hashid = match.group("hashid")
        extension = match.group("extension")
        return browser, version, hashid, extension
    else:
        raise ValueError("Filename does not match expected pattern")


class FirefoxUtils:
    firefox_plugin_id = Config.FIREFOX_PLUGIN_ID

    @staticmethod
    def get_firefox_command():
        try:
            firefox_versions = ["firefox", "firefox-esr"]

            for version in firefox_versions:
                result = subprocess.run(
                    ["which", version],
                    check=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    return version
            return ""

        except Exception:
            return ""

    @staticmethod
    def get_default_profile_path(firefox_command="firefox"):
        if platform.system() == "Windows":
            profile_path = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox")
        elif platform.system() == "Darwin":  # macOS
            profile_path = os.path.expanduser("~/Library/Application Support/Firefox")
        else:  # Linux
            profile_path = os.path.expanduser("~/.mozilla/{0}".format(firefox_command))

        config = configparser.ConfigParser()
        config.read(os.path.join(profile_path, "installs.ini"))
        sections = config.sections()
        if sections:
            default_profile = config[sections[0]]["Default"]
            return os.path.join(profile_path, default_profile)
        else:
            raise FileNotFoundError("Firefox profile not found.")

    @staticmethod
    def check(firefox_command="firefox"):
        try:
            default_profile_path = FirefoxUtils.get_default_profile_path(firefox_command)
            # firefox extensions.json
            extensions_path = os.path.join(default_profile_path, "extensions.json")
            if os.path.exists(extensions_path):
                with open(extensions_path, encoding="utf-8") as f:
                    dict_msg = json.loads(f.read())
                    for addon in dict_msg["addons"]:
                        if addon["id"] == FirefoxUtils.firefox_plugin_id:
                            return True, addon["version"]
                    return False, ""
            else:
                return False, ""
        except FileNotFoundError:
            return False, ""


class Registry:
    @staticmethod
    def exist(key_path, key_type="user") -> bool:
        """
        check key exists
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        try:
            key = reg.OpenKey(head, key_path, 0, reg.KEY_READ)
            reg.CloseKey(key)
            return True
        except Exception:
            return False

    @staticmethod
    def create(key_path, key_type="user"):
        """
        create key
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        keys = key_path.split("\\")
        head_key = reg.OpenKey(head, keys[0], 0, reg.KEY_ALL_ACCESS)
        opened_keys = list()
        opened_keys.append(head_key)
        for key in keys[1:]:
            head_key = reg.CreateKey(head_key, key)
            opened_keys.append(head_key)
        opened_keys.reverse()
        for opened_key in opened_keys:
            reg.CloseKey(opened_key)

    @staticmethod
    def delete(key_path, sub_key, key_type="user"):
        """
        delete key
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_SET_VALUE)
        reg.DeleteKey(key, sub_key)
        reg.CloseKey(key)

    @staticmethod
    def add_string_value(key_path, value_name, value, key_type="user"):
        """
        add string key value
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, value_name, 0, reg.REG_SZ, value)
        reg.CloseKey(key)

    @staticmethod
    def add_dword_value(key_path, value_name, value, key_type="user"):
        """
        add dword key value
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, value_name, 0, reg.REG_DWORD, value)
        reg.CloseKey(key)

    @staticmethod
    def query_value_ex(key, value_name):
        """
        query key value
        """
        try:
            return reg.QueryValueEx(key, value_name)
        except FileNotFoundError:
            return None, None

    @staticmethod
    def query_value(key_path, key_type="user"):
        """
        query all values under key
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        try:
            with reg.OpenKey(head, key_path, 0, reg.KEY_READ) as key:
                values = []
                i = 0
                while True:
                    try:
                        value_name, value_data, value_type = reg.EnumValue(key, i)
                        values.append(value_data)
                        i += 1
                    except OSError:
                        break
                return values
        except FileNotFoundError:
            return []

    @staticmethod
    def open_key(key_path, key_type="user"):
        """
        open key
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        try:
            return reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            raise FileNotFoundError(f"registry {key_path} not found")


def kill_process(name: str):
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if "{}.exe".format(name) == proc.info["name"].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def start_browser(browser_path: str):
    try:
        os.startfile(browser_path)
    except Exception:
        pass


def get_app_path(name: str):
    try:
        app_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{}.exe".format(name)
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, app_path)
        path, _ = reg.QueryValueEx(key, "")
        return path
    except FileNotFoundError:
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, app_path)
            path, _ = reg.QueryValueEx(key, "")
            return path
        except FileNotFoundError:
            return None


def check_chrome_plugin(preferences_path_list, extension_id):
    """
    check chrome based browser plugin installed
    """
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, encoding="utf-8") as f:
                content = f.read()
                dict_msg = json.loads(content)
                try:
                    extension_info = dict_msg["extensions"]["settings"]
                    if extension_id in extension_info:
                        version = extension_info[extension_id].get("manifest", {}).get("version", "")
                        return True, version
                    else:
                        return False, ""
                except KeyError:
                    return False, ""

    return False, ""


def remove_browser_setting(preferences_path_list, secure_preferences, extension_id):
    """
    delete browser plugin setting
    """
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, encoding="utf-8") as f:
                content = f.read()
                dict_msg = json.loads(content)
                uninstall_list = (
                    dict_msg.get("extensions").get("external_uninstalls", []) if dict_msg.get("extensions") else []
                )
                is_update = False
                if extension_id in uninstall_list:
                    uninstall_list.remove(extension_id)
                    is_update = True

                invalid_ids = (
                    dict_msg.get("install_signature").get("invalid_ids", [])
                    if dict_msg.get("install_signature")
                    else []
                )
                if extension_id in invalid_ids:
                    invalid_ids.remove(extension_id)
                    is_update = True

                apps = dict_msg.get("updateclientdata").get("apps", {}) if dict_msg.get("updateclientdata") else {}
                if extension_id in apps:
                    del apps[extension_id]
                    is_update = True

                extension_info = dict_msg.get("extensions", {}).get("settings", {}).get(extension_id, None)
                if extension_info is not None:
                    del dict_msg["extensions"]["settings"][extension_id]
                    is_update = True

                if is_update:
                    with open(file, "w", encoding="utf-8") as f:
                        json.dump(dict_msg, f)
            break

    # delete secure preferences
    if os.path.exists(secure_preferences):
        os.remove(secure_preferences)
