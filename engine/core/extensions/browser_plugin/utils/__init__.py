import configparser
import json
import os
import platform
import re
import subprocess

from ..config import Config


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
                result = subprocess.run(["which", version], capture_output=True, text=True)
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
                with open(extensions_path, "r", encoding="utf8") as f:
                    dict_msg = json.loads(f.read())
                    for addon in dict_msg["addons"]:
                        if addon["id"] == FirefoxUtils.firefox_plugin_id:
                            return True, addon["version"]
                    return False, ""
            else:
                return False, ""
        except FileNotFoundError:
            return False, ""
