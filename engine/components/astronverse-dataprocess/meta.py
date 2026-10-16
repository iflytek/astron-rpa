import json
import pathlib

from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.locale import apply_locale, load_locale
from astronverse.actionlib.tree import treeMg
from astronverse.baseline.config.config import load_config
from astronverse.dataprocess.data import DataProcess
from astronverse.dataprocess.dataconvert import DataConvertProcess
from astronverse.dataprocess.dict import DictProcess
from astronverse.dataprocess.list import ListProcess
from astronverse.dataprocess.math import MathProcess
from astronverse.dataprocess.string import StringProcess
from astronverse.dataprocess.time import TimeProcess

LANGS = ("zh_CN", "en_US")

if __name__ == "__main__":
    version = load_config("pyproject.toml")["project"]["version"]
    config.set_config_file("config.yaml")
    atomicMg.register(DataProcess, version=version)
    atomicMg.register(StringProcess, version=version)
    atomicMg.register(ListProcess, version=version)
    atomicMg.register(DictProcess, version=version)
    atomicMg.register(MathProcess, version=version)
    atomicMg.register(DataConvertProcess, version=version)
    atomicMg.register(TimeProcess, version=version)
    atomicMg.meta()

    base_meta: dict = json.loads(pathlib.Path("meta.json").read_text(encoding="utf-8"))
    for lang in LANGS:
        locale = load_locale(lang)
        out_dir = pathlib.Path("resources") / lang
        out_dir.mkdir(parents=True, exist_ok=True)

        # meta.json
        meta_path = out_dir / "meta.json"
        meta_path.write_text(
            json.dumps(apply_locale(base_meta, locale), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        treeMg.root_nodes = {}
        treeMg.load_default_node_config(locale=lang)
        treeMg.build_from_meta_and_config(str(meta_path), "config.yaml")
        tree_path = out_dir / "tree.json"
        treeMg.meta(str(tree_path))
