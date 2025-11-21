from typing import Dict

from astronverse.executor import AstGlobals, ProcessInfo, AtomicInfo, ComponentInfo
from astronverse.executor.config import Config
from astronverse.executor.flow.params import Param
from astronverse.executor.flow.storage import IStorage, HttpStorage
from astronverse.executor.flow.syntax import IParam


class FlowSvc:
    def __init__(self, conf):
        # 全局类型
        self.conf: Config = conf

        # 工具类
        self.param: IParam = Param(self)
        self.storage: IStorage = HttpStorage(self)

        # 解析树变量
        self.ast_globals_dict: Dict[str, AstGlobals] = {}
        self.ast_curr_info = {}

    def add_project_info(
        self,
        project_id: str,
        mode: str,
        version: str,
        project_name: str,
        requirement: dict,
        gateway_port: int,
        global_var: dict,
    ):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()

        self.ast_globals_dict[project_id].project_info.project_id = project_id
        self.ast_globals_dict[project_id].project_info.project_name = project_name
        self.ast_globals_dict[project_id].project_info.mode = mode
        self.ast_globals_dict[project_id].project_info.version = version
        self.ast_globals_dict[project_id].project_info.requirement = requirement
        self.ast_globals_dict[project_id].project_info.gateway_port = gateway_port
        self.ast_globals_dict[project_id].project_info.global_var = global_var

    def add_component_info(
        self,
        project_id: str,
        component_id: str,
        component_name: str,
        version: str,
        requirement: dict,
        component_file_name: str,
    ):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if component_id not in self.ast_globals_dict[project_id].component_info:
            self.ast_globals_dict[project_id].component_info[component_id] = ComponentInfo()
        self.ast_globals_dict[project_id].component_info[component_id].component_name = component_name
        self.ast_globals_dict[project_id].component_info[component_id].version = version
        self.ast_globals_dict[project_id].component_info[component_id].requirement = requirement
        self.ast_globals_dict[project_id].component_info[component_id].component_file_name = component_file_name

    def add_process_info(
        self, project_id: str, process_id: str, process_category: str, process_name, process_file_name
    ):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if process_id not in self.ast_globals_dict[project_id].process_info:
            self.ast_globals_dict[project_id].process_info[process_id] = ProcessInfo()
        self.ast_globals_dict[project_id].process_info[process_id].process_id = process_id
        self.ast_globals_dict[project_id].process_info[process_id].process_category = process_category
        self.ast_globals_dict[project_id].process_info[process_id].process_name = process_name
        self.ast_globals_dict[project_id].process_info[process_id].process_file_name = process_file_name

    def add_import_python(self, project_id: str, process_id: str, import_python: str):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if process_id not in self.ast_globals_dict[project_id].process_info:
            self.ast_globals_dict[project_id].process_info[process_id] = ProcessInfo()
        self.ast_globals_dict[project_id].process_info[process_id].import_python.add(import_python)

    def get_import_python(self, project_id: str, process_id: str):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if process_id not in self.ast_globals_dict[project_id].process_info:
            return None
        return self.ast_globals_dict[project_id].process_info[process_id].import_python

    def add_breakpoint(self, project_id: str, process_id: str, line: int):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if process_id not in self.ast_globals_dict[project_id].process_info:
            self.ast_globals_dict[project_id].process_info[process_id] = ProcessInfo()
        self.ast_globals_dict[project_id].process_info[process_id].breakpoint.add(line)

    def add_process_meta(self, project_id: str, process_id: str, process_meta: dict):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if process_id not in self.ast_globals_dict[project_id].process_info:
            self.ast_globals_dict[project_id].process_info[process_id] = ProcessInfo()
        self.ast_globals_dict[project_id].process_info[process_id].process_meta = process_meta

    def add_atomic_info(self, project_id: str, atomic_key: str, atomic_params: dict):
        if project_id not in self.ast_globals_dict:
            self.ast_globals_dict[project_id] = AstGlobals()
        if atomic_key not in self.ast_globals_dict[project_id].atomic_info:
            self.ast_globals_dict[project_id].atomic_info[atomic_key] = AtomicInfo()
        self.ast_globals_dict[project_id].atomic_info[atomic_key].key = atomic_key
        self.ast_globals_dict[project_id].atomic_info[atomic_key].params_name = atomic_params
