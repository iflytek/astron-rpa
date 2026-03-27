import json
import os
import shutil
import winreg as reg
import psutil
from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin.error import BizException, REGISTRY_NOT_FOUND_FORMAT
from astronverse.browser_plugin import BrowserType, PluginData, PluginManager, PluginManagerCore
from astronverse.browser_plugin.error import BizException, UNSUPPORTED_BROWSER_FORMAT
from astronverse.browser_plugin.win.browser_360 import Browser360PluginManager
from astronverse.browser_plugin.win.browser_360x import Browser360XPluginManager
from astronverse.browser_plugin.win.chrome import ChromePluginManager
from astronverse.browser_plugin.win.firefox import FirefoxPluginManager
from astronverse.browser_plugin.win.microsoft_edge import EdgePluginManager


class BrowserPluginFactory(PluginManager):
    @staticmethod
    def get_support_browser():
        return [
            BrowserType.CHROME,
            BrowserType.MICROSOFT_EDGE,
            BrowserType.FIREFOX,
            BrowserType.BROWSER_360,
            BrowserType.BROWSER_360X,
        ]

    @staticmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        if browser_type == BrowserType.CHROME:
            return ChromePluginManager(plugin_data)
        elif browser_type == BrowserType.MICROSOFT_EDGE:
            return EdgePluginManager(plugin_data)
        elif browser_type == BrowserType.FIREFOX:
            return FirefoxPluginManager(plugin_data)
        elif browser_type == BrowserType.BROWSER_360:
            return Browser360PluginManager(plugin_data)
        elif browser_type == BrowserType.BROWSER_360X:
            return Browser360XPluginManager(plugin_data)
        else:
            raise BizException(UNSUPPORTED_BROWSER_FORMAT.format(browser_type), f"不支持的浏览器类型: {browser_type}")


class Registry:
    @staticmethod
    def exist(key_path, key_type="user") -> bool:
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        try:
            key = reg.OpenKey(head, key_path, 0, reg.KEY_READ)
            reg.CloseKey(key)
            return True
        except Exception:
            return False

    @staticmethod
    def create(key_path, key_type="user"):
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        keys = key_path.split("\\")
        head_key = reg.OpenKey(head, keys[0], 0, reg.KEY_ALL_ACCESS)
        opened_keys = [head_key]
        for key in keys[1:]:
            head_key = reg.CreateKey(head_key, key)
            opened_keys.append(head_key)
        opened_keys.reverse()
        for opened_key in opened_keys:
            reg.CloseKey(opened_key)

    @staticmethod
    def delete(key_path, sub_key, key_type="user"):
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_SET_VALUE)
        reg.DeleteKey(key, sub_key)
        reg.CloseKey(key)

    @staticmethod
    def add_string_value(key_path, value_name, value, key_type="user"):
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, value_name, 0, reg.REG_SZ, value)
        reg.CloseKey(key)

    @staticmethod
    def add_dword_value(key_path, value_name, value, key_type="user"):
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(key, value_name, 0, reg.REG_DWORD, value)
        reg.CloseKey(key)

    @staticmethod
    def query_value_ex(key, value_name):
        try:
            return reg.QueryValueEx(key, value_name)
        except Exception:
            return None, None

    @staticmethod
    def query_value(key_path, key_type="user"):
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        try:
            with reg.OpenKey(head, key_path, 0, reg.KEY_READ) as key:
                values = []
                i = 0
                while True:
                    try:
                        _, value_data, _ = reg.EnumValue(key, i)
                        values.append(value_data)
                        i += 1
                    except OSError:
                        break
                return values
        except Exception:
            return []

    @staticmethod
    def open_key(key_path, key_type="user"):
        head = reg.HKEY_LOCAL_MACHINE if key_type == "machine" else reg.HKEY_CURRENT_USER
        try:
            return reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        except Exception:
            raise BizException(REGISTRY_NOT_FOUND_FORMAT.format(key_path), f"注册表项 {key_path} 未找到")


def run_reg_file(plugin_id):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        policy_reg_path = os.path.join(project_root, "plugins", "windows_policy.reg")
        # check registry key exists
        path_machine_exists = Registry.exist(
            r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", key_type="machine"
        )

        if path_machine_exists:
            values_machine = Registry.query_value(
                r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist", key_type="machine"
            )
            logger.info(f"ExtensionInstallAllowlist machine values {values_machine}")
            if plugin_id in values_machine:
                return True
            else:
                os.startfile(policy_reg_path)
                logger.info("overwrite machine policy")
            return True
        else:
            os.startfile(policy_reg_path)
            return True
    except Exception as e:
        logger.error(f"reg error: {e}")
        return False


def kill_process(name: str):
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if f"{name}.exe" == proc.info["name"].lower():
                proc.kill()
        except Exception:
            pass


def start_browser(browser_path: str):
    try:
        os.startfile(browser_path)
    except Exception:
        pass


def get_app_path(name: str):
    app_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{}.exe".format(name)
    try:
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, app_path)
        path, _ = reg.QueryValueEx(key, "")
        return path
    except Exception:
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, app_path)
            path, _ = reg.QueryValueEx(key, "")
            return path
        except Exception:
            return None


def is_browser_running(browser_name: str) -> bool:
    proc_name = f"{browser_name}.exe"
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if proc_name.lower() == proc.info["name"].lower():
                return True
        except Exception:
            pass
    return False


def get_profile_list(base_path):
    profile_list = []
    if os.path.exists(base_path):
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and (item == "Default" or item.startswith("Profile")):
                profile_list.append(base_path + "\\" + item + "\\Preferences")
    return profile_list


def check_chrome_plugin(preferences_path_list, extension_id):
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, encoding="utf-8") as f:
                dict_msg = json.loads(f.read())
                try:
                    extension_info = dict_msg.get("extensions", {}).get("settings")
                    if extension_id in extension_info:
                        version = extension_info[extension_id].get("manifest", {}).get("version", "")
                        return True, version
                except Exception:
                    version = _get_install_signature_extension_version(preferences_path_list, extension_id)
                    if version:
                        return True, version
                    return False, ""
        else:
            logger.info(f"{file} does not exist")
    return False, ""


def _get_install_signature_extension_version(preferences_path_list, extension_id):
    versions = []
    for preferences_path in preferences_path_list:
        extensions_path = preferences_path.replace("Preferences", "Extensions")
        for item in os.listdir(extensions_path):
            if item == extension_id:
                item_path = os.path.join(extensions_path, item)
                version = max(os.listdir(item_path), key=lambda v: [int(x) for x in v.split(".")])
                version = version.split("_")[0] if "_" in version else version
                logger.info(f"{extensions_path}, {version}")
                versions.append(version)
    if versions:
        return max(versions, key=lambda v: [int(x) for x in v.split(".")])
    return ""


def remove_browser_setting(preferences_path_list, secure_preferences, extension_id, old_extension_ids=[]):
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, encoding="utf8") as f:
                dict_msg = json.loads(f.read())
                is_update = False

                uninstall_list = (
                    dict_msg.get("extensions").get("external_uninstalls", []) if dict_msg.get("extensions") else []
                )
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

                for old_id in old_extension_ids:
                    extension_info = dict_msg.get("extensions", {}).get("settings", {}).get(old_id, None)
                    if extension_info is not None:
                        del dict_msg["extensions"]["settings"][old_id]

                extension_info = dict_msg.get("extensions", {}).get("settings", {}).get(extension_id, None)
                if extension_info is not None:
                    del dict_msg["extensions"]["settings"][extension_id]
                    is_update = True

                if is_update:
                    with open(file, "w", encoding="utf8") as f:
                        json.dump(dict_msg, f)

    if os.path.exists(secure_preferences):
        os.remove(secure_preferences)


def remove_old_extensions(extension_path, old_extension_ids=[], old_extension_path_list=[]):
    for ext_id in old_extension_ids:
        if Registry.exist(extension_path + "\\" + ext_id):
            logger.info(f"delete old extension registry: {extension_path}\\{ext_id}")
            Registry.delete(extension_path, ext_id)
    for ext_path in old_extension_path_list:
        if os.path.exists(ext_path):
            try:
                shutil.rmtree(ext_path)
                logger.info(f"delete old extension file: {ext_path}")
            except Exception:
                pass
