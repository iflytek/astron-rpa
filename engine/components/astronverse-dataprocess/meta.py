import toml
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.dataprocess.data import DataProcess
from astronverse.dataprocess.dataconvert import DataConvertProcess
from astronverse.dataprocess.dict import DictProcess
from astronverse.dataprocess.list import ListProcess
from astronverse.dataprocess.math import MathProcess
from astronverse.dataprocess.string import StringProcess
from astronverse.dataprocess.time import TimeProcess


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(DataProcess, version=get_version())
    atomicMg.register(StringProcess, version=get_version())
    atomicMg.register(ListProcess, version=get_version())
    atomicMg.register(DictProcess, version=get_version())
    atomicMg.register(MathProcess, version=get_version())
    atomicMg.register(DataConvertProcess, version=get_version())
    atomicMg.register(TimeProcess, version=get_version())
    atomicMg.meta()
