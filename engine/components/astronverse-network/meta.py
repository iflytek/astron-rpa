import toml
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.ftp import FTP
from astronverse.network import Network


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(FTP, group_key="Network", version=get_version())
    atomicMg.register(Network, group_key="Network", version=get_version())
    atomicMg.meta()
