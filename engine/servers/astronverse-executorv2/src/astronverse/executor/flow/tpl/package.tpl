import os.path
from typing import Optional, Any
from astronverse.actionlib.types import Pick
from astronverse.workflowlib.storage import HttpStorage
from astronverse.workflowlib.config import config
from astronverse.workflowlib.params import ComplexParamParser

conf = config({{PACKAGE_PATH}})

project_info = conf.get("project_info", {})
process_info = conf.get("process_info", {})
component_info = conf.get("component_info", {})

storage = HttpStorage(project_info.get("gateway_port"), project_info.get("mode"))


def module(module_id) -> Optional[str]:
    if module_id not in process_info:
        return None
    name = process_info[module_id].get("process_file_name")
    if not name:
        return name
    return os.path.splitext(name)[0]


def component(component_id) -> Optional[str]:
    if component_id not in component_info:
        return None
    name = component_info[component_id].get("component_file_name")
    if not name:
        return name
    return os.path.splitext(name)[0]


def complex_param_parser(complex_param: dict) -> dict:
    return ComplexParamParser.evaluate_params(ComplexParamParser.parse_params(complex_param))


def element(element_id) -> Optional[Pick]:
    res = storage.element_detail(
        project_info.get("project_id"),
        element_id,
        project_info.get("mode"),
        project_info.get("version")
    )
    if res is None:
        return None
    res = complex_param_parser(res)
    return Pick(res)


def element_vision(url) -> str:
    return storage.element_vision_detail(url)


gv = {}
pass
{{GLOBAL}}
