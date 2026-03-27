import configparser
import json
import os
import platform
import re

from astronverse.browser_plugin.error import BizException, FIREFOX_PROFILE_NOT_FOUND, INVALID_FILENAME
from astronverse.browser_plugin.config import Config


def parse_filename_regex(filename):
    pattern = (
        r"^(?P<browser>[a-zA-Z0-9-]+)-(?P<version>\d+(\.\d+)*)-(?P<hashid>[a-zA-Z0-9]+)\.(?P<extension>[a-zA-Z]+)$"
    )
    match = re.match(pattern, filename)
    if match:
        return match.group("browser"), match.group("version"), match.group("hashid"), match.group("extension")
    raise BizException(INVALID_FILENAME, "文件名不匹配预期格式")


def get_latest_plugin(plugins, pre_name):
    filtered_plugins = [f for f in plugins if f.startswith(pre_name + "-")]
    if not filtered_plugins:
        raise Exception("plugins not found...")
    plugins_versions = []
    for plugin in filtered_plugins:
        try:
            _, version, _, _ = parse_filename_regex(plugin)
            plugins_versions.append((plugin, version))
        except Exception:
            continue
    if not plugins_versions:
        raise Exception("No valid plugins found...")
    return max(plugins_versions, key=lambda x: [int(v) for v in x[1].split(".")])[0]


class FirefoxUtils:
    firefox_plugin_id = Config.FIREFOX_PLUGIN_ID
    firefox_plugin_file_ids = Config.FIREFOX_PLUGIN_FILE_IDS

    @staticmethod
    def get_firefox_command():
        """Unix only: find firefox executable via `which`"""
        import subprocess
        try:
            for version in ["firefox", "firefox-esr"]:
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
        elif platform.system() == "Darwin":
            profile_path = os.path.expanduser("~/Library/Application Support/Firefox")
        else:
            profile_path = os.path.expanduser("~/.mozilla/{0}".format(firefox_command))

        config = configparser.ConfigParser()
        config.read(os.path.join(profile_path, "installs.ini"))
        sections = config.sections()
        if sections:
            default_profile = config[sections[0]]["Default"]
            return os.path.join(profile_path, default_profile)
        raise BizException(FIREFOX_PROFILE_NOT_FOUND, "Firefox profile 未找到")

    @staticmethod
    def check(firefox_command="firefox"):
        try:
            default_profile_path = FirefoxUtils.get_default_profile_path(firefox_command)
            extensions_path = os.path.join(default_profile_path, "extensions.json")
            if os.path.exists(extensions_path):
                with open(extensions_path, encoding="utf-8") as f:
                    dict_msg = json.loads(f.read())
                    for addon in dict_msg["addons"]:
                        if addon["id"] == FirefoxUtils.firefox_plugin_id:
                            return True, addon["version"]
                        for file_id in FirefoxUtils.firefox_plugin_file_ids:
                            if addon["sourceURI"] and file_id in addon["sourceURI"]:
                                return True, addon["version"]
                    return False, ""
            return False, ""
        except Exception:
            return False, ""
