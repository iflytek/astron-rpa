import json
import os
import time
from dataclasses import asdict
from enum import Enum
from queue import Queue

from astronverse.actionlib import (
    ReportCode,
    ReportCodeStatus,
    ReportFlow,
    ReportScript,
    ReportTip,
    ReportType,
    ReportUser,
)
from astronverse.actionlib.report import IReport


class Report(IReport):
    """运行日志处理程序"""

    def __init__(self, svc):
        self.svc = svc
        self.queue = Queue(maxsize=1000)
        local_file_path = os.path.join(self.svc.conf.log_path, "report", self.svc.conf.project_id)
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path)
        self.log_local_file = open(
            os.path.join(str(local_file_path), "{}.txt".format(self.svc.conf.exec_id)), "w", encoding="utf-8"
        )

        self.process = {}
        for i, v in self.svc.ast_globals.process_info.items():
            process_meta = {}
            if v.process_meta:
                for m in v.process_meta:
                    process_meta[m[0]] = m
            v.process_meta = process_meta
            self.process[v.process_id] = v

        self.last_process_id = ""
        self.last_process_name = ""
        self.last_meta = []
        self.last_line = 0

    def close(self):
        self.log_local_file.close()

    @staticmethod
    def __json__(obj):
        if isinstance(obj, Enum):
            return obj.value
        else:
            return obj.__dict__

    def __send__(self, filtered_dict):
        if self.queue and self.svc.conf.open_log_ws:
            ms = json.dumps(filtered_dict, ensure_ascii=False, default=self.__json__)
            self.queue.put(ms, block=True, timeout=None)

        if (
            self.log_local_file
            and (not self.log_local_file.closed)
            and filtered_dict["log_type"] != ReportType.Tip
            and filtered_dict.get("tag", None) != "tip"
        ):
            # Tip数据不写入到日志里面, tag等于Tag也不写入到日志
            message = json.dumps(
                {"event_time": int(time.time()), "data": filtered_dict}, ensure_ascii=False, default=self.__json__
            )
            self.log_local_file.write(f"{message}\n")
            self.log_local_file.flush()

    def __pre__(self, message):
        if (
            isinstance(message, ReportFlow)
            or isinstance(message, ReportCode)
            or isinstance(message, ReportUser)
            or isinstance(message, ReportTip)
        ):
            pass
        else:
            message = ReportScript(msg_str=str(message))

        if isinstance(message, ReportCode) or isinstance(message, ReportUser):
            process_id = message.process_id
            if process_id in self.process:
                process = self.process[process_id]
                process_name = process.process_name
                line = message.line
                if not message.process:
                    message.process = process_name
                    message.msg_str = message.msg_str.replace("{process}", process_name)
                if line in process.process_meta:
                    meta = process.process_meta[line]
                    atomic = meta[2]
                    key = meta[3]
                    line_id = meta[1]
                    if hasattr(message, "atomic") and not message.atomic:
                        message.atomic = atomic
                        message.msg_str = message.msg_str.replace("{atomic}", atomic)
                    if hasattr(message, "key") and not message.key:
                        message.key = key
                        message.msg_str = message.msg_str.replace("{key}", key)
                    if hasattr(message, "line_id") and not message.line_id:
                        message.line_id = line_id
                        message.msg_str = message.msg_str.replace("{line_id}", line_id)
                    self.last_meta = meta
                self.last_line = line
                self.last_process_name = process_name
                self.last_process_id = process_id
            else:
                # 没有就是组件
                if self.last_process_id:
                    message.process_id = self.last_process_id
                if self.last_process_name:
                    if not message.process:
                        message.process = self.last_process_name
                        message.msg_str = message.msg_str.replace("{process}", self.last_process_name)
                if self.last_line:
                    message.line = self.last_line
                if self.last_meta and len(self.last_meta) >= 3:
                    atomic = self.last_meta[2]
                    key = self.last_meta[3]
                    line_id = self.last_meta[1]
                    if hasattr(message, "atomic") and not message.atomic:
                        message.atomic = atomic
                        message.msg_str = message.msg_str.replace("{atomic}", atomic)
                    if hasattr(message, "key") and not message.key:
                        message.key = key
                        message.msg_str = message.msg_str.replace("{key}", key)
                    if hasattr(message, "line_id") and not message.line_id:
                        message.line_id = line_id
                        message.msg_str = message.msg_str.replace("{line_id}", line_id)
        return message

    def info(self, message):
        message = self.__pre__(message)

        filtered_dict = {k: v for k, v in asdict(message).items() if v is not None}

        if isinstance(message, ReportCode):
            if message.status == ReportCodeStatus.START:
                filtered_dict["tag"] = "tip"  # 特殊处理，只发送给右下角tip
        filtered_dict["log_level"] = "info"
        return self.__send__(filtered_dict)

    def warning(self, message):
        message = self.__pre__(message)

        filtered_dict = {k: v for k, v in asdict(message).items() if v is not None}
        filtered_dict["log_level"] = "warning"
        return self.__send__(filtered_dict)

    def error(self, message):
        message = self.__pre__(message)

        filtered_dict = {k: v for k, v in asdict(message).items() if v is not None}
        filtered_dict["log_level"] = "error"
        return self.__send__(filtered_dict)
