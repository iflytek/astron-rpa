import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional


# Cache for user settings to avoid repeated file reads
_user_settings_cache: Optional[Dict[str, Any]] = None


def load_user_settings(force_reload: bool = False, file_path: str = ".setting.json", times: int = 5) -> Dict[str, Any]:
    """Load user settings from .setting.json file

    Args:
        force_reload: If True, reload from file even if cached
        file_path: Path to settings file (default: ".setting.json")
        times: Number of retry attempts if file read fails (default: 5)

    Returns:
        Dictionary containing user settings with keys like:
        - language: Language code (e.g., 'zh-CN', 'en-US')
        - platform: Platform identifier (e.g., 'win32', 'darwin')
        - version: Application version
        - commonSetting: Common application settings
        - shortcutConfig: Keyboard shortcuts configuration
        - videoForm: Video recording settings
        - msgNotifyForm: Message notification settings

    Note:
        Returns empty dict if .setting.json doesn't exist or fails to load.
        The result is cached after first load for performance unless force_reload is True.
    """
    global _user_settings_cache

    # Return cached settings if available and not forcing reload
    if _user_settings_cache is not None and not force_reload:
        return _user_settings_cache

    settings = {}
    for i in range(times):
        try:
            config_path = Path(file_path)
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    _user_settings_cache = settings
                    return settings
        except Exception:
            time.sleep(0.1)

    _user_settings_cache = settings
    return settings


def load_config(url, file_type=None, wait_time=0):
    """Load and parse configuration file

    Args:
        url: Configuration file path
        file_type: File type, supports "yaml", "json" and "toml". If None, will auto-detect based on file extension
        wait_time: Wait time in seconds if file doesn't exist (default: 0, no wait)
    """

    if not os.path.exists(url):
        if wait_time > 0:
            time.sleep(wait_time)
        if not os.path.exists(url):
            raise FileNotFoundError("Configuration file not found: {}".format(url))

    if file_type is None:
        file_extension = os.path.splitext(url)[1].lower()
        if file_extension in [".yml", ".yaml"]:
            file_type = "yaml"
        elif file_extension == ".json":
            file_type = "json"
        elif file_extension == ".toml":
            file_type = "toml"
        else:
            raise Exception("Cannot auto-detect file type from extension: {}".format(file_extension))

    with open(url, encoding="utf-8") as config_file:
        if file_type == "yaml":
            import yaml

            data = yaml.load(config_file, Loader=yaml.FullLoader)
        elif file_type == "json":
            import json

            data = json.load(config_file)
        elif file_type == "toml":
            import toml

            data = toml.load(config_file)
        else:
            raise Exception("Configuration file parsing does not support this type {}".format(file_type))
    return data
