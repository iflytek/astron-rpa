from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg
from astronverse.baseline.config.config import load_config
from astronverse.software.software import Software
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parent


def get_version():
    pyproject_data = load_config(str(MODULE_DIR / "pyproject.toml"))
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file(str(MODULE_DIR / "config.yaml"))
    atomicMg.register(Software, version=get_version())
    atomicMg.meta()

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")