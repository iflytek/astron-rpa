from astronverse.executor import AstGlobals, ProcessInfo, AtomicInfo
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
        self.ast_globals: AstGlobals = AstGlobals()
        self.ast_curr_info: {}

    def add_project_info(self, project_id: str, mode: str, version: str, project_name: str,
                         requirement: dict, gateway_port: int):
        self.ast_globals.project_info.project_id = project_id
        self.ast_globals.project_info.project_name = project_name
        self.ast_globals.project_info.mode = mode
        self.ast_globals.project_info.version = version
        self.ast_globals.project_info.requirement = requirement
        self.ast_globals.project_info.gateway_port = gateway_port

    def add_process_info(self, process_id: str, process_category: str, process_name, process_file_name):
        if process_id not in self.ast_globals.process_info:
            self.ast_globals.process_info[process_id] = ProcessInfo()
        self.ast_globals.process_info[process_id].process_id = process_id
        self.ast_globals.process_info[process_id].process_category = process_category
        self.ast_globals.process_info[process_id].process_name = process_name
        self.ast_globals.process_info[process_id].process_file_name = process_file_name

    def add_import_python(self, process_id: str, import_python: str):
        if process_id not in self.ast_globals.process_info:
            self.ast_globals.process_info[process_id] = ProcessInfo()
        self.ast_globals.process_info[process_id].import_python.add(import_python)

    def get_import_python(self, process_id: str):
        if process_id not in self.ast_globals.process_info:
            return None
        return self.ast_globals.process_info[process_id].import_python

    def add_breakpoint(self, process_id: str, line: int):
        if process_id not in self.ast_globals.process_info:
            self.ast_globals.process_info[process_id] = ProcessInfo()
        self.ast_globals.process_info[process_id].breakpoint.add(line)
    
    def add_process_meta(self, process_id: str, process_meta: dict):
        if process_id not in self.ast_globals.process_info:
            self.ast_globals.process_info[process_id] = ProcessInfo()
        self.ast_globals.process_info[process_id].process_meta = process_meta
    
    def add_atomic_info(self, atomic_key: str, atomic_params: dict):
        if atomic_key not in self.ast_globals.atomic_info:
            self.ast_globals.atomic_info[atomic_key] = AtomicInfo()
        self.ast_globals.atomic_info[atomic_key].key = atomic_key
        self.ast_globals.atomic_info[atomic_key].params_name = atomic_params
