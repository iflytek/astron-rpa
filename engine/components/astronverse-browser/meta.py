from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg
from astronverse.actionlib.types import typesMg
from astronverse.baseline.config.config import load_config
from astronverse.browser.browser import Browser
from astronverse.browser.browser_element import BrowserElement
from astronverse.browser.browser_script import BrowserScript
from astronverse.browser.browser_software import BrowserSoftware


def get_version():
    pyproject_data = load_config("pyproject.toml")
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(BrowserElement, version=get_version())
    atomicMg.register(BrowserSoftware, version=get_version())
    atomicMg.register(BrowserScript, version=get_version())
    atomicMg.meta()

    # 生成 tree.json
    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")

    config.set_config_file("config_type.yaml")
    typesMg.register_types(Browser, version=get_version(), channel="global", template="Browser对象")
    typesMg.meta()
