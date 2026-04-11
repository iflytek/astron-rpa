from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.types import typesMg
from astronverse.actionlib.tree import treeMg
from astronverse.baseline.config.config import load_config
from astronverse.word.docx import Docx
from astronverse.word.docx_obj import DocumentObject


def get_version():
    pyproject_data = load_config("pyproject.toml")
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(Docx, version=get_version())
    atomicMg.meta()

    config.set_config_file("config_type.yaml")
    typesMg.register_types(DocumentObject, version=get_version(), channel="global", template="Word对象")
    typesMg.meta()

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")