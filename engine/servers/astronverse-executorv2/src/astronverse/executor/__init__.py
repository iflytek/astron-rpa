from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class AtomicInfo:
    key: str = ""
    params_name: dict = ""

    def __json__(self):
        return {
            "key": self.key,
            "params_name": self.params_name
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            key=data.get("key", ""),
            params_name=data.get("params_name", {})
        )


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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            project_id=data.get("project_id", ""),
            project_name=data.get("project_name", ""),
            mode=data.get("mode", ""),
            version=data.get("version", ""),
            requirement=data.get("requirement", {}),
            gateway_port=int(data.get("gateway_port", 0))
        )


@dataclass
class ProcessInfo:
    process_file_name: str = ""
    process_id: str = ""
    process_category: str = ""
    process_name: str = ""
    import_python: set = None
    breakpoint: set = None
    process_meta: list = None

    def __init__(self):
        self.import_python = set()
        self.breakpoint = set()
        self.process_meta = []

    def __json__(self):
        return {
            "process_file_name": self.process_file_name,
            "process_id": self.process_id,
            "process_category": self.process_category,
            "process_name": self.process_name,
            "breakpoint": list(self.breakpoint),
            "process_meta": self.process_meta
        }

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()
        instance.process_file_name = data.get("process_file_name", "")
        instance.process_id = data.get("process_id", "")
        instance.process_category = data.get("process_category", "")
        instance.process_name = data.get("process_name", "")
        instance.breakpoint = set(data.get("breakpoint", []))
        instance.process_meta = data.get("process_meta", [])
        return instance


@dataclass
class AstGlobals:
    project_info: ProjectInfo = None
    process_info: Dict[str, ProcessInfo] = None
    atomic_info: Dict[str, AtomicInfo] = None

    def __init__(self):
        self.project_info = ProjectInfo()
        self.process_info = {}
        self.atomic_info = {}

    def __json__(self):
        return {
            "project_info": self.project_info.__json__(),
            "process_info": {k: v.__json__() for k, v in self.process_info.items()},
            "atomic_info": {k: v.__json__() for k, v in self.atomic_info.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()
        instance.project_info = ProjectInfo.from_dict(data.get("project_info", {}))
        instance.process_info = {
            process_id: ProcessInfo.from_dict(process_data)
            for process_id, process_data in data.get("process_info", {}).items()
        }
        instance.atomic_info = {
            key: AtomicInfo.from_dict(atomic_data)
            for key, atomic_data in data.get("atomic_info", {}).items()
        }
        return instance


class ExecPosition(Enum):
    """
    指定工程在哪个阶段运行
    """

    # 工程列表页
    PROJECT_LIST = "PROJECT_LIST"
    # 工程编辑页
    EDIT_PAGE = "EDIT_PAGE"
    # 计划任务启动
    CRONTAB = "CRONTAB"
    # 执行器运行
    EXECUTOR = "EXECUTOR"


class ExecuteStatus(Enum):
    """
    机器人执行状态[远程状态]
    """

    SUCCESS = "robotSuccess"
    EXECUTE = "robotExecute"
    CANCEL = "robotCancel"
    FAIL = "robotFail"
