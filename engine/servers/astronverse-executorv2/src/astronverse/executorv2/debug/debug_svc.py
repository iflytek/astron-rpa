import json
import os.path
from typing import Optional
from astronverse.actionlib import ReportFlow, ReportType, ReportFlowStatus
from astronverse.actionlib.report import report
from astronverse.executorv2 import ExecuteStatus, AstGlobals
from astronverse.executorv2.config import Config
from astronverse.executorv2.debug.debug import Debug
from astronverse.executorv2.debug.package import Package
from astronverse.executorv2.debug.report import Report
from astronverse.executorv2.debug.tools import LogTool
from astronverse.executorv2.error import MSG_TASK_EXECUTION_END, MSG_TASK_EXECUTION_ERROR, MSG_TASK_USER_CANCELLED
from astronverse.executorv2.logger import logger


class DebugSvc:

    def __init__(self, conf, debug_model):
        # 全局类型
        self.conf: Config = conf



        # 工具类
        self.ast_globals: AstGlobals = AstGlobals()
        self.load_package_info()
        self.report = Report(self)
        self.package = Package(self)
        report.set_code(self.report)
        self.log_tool = LogTool(self)

        # 运行时
        self.debug_model = debug_model
        self.debug_handler: Optional[Debug] = None

    def load_package_info(self):
        """从 package.json 加载项目信息并转换为结构化对象"""
        package_json = os.path.join(self.conf.gen_core_path, "package.json")
        if os.path.exists(package_json):
            with open(package_json, "r", encoding="utf-8") as f:
                package_info = json.load(f)
            self._load_ast_globals_from_dict(package_info)

    def _load_ast_globals_from_dict(self, data: dict):
        """将字典数据转换为结构化对象"""
        self.ast_globals = AstGlobals.from_dict(data)

    def get_process_info(self, process_id):
        if process_id not in self.ast_globals.process_info:
            return None
        return self.ast_globals.process_info[process_id]

    def end(self, status: ExecuteStatus, reason, traceback):
        logger.info("end: {}.{}.{}".format(status, reason, traceback))
        if status == ExecuteStatus.SUCCESS:
            self.report.info(ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.TASK_END, msg_str=MSG_TASK_EXECUTION_END))
            return
        elif status == ExecuteStatus.CANCEL:
            self.report.info(ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.TASK_ERROR, msg_str=MSG_TASK_USER_CANCELLED))
        elif status == ExecuteStatus.FAIL:
            self.report.info(ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.TASK_ERROR, msg_str=MSG_TASK_EXECUTION_ERROR))
        raise Exception("结束")
