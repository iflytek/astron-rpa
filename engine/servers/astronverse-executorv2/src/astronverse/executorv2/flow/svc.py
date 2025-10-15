from dataclasses import dataclass
from typing import Dict
from astronverse.executorv2.flow.params import Param
from astronverse.executorv2.flow.storage import IStorage, HttpStorage
from astronverse.executorv2.flow.syntax import IParam


@dataclass
class AstGlobals:
    import_python: set = None
    process_file_name: str = ""
    process_id: str = ""
    process_category: str = ""
    process_name: str = ""

    def __init__(self):
        self.import_python: set = set()

    def to_project_json(self):
        return {
            "process_file_name": self.process_file_name,
            "process_id": self.process_id,
            "process_category": self.process_category,
        }


class Svc:

    def __init__(self, args, conf):
        # 全局类型
        self.conf = conf
        self.port = args.port
        self.gateway_port = args.gateway_port

        # 工具类
        self.param: IParam = Param(self)
        self.storage: IStorage = HttpStorage(self)

        # 解析树全局变量字典
        self.ast_globals: Dict[str, AstGlobals] = {}
        self.ast_curr_info: {}

    def set_process_info(self, process_id, process_file_name, process_category, process_name):
        if process_id not in self.ast_globals:
            self.ast_globals[process_id] = AstGlobals()
        self.ast_globals[process_id].process_id = process_id
        self.ast_globals[process_id].process_file_name = process_file_name
        self.ast_globals[process_id].process_category = process_category
        self.ast_globals[process_id].process_name = process_name

    def add_import_python(self, process_id: str, import_python: str):
        if process_id not in self.ast_globals:
            self.ast_globals[process_id] = AstGlobals()
        self.ast_globals[process_id].import_python.add(import_python)

    def get_import_python(self, process_id):
        if process_id not in self.ast_globals:
            return None
        return self.ast_globals[process_id].import_python
