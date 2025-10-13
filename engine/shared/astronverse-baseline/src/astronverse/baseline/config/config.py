import os
import time


def load_config(url, file_type="yaml", wait_time=0):
    """Load and parse configuration file

    Args:
        url: Configuration file path
        file_type: File type, supports "yaml", "json" and "toml"
        wait_time: Wait time in seconds if file doesn't exist (default: 0, no wait)
    """

    if not os.path.exists(url):
        if wait_time > 0:
            time.sleep(wait_time)
        if not os.path.exists(url):
            raise FileNotFoundError("Configuration file not found: {}".format(url))

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
