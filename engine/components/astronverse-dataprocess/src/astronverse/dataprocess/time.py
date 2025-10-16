"""时间处理工具集。"""

import copy
from datetime import UTC, datetime

from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, DynamicsItem, TimeFormatType
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.types import Date
from astronverse.dataprocess import TimeChangeType, TimestampUnitType, TimeUnitType, TimeZoneType
from dateutil.relativedelta import relativedelta


class TimeProcess:
    """时间相关原子能力集合。"""

    @staticmethod
    @atomicMg.atomic("TimeProcess", outputList=[atomicMg.param("current_time", types="Date")])
    def get_current_time(time_format: TimeFormatType = TimeFormatType.YMD_HMS):
        """获取当前时间对象并应用格式。"""
        res = Date()
        res.format = time_format
        return res

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
            atomicMg.param(
                "seconds",
                dynamics=[
                    DynamicsItem(
                        key="$this.seconds.show",
                        expression=f"return $this.change_type.value != '{TimeChangeType.MAINTAIN.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "minutes",
                dynamics=[
                    DynamicsItem(
                        key="$this.minutes.show",
                        expression=f"return $this.change_type.value != '{TimeChangeType.MAINTAIN.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "hours",
                dynamics=[
                    DynamicsItem(
                        key="$this.hours.show",
                        expression=f"return $this.change_type.value != '{TimeChangeType.MAINTAIN.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "days",
                dynamics=[
                    DynamicsItem(
                        key="$this.days.show",
                        expression=f"return $this.change_type.value != '{TimeChangeType.MAINTAIN.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "months",
                dynamics=[
                    DynamicsItem(
                        key="$this.months.show",
                        expression=f"return $this.change_type.value != '{TimeChangeType.MAINTAIN.value}'",
                    )
                ],
            ),
            atomicMg.param(
                "years",
                dynamics=[
                    DynamicsItem(
                        key="$this.years.show",
                        expression=f"return $this.change_type.value != '{TimeChangeType.MAINTAIN.value}'",
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("set_time", types="Date")],
    )
    def set_time(
        time: Date,
        change_type: TimeChangeType = TimeChangeType.MAINTAIN,
        seconds: int = 0,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        months: int = 0,
        years: int = 0,
    ):
        """对给定时间按增减方式进行偏移。"""
        res = copy.deepcopy(time)
        delta = relativedelta(
            years=years,
            months=months,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        if change_type == TimeChangeType.ADD:
            res.time += delta
        elif change_type == TimeChangeType.SUB:
            res.time -= delta
        return res

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            )
        ],
        outputList=[atomicMg.param("converted_timestamp", types="Int")],
    )
    def time_to_timestamp(time: Date, timestamp_unit: TimestampUnitType = TimestampUnitType.SECOND):
        """时间对象转时间戳。"""
        base = time.time.timestamp()
        if timestamp_unit == TimestampUnitType.SECOND:
            return int(base)
        if timestamp_unit == TimestampUnitType.MILLISECOND:
            return int(base * 1000)
        if timestamp_unit == TimestampUnitType.MICROSECOND:
            return int(base * 1_000_000)
        raise ValueError("不支持的时间戳单位")

    @staticmethod
    @atomicMg.atomic("TimeProcess", outputList=[atomicMg.param("converted_time", types="Date")])
    def timestamp_to_time(timestamp: int, time_zone: TimeZoneType = TimeZoneType.LOCAL):
        """时间戳转换为时间对象。支持秒/毫秒/微秒自动判定。"""
        ts_str = str(timestamp)
        length = len(ts_str)
        if length <= 10:
            timestamp_float = timestamp
        elif 10 < length <= 13:  # 毫秒
            timestamp_float = timestamp / 1000
        elif 13 < length <= 16:  # 微秒
            timestamp_float = timestamp / 1_000_000
        else:
            raise ValueError("时间戳长度不支持")
        time_obj = Date()
        if time_zone == TimeZoneType.UTC:
            time_obj.time = datetime.fromtimestamp(timestamp_float, tz=UTC)
        else:  # 本地
            time_obj.time = datetime.fromtimestamp(timestamp_float)
        return time_obj

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time_1",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
            atomicMg.param(
                "time_2",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
        ],
        outputList=[atomicMg.param("time_difference", types="Int")],
    )
    def get_time_difference(time_1: Date, time_2: Date, time_unit: TimeUnitType = TimeUnitType.SECOND):
        """计算两个时间的差值并按单位返回。"""
        diff_seconds = abs((time_2.time - time_1.time).total_seconds())
        if time_unit == TimeUnitType.SECOND:
            return int(diff_seconds)
        if time_unit == TimeUnitType.MINUTE:
            return int(diff_seconds / 60)
        if time_unit == TimeUnitType.HOUR:
            return int(diff_seconds / 3600)
        if time_unit == TimeUnitType.DAY:
            return int(diff_seconds / 86400)
        if time_unit in {TimeUnitType.MONTH, TimeUnitType.YEAR}:
            delta = relativedelta(time_2.time, time_1.time)
            if time_unit == TimeUnitType.MONTH:
                return delta.years * 12 + delta.months
            return delta.years
        raise ValueError("不支持的时间单位")

    @staticmethod
    @atomicMg.atomic(
        "TimeProcess",
        inputList=[
            atomicMg.param(
                "time",
                types="Date",
                formType=AtomicFormTypeMeta(AtomicFormType.INPUT_VARIABLE_PYTHON_DATETIME.value),
            ),
        ],
        outputList=[atomicMg.param("format_datetime", types="Str")],
    )
    def format_datetime(time: Date, format_type: TimeFormatType = TimeFormatType.YMD_HMS):
        """格式化时间为字符串。"""
        time.format = format_type
        return str(time)
