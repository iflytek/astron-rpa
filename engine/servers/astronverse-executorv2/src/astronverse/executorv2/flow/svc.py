from dataclasses import dataclass
from typing import Dict
from astronverse.executorv2.flow.params import Param
from astronverse.executorv2.flow.storage import IStorage, HttpStorage
from astronverse.executorv2.flow.syntax import IParam


class ProjectInfo:
    project_id: str = ""
    project_name: str = ""
    mode: str = ""
    version: str = ""


@dataclass
class ProcessInfo:
    process_file_name: str = ""
    process_id: str = ""
    process_category: str = ""
    process_name: str = ""
    import_python: set = None

    def __init__(self):
        self.import_python = set()


@dataclass
class AstGlobals:
    project_info: ProjectInfo = None
    process_info: Dict[str, ProcessInfo] = None

    def __init__(self):
        self.project_info = ProjectInfo()
        self.process_info = {}


class Svc:

    def __init__(self, args, conf):
        # 全局类型
        self.conf = conf
        self.port = args.port
        self.gateway_port = args.gateway_port

        # 工具类
        self.param: IParam = Param(self)
        self.storage: IStorage = HttpStorage(self)

        # 解析树变量
        self.ast_globals: AstGlobals = AstGlobals()
        self.ast_curr_info: {}
    
    def add_project_info(self, project_id: str, mode: str, version: str, project_name: str):
        self.ast_globals.project_info.project_id = project_id
        self.ast_globals.project_info.project_name = project_name
        self.ast_globals.project_info.mode = mode
        self.ast_globals.project_info.version = version

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

    def get_import_python(self, process_id):
        if process_id not in self.ast_globals.process_info:
            return None
        return self.ast_globals.process_info[process_id].import_python
