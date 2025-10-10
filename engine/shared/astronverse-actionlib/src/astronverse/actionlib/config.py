import os

from astronverse.actionlib.error import *


def load_config(url, file_type="yaml"):
    """读取并解析配置文件"""
    
    with open(url, "r", encoding="utf-8") as config_file:
        if file_type == "yaml":
            import yaml
            try:
                data = yaml.load(config_file, Loader=yaml.FullLoader)
            except Exception as e:
                raise BaseException(CONFIG_LOAD_ERROR.format(config_file), "配置文件加载出错 {}".format(e)) from e
        elif file_type == "json":
            import json
            try:
                data = json.load(config_file)
            except Exception as e:
                raise BaseException(CONFIG_LOAD_ERROR.format(config_file), "配置文件加载出错 {}".format(e)) from e
        else:
            raise BaseException(
                CONFIG_TYPE_ERROR.format(file_type), "配置文件解析不支持该类型 {}".format(file_type)
            )
    return data


class Config:
    """读取配置"""

    data: dict = {}

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.set_config_file(os.path.join(script_dir, "config.yaml"))

    def set_config_file(self, url, file_type="yaml"):
        data = load_config(url, file_type)
        if not data or not isinstance(data, dict):
            return

        # 合并配置数据
        for key, val in data.items():
            if key in self.data:
                self.data[key].update(val)
            else:
                self.data[key] = val

    def get(self, *args):
        data = self.data
        for key in args:
            if data is None:
                break
            data = data.get(key, None)
        return data


config = Config()
