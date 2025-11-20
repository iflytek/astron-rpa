import json
import traceback

from astronverse.actionlib import ReportCode, ReportType, ReportCodeStatus, ReportFlow, ReportFlowStatus
from astronverse.actionlib.error import IgnoreException, ParamException, BaseException

from astronverse.executor import ExecuteStatus
from astronverse.executor.debug.bdb import CustomBdb
from astronverse.executor.error import python_base_error, MSG_DEBUG_INSTRUCTION_START_FORMAT, MSG_EXECUTION_ERROR


class Debug:
    def __init__(self, svc, args):
        self.svc = svc
        self.bdb = CustomBdb(
            project_dir=svc.conf.gen_core_path,
            ext_dir=svc.conf.gen_component_path,
            notify=self.notify,
            err_handler=python_base_error,
        )
        self.svc.main_process_id = args.process_id

        # 让 DebugSvc 负责加载数据
        svc.load_package_info()

        self.file_to_process = {}
        for i, v in self.svc.ast_globals.process_info.items():
            self.file_to_process[v.process_file_name] = v.process_id
            if not self.svc.main_process_id and v.process_name == svc.conf.main_process_name:
                self.svc.main_process_id = v.process_id

    def notify(self, typ, **kw):
        """打印演示"""

        if typ == "breakpoint" or typ == "step":
            file = kw.get("file")
            process_id = ""
            if file in self.file_to_process:
                process_id = self.file_to_process[file]

            line = kw.get("line")

            self.svc.report.info(
                ReportCode(
                    log_type=ReportType.Code,
                    process_id=process_id,
                    line=line,
                    msg_str=MSG_DEBUG_INSTRUCTION_START_FORMAT.format("{process}", line, "{atomic}"),
                    status=ReportCodeStatus.DEBUG_START,
                    debug_data={"is_break": True, "data": kw.get("merged_vars")},
                )
            )
        else:
            exc = kw.get("exc")
            if isinstance(exc, IgnoreException):
                error_str = exc.code.message
            elif isinstance(exc, ParamException):
                error_str = exc.code.message
            elif isinstance(exc, BaseException):
                error_str = exc.code.message
            else:
                error_str = str(exc)
            self.svc.report.error(
                ReportFlow(
                    log_type=ReportType.Flow,
                    status=ReportFlowStatus.TASK_ERROR,
                    result=ExecuteStatus.FAIL.value,
                    msg_str="{} {}".format(MSG_EXECUTION_ERROR, error_str),
                    error_traceback=traceback.format_exc(),
                )
            )

    def start(self, params: dict) -> dict:
        """执行代码"""

        # 环境准备, 下载依赖环境
        if self.svc.ast_globals.project_info.requirement:
            for k, v in self.svc.ast_globals.project_info.requirement.items():
                self.svc.package.download(
                    library=v.get("package_name"),
                    version=v.get("package_version", ""),
                    mirror=v.get("package_mirror", ""),
                )
        if self.svc.ast_globals.component_info:
            for c_id, c in self.svc.ast_globals.component_info.items():
                for k, v in c.requirement.items():
                    self.svc.package.download(
                        library=v.get("package_name"),
                        version=v.get("package_version", ""),
                        mirror=v.get("package_mirror", ""),
                    )

        # 断点设置
        if self.svc.debug_model:
            # 如果开启了debug,需要手动添加第一个默认第一个节点为断点
            self.set_breakpoint(self.svc.main_process_id, 1)

        for k, v in self.svc.ast_globals.process_info.items():
            for b in v.breakpoint:
                self.set_breakpoint(v.process_id, b)

        shared = {"_args": params}
        self.bdb.cmd_start(g_v=shared)
        return shared.get("_args", {})

    def cmd_continue(self):
        """继续执行"""
        return self.bdb.cmd_continue()

    def cmd_next(self):
        """单步执行"""
        return self.bdb.cmd_next()

    def set_breakpoint(self, filename, flow_line: int):
        """设置断点 - 支持多文件"""
        if self.svc.debug_model:
            info = self.svc.get_process_info(filename)
            if info:
                filename = info.process_file_name
            return self.bdb.set_breakpoint(filename=filename, flow_line=flow_line)

    def clear_breakpoint(self, filename: str, flow_line: int):
        """清除断点 - 支持多文件"""
        if self.svc.debug_model:
            info = self.svc.get_process_info(filename)
            if info:
                filename = info.process_file_name
            return self.bdb.clear_breakpoint(filename=filename, flow_line=flow_line)
