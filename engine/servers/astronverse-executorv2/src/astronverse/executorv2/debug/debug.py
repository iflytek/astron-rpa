import json
from astronverse.actionlib import ReportCode, ReportType, ReportCodeStatus
from astronverse.executorv2.debug.bdb import CustomBdb
from astronverse.executorv2.error import python_base_error


class Debug:

    def __init__(self, svc):
        self.svc = svc
        self.bdb = CustomBdb(project_dir=svc.conf.gen_core_path, notify=self.notify, err_handler=python_base_error)

        # 让 DebugSvc 负责加载数据
        svc.load_package_info()

        self.file_to_process = {}
        for i, v in self.svc.ast_globals.process_info.items():
            self.file_to_process[v.process_file_name] = v

    def notify(self, typ, **kw):
        """打印演示"""

        if typ == "breakpoint" or typ == "step":
            print(json.dumps(kw.get("merged_vars"), ensure_ascii=False))

            file = kw.get("file")
            process_id = ""
            process = ""
            if file in self.file_to_process:
                process_id = self.file_to_process[file].process_id
                process = self.file_to_process[file].process_name

            self.svc.report.info(ReportCode(
                log_type=ReportType.Code,
                process=process,
                process_id=process_id,
                atomic="",
                key="",
                line_id="",
                line=kw.get("py_line"),
                status=ReportCodeStatus.DEBUG_START,
                debug_data={
                    "is_break": True,
                    "data": kw.get("merged_vars")
                },
            ))

            print(json.dumps({'type': typ, "file": kw.get("file"), "line": kw.get("line"), "py_line": kw.get("py_line")}, ensure_ascii=False))
        else:
            raise kw.get("exc")

    def start(self):
        """执行代码"""

        # 环境准备
        if self.svc.ast_globals.project_info.requirement:
            for k, v in self.svc.ast_globals.project_info.requirement.items():
                self.svc.package.download(
                    library=v.get("package_name"),
                    version=v.get("package_version", ""),
                    mirror=v.get("package_mirror", "")
                )

        # 断点设置
        if self.svc.debug_model:
            # 如果开启了debug,需要手动添加第一个默认第一个节点为断点
            self.set_breakpoint(self.svc.ast_globals.project_info.main_process_id, 1)

        for k, v in self.svc.ast_globals.process_info.items():
            for b in v.breakpoint:
                self.set_breakpoint(v.process_id, b)

        self.bdb.cmd_start()

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
