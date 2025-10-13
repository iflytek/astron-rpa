"""
封装对执行过程中的用户级别日志输出。提供一个原子能力 `Report.print`，
根据 `ReportLevelType` 分发到 info / warning / error 通道。
"""

from collections.abc import Callable
from typing import Any  # PEP 585: use built-in generics for dict

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, ReportType, ReportUser
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.report import report
from astronverse.report import ReportLevelType

__all__ = ["Report"]


class Report:  # pylint: disable=too-few-public-methods
    """Report 原子能力容器。

    目前仅提供一个静态方法 `print`，用于向统一报告模块发送一条用户级别日志。
    """

    @staticmethod
    @atomicMg.atomic(
        "Report",
        inputList=[
            atomicMg.param(
                key="report_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
            ),
        ],
    )
    def print(  # pylint: disable=redefined-builtin
        report_type: ReportLevelType = ReportLevelType.INFO,
        msg: Any = "",
        **kwargs: Any,
    ) -> None:
        """输出一条日志。

        参数:
            report_type: 日志级别，缺省为 INFO。
            msg: 任意可转换为字符串的消息对象。
            **kwargs: 执行框架注入的上下文字段，如 `__line__`, `__process_name__` 等。
        """
        msg = str(msg)

        line = int(kwargs.get("__line__", 0))
        line_id = kwargs.get("__line_id__", "")
        process_name = kwargs.get("__process_name__", "")
        process_id = kwargs.get("__process_id__", "")
        atomic_name = kwargs.get("__atomic_name__", "")

        user_obj = ReportUser(
            log_type=ReportType.User,
            process=process_name,
            process_id=process_id,
            atomic=atomic_name,
            line=line,
            line_id=line_id,
            msg_str=msg,
        )
        dispatcher: dict[ReportLevelType, Callable[[ReportUser], Any]] = {
            ReportLevelType.INFO: report.info,
            ReportLevelType.WARNING: report.warning,
            ReportLevelType.ERROR: report.error,
        }
        dispatch = dispatcher.get(report_type, report.info)
        dispatch(user_obj)
        # no explicit return needed (implicit None)
