import psutil
import winreg as reg
import json
import os
import platform
import re
import subprocess
import configparser


def parse_filename_regex(filename):
    # 正则表达式匹配模式
    pattern = (
        r"^(?P<browser>[a-zA-Z0-9-]+)-(?P<version>\d+(\.\d+)*)-(?P<hashid>[a-zA-Z0-9]+)\.(?P<extension>[a-zA-Z]+)$"
    )
    match = re.match(pattern, filename)
    if match:
        # 使用命名捕获组来提取各部分
        browser = match.group("browser")
        version = match.group("version")
        hashid = match.group("hashid")
        extension = match.group("extension")
        return browser, version, hashid, extension
    else:
        raise ValueError("Filename does not match expected pattern")


class FirefoxUtils:
    firefox_plugin_id = "iflyrpa@iflytek.com"

    @staticmethod
    def get_firefox_command():
        try:
            """
            检查系统上是否安装了Firefox或Firefox ESR。

            返回:
                bool: 如果安装了Firefox或Firefox ESR则返回True，否则返回False。
            """
            # 可能的Firefox二进制文件名列表
            firefox_versions = ["firefox", "firefox-esr"]

            # 遍历每个版本并检查是否安装
            for version in firefox_versions:
                result = subprocess.run(["which", version], capture_output=True, text=True)
                # 检查'which'命令是否找到了二进制文件
                if result.returncode == 0:
                    return version

        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def get_default_profile_path(firefox_command="firefox"):
        """
        获取 Firefox 配置文件路径
        :return:
        """
        if platform.system() == "Windows":
            profile_path = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox")
        elif platform.system() == "Darwin":  # macOS
            profile_path = os.path.expanduser("~/Library/Application Support/Firefox")
        else:  # Linux
            profile_path = os.path.expanduser("~/.mozilla/{0}".format(firefox_command))

        # 找到默认配置文件夹
        config = configparser.ConfigParser()
        config.read(os.path.join(profile_path, "installs.ini"))
        sections = config.sections()
        # 检查是否有任何 section 存在
        if sections:
            default_profile = config[sections[0]]["Default"]
            return os.path.join(profile_path, default_profile)
        else:
            raise FileNotFoundError("没有找到默认配置文件。请确保已创建 Firefox 配置文件。")

    @staticmethod
    def check(firefox_command="firefox"):
        """
        检查插件是否安装, 并返回插件的版本号
        :return:
        """
        try:
            default_profile_path = FirefoxUtils.get_default_profile_path(firefox_command)
            # extensions.json 文件中保存了插件的相关信息
            extensions_path = os.path.join(default_profile_path, "extensions.json")
            if os.path.exists(extensions_path):
                with open(extensions_path, "r", encoding="utf8") as f:
                    dict_msg = json.loads(f.read())
                    for addon in dict_msg["addons"]:
                        if addon["id"] == FirefoxUtils.firefox_plugin_id:
                            return True, addon["version"]
                    return False, None
            else:
                return False, None
        except FileNotFoundError:
            return False, None


class Registry(object):
    @staticmethod
    def exist(key_path, key_type="user") -> bool:
        """
        检测注册表是否存在
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        try:
            key = reg.OpenKey(head, key_path, 0, reg.KEY_READ)
            reg.CloseKey(key)
            return True
        except Exception as e:
            return False

    @staticmethod
    def create(key_path, key_type="user"):
        """
        创建项
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
        删除项
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        key = reg.OpenKey(head, key_path, 0, reg.KEY_SET_VALUE)
        # 删除子项
        reg.DeleteKey(key, sub_key)
        reg.CloseKey(key)

    @staticmethod
    def add_string_value(key_path, value_name, value, key_type="user"):
        """
        添加字符串kv对
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
        添加dword kv对
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
        查询注册表值
        """
        try:
            return reg.QueryValueEx(key, value_name)
        except FileNotFoundError:
            return None, None

    @staticmethod
    def query_value(key_path, key_type="user"):
        """
        查询注册表值
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
                # print(f"ExtensionInstallAllowlist下的所有值: {values}")
                return values
        except FileNotFoundError:
            return []

    @staticmethod
    def open_key(key_path, key_type="user"):
        """
        打开注册表键
        """
        if key_type == "machine":
            head = reg.HKEY_LOCAL_MACHINE
        else:
            head = reg.HKEY_CURRENT_USER
        try:
            return reg.OpenKey(head, key_path, 0, reg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            raise FileNotFoundError(f"注册表键 {key_path} 不存在。")


def kill_process(name: str):
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if "{}.exe".format(name) == proc.info["name"].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def check_chrome_plugin(preferences_path_list, extension_id):
    """
    检查类 chrome 浏览器插件的安装状态
    :return: 插件是否安装，安装版本
    """
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, "r", encoding="utf8") as f:
                content = f.read()
                dict_msg = json.loads(content)
                try:
                    extension_info = dict_msg["extensions"]["settings"]
                    if extension_id in extension_info:
                        version = extension_info[extension_id].get("manifest", {}).get("version", "")
                        return True, version
                    else:
                        return False, None
                except KeyError:
                    return False, None

    return False, None


def remove_browser_setting(preferences_path_list, secure_preferences, extension_id):
    """
    删除preferences中插件信息
    :return:
    """
    for file in preferences_path_list:
        if os.path.exists(file):
            with open(file, "r", encoding="utf8") as f:
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

                if is_update:
                    with open(file, "w", encoding="utf8") as f:
                        json.dump(dict_msg, f)
            break

    # 删除用户偏好设置
    if os.path.exists(secure_preferences):
        os.remove(secure_preferences)
