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
        self.log_local_file = open(os.path.join(str(local_file_path), "{}.txt".format(self.svc.conf.exec_id)), "w", encoding="utf-8")

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

    def info(self, message):
        if (
            isinstance(message, ReportFlow)
            or isinstance(message, ReportCode)
            or isinstance(message, ReportUser)
            or isinstance(message, ReportTip)
        ):
            pass
        else:
            message = ReportScript(msg_str=str(message))

        filtered_dict = {k: v for k, v in asdict(message).items() if v is not None}

        if isinstance(message, ReportCode):
            if message.status == ReportCodeStatus.START:
                filtered_dict["tag"] = "tip"  # 特殊处理，只发送给右下角tip
        filtered_dict["log_level"] = "info"
        return self.__send__(filtered_dict)

    def warning(self, message):
        if (
            isinstance(message, ReportFlow)
            or isinstance(message, ReportCode)
            or isinstance(message, ReportUser)
            or isinstance(message, ReportTip)
        ):
            pass
        else:
            message = ReportScript(msg_str=str(message))

        filtered_dict = {k: v for k, v in asdict(message).items() if v is not None}
        filtered_dict["log_level"] = "warning"
        return self.__send__(filtered_dict)

    def error(self, message):
        if (
            isinstance(message, ReportFlow)
            or isinstance(message, ReportCode)
            or isinstance(message, ReportUser)
            or isinstance(message, ReportTip)
        ):
            pass
        else:
            message = ReportScript(msg_str=str(message))

        filtered_dict = {k: v for k, v in asdict(message).items() if v is not None}
        filtered_dict["log_level"] = "error"
        return self.__send__(filtered_dict)



