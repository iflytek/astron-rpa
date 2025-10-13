from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.baseline.config.config import load_config
from astronverse.system.clipboard import Clipboard
from astronverse.system.compress import Compress
from astronverse.system.file import File
from astronverse.system.folder import Folder
from astronverse.system.process import Process
from astronverse.system.system import System


def get_version():
    pyproject_data = load_config("pyproject.toml")
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(Clipboard, group_key="System", version=get_version())
    atomicMg.register(Compress, group_key="System", version=get_version())
    atomicMg.register(File, group_key="File", version=get_version())
    atomicMg.register(Folder, group_key="Folder", version=get_version())
    atomicMg.register(Process, group_key="System", version=get_version())
    atomicMg.register(System, group_key="System", version=get_version())
    atomicMg.meta()
