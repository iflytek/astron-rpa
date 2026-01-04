from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class AtomicInfo:
    key: str = ""
    params_name: dict = ""

    def __json__(self):
        return {"key": self.key, "params_name": self.params_name}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(key=data.get("key", ""), params_name=data.get("params_name", {}))


@dataclass
class ProjectInfo:
    project_id: str = ""
    project_name: str = ""
    mode: str = ""
    version: str = ""
    requirement: dict = None
    gateway_port: int = 0
    global_var: dict = None

    def __json__(self):
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "mode": self.mode,
            "version": self.version,
            "requirement": self.requirement,
            "gateway_port": self.gateway_port,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            project_id=data.get("project_id", ""),
            project_name=data.get("project_name", ""),
            mode=data.get("mode", ""),
            version=data.get("version", ""),
            requirement=data.get("requirement", {}),
            gateway_port=int(data.get("gateway_port", 0)),
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
            "process_meta": self.process_meta,
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
class ComponentInfo:
    component_name: str = ""
    version: str = ""
    requirement: dict = None
    component_file_name: str = ""

    def __json__(self):
        return {
            "component_name": self.component_name,
            "version": self.version,
            "requirement": self.requirement,
            "component_file_name": self.component_file_name,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            component_name=data.get("component_name", ""),
            version=data.get("version", ""),
            requirement=data.get("requirement", {}),
            component_file_name=data.get("component_file_name", ""),
        )


@dataclass
class SmartComponentInfo:
    smart_id: str = ""
    smart_version: str = ""
    component_file_name: str = ""
    smart_type: str = ""

    def __json__(self):
        return {
            "smart_id": self.smart_id,
            "smart_version": self.smart_version,
            "component_file_name": self.component_file_name,
            "smart_type": self.smart_type,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            smart_id=data.get("smart_id", ""),
            smart_version=data.get("smart_version", ""),
            component_file_name=data.get("component_file_name", ""),
            smart_type=data.get("smart_type", ""),
        )


@dataclass
class AstGlobals:
    project_info: ProjectInfo = None
    smart_component_info: Dict[str, SmartComponentInfo] = None
    component_info: Dict[str, ComponentInfo] = None
    process_info: Dict[str, ProcessInfo] = None
    atomic_info: Dict[str, AtomicInfo] = None

    def __init__(self):
        self.project_info = ProjectInfo()
        self.smart_component_info = {}
        self.process_info = {}
        self.component_info = {}
        self.atomic_info = {}

    def __json__(self):
        return {
            "project_info": self.project_info.__json__(),
            "smart_component_info": {k: v.__json__() for k, v in self.smart_component_info.items()},
            "component_info": {k: v.__json__() for k, v in self.component_info.items()},
            "process_info": {k: v.__json__() for k, v in self.process_info.items()},
            "atomic_info": {k: v.__json__() for k, v in self.atomic_info.items()},
        }

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()
        instance.project_info = ProjectInfo.from_dict(data.get("project_info", {}))
        instance.smart_component = {
            smart_component_key: SmartComponentInfo.from_dict(smart_component_data)
            for smart_component_key, smart_component_data in data.get("smart_component_info", {}).items()
        }
        instance.component_info = {
            component_id: ComponentInfo.from_dict(component_data)
            for component_id, component_data in data.get("component_info", {}).items()
        }
        instance.process_info = {
            process_id: ProcessInfo.from_dict(process_data)
            for process_id, process_data in data.get("process_info", {}).items()
        }
        instance.atomic_info = {
            atomic_key: AtomicInfo.from_dict(atomic_data)
            for atomic_key, atomic_data in data.get("atomic_info", {}).items()
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
