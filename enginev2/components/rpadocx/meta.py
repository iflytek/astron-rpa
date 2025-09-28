import toml
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.types import typesMg
from rpadocx.docx import Docx
from rpadocx.docx_obj import DocxObj


def get_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["project"]["version"]


if __name__ == "__main__":
    config.default_value["atomic"] = {
        "icon": "icon-list-read-word",
    }
    config.set_config_file("config.yaml")
    atomicMg.register(Docx, version=get_version())
    atomicMg.meta()

    config.set_config_file("config_type.yaml")
    typesMg.register_types(DocxObj, version=get_version(), channel="global", template="Word对象")
    typesMg.meta()
