import json
import os.path
import threading
import time
from typing import Optional

from astronverse.actionlib import ReportFlow, ReportFlowStatus, ReportTip, ReportType
from astronverse.actionlib.report import report
from astronverse.executor import AstGlobals, ExecuteStatus
from astronverse.executor.config import Config
from astronverse.executor.debug.debug import Debug
from astronverse.executor.debug.package import Package
from astronverse.executor.debug.recording import RecordingTool
from astronverse.executor.debug.report import Report
from astronverse.executor.debug.tools import LogTool
from astronverse.executor.error import *
from astronverse.executor.logger import logger
from astronverse.executor.utils.utils import kill_proc_tree


class DebugSvc:
    def __init__(self, conf, debug_model):
        # 全局类型
        self.conf: Config = conf

        # 启动数据
        self.ast_globals: AstGlobals = AstGlobals()
        self.load_package_info()
        self.main_process_id = None
        self.main_process_start_line = 1

        # 工具包
        self.report = Report(self)
        self.package = Package(self)
        report.set_code(self.report)
        self.log_tool = LogTool(self)
        self.recording_tool = RecordingTool(self)
        self.debug = None

        # 运行时
        self.debug_model = debug_model
        self.debug_handler: Optional[Debug] = None

        # 退出锁
        self.sys_exit_lock = threading.Lock()
        self.sys_exit_lock_end = False

    def load_package_info(self):
        """从 package.json 加载项目信息并转换为结构化对象"""
        package_json = os.path.join(self.conf.gen_core_path, "package.json")
        if os.path.exists(package_json):
            with open(package_json, encoding="utf-8") as f:
                package_info = json.load(f)
            self._load_ast_globals_from_dict(package_info)

    def _load_ast_globals_from_dict(self, data: dict):
        """将字典数据转换为结构化对象"""
        self.ast_globals = AstGlobals.from_dict(data)

    def get_project_info(self):
        return self.ast_globals.project_info

    def get_process_info(self, process_id):
        if process_id not in self.ast_globals.process_info:
            return None
        return self.ast_globals.process_info[process_id]

    def end(self, status: ExecuteStatus, data=None, reason=""):
        logger.info("end: {}.{}.{}".format(status, data, reason))
        with self.sys_exit_lock:
            if not self.sys_exit_lock_end:
                # 提示录制
                if self.recording_tool.config.get("open"):
                    url = os.path.join(os.path.abspath(self.conf.resource_dir), "ffmpeg.exe")
                    if not os.path.exists(url):
                        self.report.info(ReportTip(msg_str=MSG_NO_FFMPEG))
                    else:
                        self.report.info(ReportTip(msg_str=MSG_VIDEO_PROCESSING_WAIT))

                # 同步状态
                if status == ExecuteStatus.SUCCESS:
                    if data is None:
                        data = {}
                    self.report.info(
                        ReportFlow(
                            log_type=ReportType.Flow,
                            status=ReportFlowStatus.TASK_END,
                            result=status.value,
                            data=data,
                            msg_str=MSG_TASK_EXECUTION_END,
                        )
                    )
                elif status == ExecuteStatus.CANCEL:
                    self.report.info(
                        ReportFlow(
                            log_type=ReportType.Flow,
                            status=ReportFlowStatus.TASK_ERROR,
                            result=status.value,
                            msg_str=MSG_TASK_USER_CANCELLED,
                        )
                    )
                elif status == ExecuteStatus.FAIL:
                    if not reason:
                        reason = MSG_TASK_EXECUTION_ERROR
                    self.report.info(
                        ReportFlow(
                            log_type=ReportType.Flow,
                            result=status.value,
                            status=ReportFlowStatus.TASK_ERROR,
                            msg_str=reason,
                        )
                    )
                else:
                    raise NotImplementedError()

                # 结束log_tool
                if status in [ExecuteStatus.SUCCESS, ExecuteStatus.CANCEL, ExecuteStatus.FAIL]:
                    if self.log_tool:
                        self.log_tool.close()

                # 关闭日志
                if self.report:
                    self.report.close()

                # 结束录制
                if self.recording_tool.config.get("open"):
                    if status == ExecuteStatus.SUCCESS or status == ExecuteStatus.CANCEL:
                        self.recording_tool.close(True)
                    elif status == ExecuteStatus.FAIL:
                        self.recording_tool.close(False)

                # 结束退出
                self.sys_exit_lock_end = True
                time.sleep(1)
                kill_proc_tree(os.getpid(), True)
                # raise NotImplementedError()
