from dataclasses import dataclass
from typing import Dict, Optional
from astronverse.executorv2.config import Config
from astronverse.executorv2.flow.params import Param
from astronverse.executorv2.flow.storage import IStorage, HttpStorage
from astronverse.executorv2.flow.syntax import IParam
from astronverse.executorv2.run import report
from astronverse.executorv2.run.debug import Debug
from astronverse.executorv2.run.report import Report
from astronverse.executorv2.logger import logger


@dataclass
class ProjectInfo:
    project_id: str = ""
    project_name: str = ""
    mode: str = ""
    version: str = ""
    requirement: dict = None
    gateway_port: int = 0

    def __json__(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "mode": self.mode,
            "version": self.version,
            "requirement": self.requirement,
            "gateway_port": self.gateway_port
        }


@dataclass
class ProcessInfo:
    process_file_name: str = ""
    process_id: str = ""
    process_category: str = ""
    process_name: str = ""
    import_python: set = None
    breakpoint: set = None

    def __init__(self):
        self.import_python = set()
        self.breakpoint = set()

    def __json__(self):
        return {
            "process_file_name": self.process_file_name,
            "process_id": self.process_id,
            "process_category": self.process_category,
            "process_name": self.process_name,
            "import_python": list(self.import_python),
        }


@dataclass
class AstGlobals:
    project_info: ProjectInfo = None
    process_info: Dict[str, ProcessInfo] = None

    def __init__(self):
        self.project_info = ProjectInfo()
        self.process_info = {}

    def __json__(self):
        return {
            "project_info": self.project_info.__json__(),
            "process_info": {k: v.__json__() for k, v in self.process_info.items()},
        }


class Svc:

    def __init__(self, conf, debug_model):
        # 全局类型
        self.conf: Config = conf

        # 工具类
        self.param: IParam = Param(self)
        self.storage: IStorage = HttpStorage(self)
        self.report = Report(self)
        report.code = self.report

        # 解析树变量
        self.ast_globals: AstGlobals = AstGlobals()
        self.ast_curr_info: {}

        # 运行时
        self.debug_model = debug_model
        self.debug_handler: Optional[Debug] = None

    def add_project_info(self, project_id: str, mode: str, version: str, project_name: str, requirement: dict, gateway_port: int):
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
    
    def get_process_info(self, process_id):
        if process_id not in self.ast_globals.process_info:
            return None
        return self.ast_globals.process_info[process_id]
    
    def add_import_python(self, process_id: str, import_python: str):
        if process_id not in self.ast_globals.process_info:
            self.ast_globals.process_info[process_id] = ProcessInfo()
        self.ast_globals.process_info[process_id].import_python.add(import_python)

    def get_import_python(self, process_id):
        if process_id not in self.ast_globals.process_info:
            return None
        return self.ast_globals.process_info[process_id].import_python

    def add_breakpoint(self, process_id, line):
        if process_id not in self.ast_globals.process_info:
            self.ast_globals.process_info[process_id] = ProcessInfo()
        self.ast_globals.process_info[process_id].breakpoint.add(line)

    @staticmethod
    def end(status, reason, traceback):
        logger.info("{}.{}.{}".format(status, reason, traceback))
