import os.path
from typing import Optional
from astronverse.actionlib.types import Pick
from astronverse.workflowlib.storage import HttpStorage
from astronverse.workflowlib.config import config

conf = config("./package.json")

storage = HttpStorage(conf.get("gateway_port"))

project_info = conf.get("project_info", {})
process_info = conf.get("process_info", {})


def module(module_id) -> Optional[str]:
    if module_id not in process_info:
        return None
    name = process_info[module_id].get("process_file_name")
    if not name:
        return name
    return os.path.splitext(name)[0]


def element(element_id) -> Optional[Pick]:
    res = storage.element_detail(
        project_info.get("project_id"),
        element_id,
        project_info.get("mode"),
        project_info.get("version")
    )
    if res is None:
        return None
    return Pick(res)


def element_img(url) -> str:
    return storage.element_img_detail(url)


gv = {}
pass
{{GLOBAL}}
