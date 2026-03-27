import json
import os
import subprocess
import sys
import tempfile

import psutil

from astronverse.baseline.logger.logger import logger
from astronverse.browser_plugin import BrowserType, PluginData, PluginManager, PluginManagerCore
from astronverse.browser_plugin.error import BizException, UNSUPPORTED_BROWSER_FORMAT, NO_PERMISSION_FORMAT
from astronverse.browser_plugin.unix.chromium import ChromiumPluginManager


class BrowserPluginFactory(PluginManager):
    @staticmethod
    def get_support_browser():
        return [
            BrowserType.CHROME,
        ]

    @staticmethod
    def get_plugin_manager(browser_type: BrowserType, plugin_data: PluginData) -> PluginManagerCore:
        if browser_type == BrowserType.CHROME:
            return ChromiumPluginManager(plugin_data)
        else:
            raise BizException(UNSUPPORTED_BROWSER_FORMAT.format(browser_type), f"不支持的浏览器类型: {browser_type}")


def is_macos() -> bool:
    return sys.platform == "darwin"


def ensure_dir(path: str):
    """Create directory, requesting elevated permission on Linux if needed."""
    if os.path.exists(path):
        return
    if is_macos():
        os.makedirs(path, exist_ok=True)
        return
    # Linux: try direct creation, fall back to pkexec
    try:
        os.makedirs(path, exist_ok=True)
    except PermissionError:
        try:
            subprocess.run(
                ["pkexec", "mkdir", "-p", path],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["pkexec", "chmod", "777", path],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            raise BizException(NO_PERMISSION_FORMAT.format(path), f"没有权限写入 {path}")


def write_json(path: str, data: dict):
    """Write JSON file, requesting elevated permission on Linux if needed."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except PermissionError:
        if is_macos():
            raise BizException(NO_PERMISSION_FORMAT.format(path), f"没有权限写入 {path}")
        # Linux: write to temp then move with pkexec
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(data, tmp, indent=4)
            tmp_path = tmp.name
        try:
            subprocess.run(
                ["pkexec", "mv", tmp_path, path],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            os.unlink(tmp_path)
            raise BizException(NO_PERMISSION_FORMAT.format(path), f"没有权限写入 {path}")


def kill_process(process_name: str):
    """Kill process by name using killall."""
    try:
        subprocess.run(
            ["killall", process_name],
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def is_browser_running(browser_name: str) -> bool:
    """Check if a browser process is running by name."""
    for proc in psutil.process_iter(attrs=["name"]):
        try:
            if proc.info["name"] == browser_name:
                return True
        except Exception:
            pass
    return False


def start_browser(browser_cmd: list):
    """Start browser using command list."""
    try:
        subprocess.Popen(
            browser_cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        logger.error(f"start browser failed: {e}")


def get_profile_list(base_path: str) -> list:
    """Get list of Chrome profile Preferences file paths."""
    profile_list = []
    if os.path.exists(base_path):
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and (item == "Default" or item.startswith("Profile")):
                profile_list.append(os.path.join(base_path, item, "Preferences"))
    return profile_list


def check_chrome_plugin(preferences_path_list: list, extension_id: str) -> tuple:
    """Check if Chrome plugin is installed and return (installed, version)."""
    for file in preferences_path_list:
        if os.path.exists(file):
            try:
                with open(file, encoding="utf-8") as f:
                    dict_msg = json.loads(f.read())
                    extension_info = dict_msg.get("extensions", {}).get("settings")
                    if extension_info and extension_id in extension_info:
                        version = extension_info[extension_id].get("manifest", {}).get("version", "")
                        return True, version
            except Exception:
                version = _get_install_signature_extension_version(preferences_path_list, extension_id)
                if version:
                    return True, version
        else:
            logger.info(f"{file} does not exist")
    return False, ""


def _get_install_signature_extension_version(preferences_path_list: list, extension_id: str) -> str:
    """Get extension version from Extensions directory."""
    versions = []
    for preferences_path in preferences_path_list:
        extensions_path = preferences_path.replace("Preferences", "Extensions")
        if not os.path.exists(extensions_path):
            continue
        for item in os.listdir(extensions_path):
            if item == extension_id:
                item_path = os.path.join(extensions_path, item)
                if os.path.isdir(item_path):
                    version_dirs = os.listdir(item_path)
                    if version_dirs:
                        version = max(version_dirs, key=lambda v: [int(x) for x in v.split("_")[0].split(".")])
                        version = version.split("_")[0] if "_" in version else version
                        logger.info(f"{extensions_path}, {version}")
                        versions.append(version)
    if versions:
        return max(versions, key=lambda v: [int(x) for x in v.split(".")])
    return ""


def remove_browser_setting(preferences_path_list: list, secure_preferences: str, extension_id: str, old_extension_ids: list = []):
    """Remove extension settings from browser Preferences files."""
    for file in preferences_path_list:
        if os.path.exists(file):
            try:
                with open(file, encoding="utf8") as f:
                    dict_msg = json.loads(f.read())
                    is_update = False

                    uninstall_list = (
                        dict_msg.get("extensions", {}).get("external_uninstalls", [])
                    )
                    if extension_id in uninstall_list:
                        uninstall_list.remove(extension_id)
                        is_update = True

                    invalid_ids = (
                        dict_msg.get("install_signature", {}).get("invalid_ids", [])
                    )
                    if extension_id in invalid_ids:
                        invalid_ids.remove(extension_id)
                        is_update = True

                    apps = dict_msg.get("updateclientdata", {}).get("apps", {})
                    if extension_id in apps:
                        del apps[extension_id]
                        is_update = True

                    for old_id in old_extension_ids:
                        extension_info = dict_msg.get("extensions", {}).get("settings", {}).get(old_id, None)
                        if extension_info is not None:
                            del dict_msg["extensions"]["settings"][old_id]
                            is_update = True

                    extension_info = dict_msg.get("extensions", {}).get("settings", {}).get(extension_id, None)
                    if extension_info is not None:
                        del dict_msg["extensions"]["settings"][extension_id]
                        is_update = True

                    if is_update:
                        with open(file, "w", encoding="utf8") as f:
                            json.dump(dict_msg, f)
            except Exception as e:
                logger.error(f"remove browser setting failed: {e}")

    if os.path.exists(secure_preferences):
        try:
            os.remove(secure_preferences)
        except Exception as e:
            logger.error(f"remove secure preferences failed: {e}")


def remove_old_extensions(extension_dir: str, old_extension_ids: list = [], old_extension_path_list: list = []):
    """Remove old extension JSON files and directories."""
    for ext_id in old_extension_ids:
        old_json = os.path.join(extension_dir, f"{ext_id}.json")
        if os.path.exists(old_json):
            try:
                os.remove(old_json)
                logger.info(f"delete old extension json: {old_json}")
            except Exception as e:
                logger.error(f"delete old extension json failed: {e}")

    for ext_path in old_extension_path_list:
        if os.path.exists(ext_path):
            try:
                import shutil
                shutil.rmtree(ext_path)
                logger.info(f"delete old extension file: {ext_path}")
            except Exception as e:
                logger.error(f"delete old extension file failed: {e}")

