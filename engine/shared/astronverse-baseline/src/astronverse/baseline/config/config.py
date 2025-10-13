import os
import time


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
