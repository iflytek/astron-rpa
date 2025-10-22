from enum import Enum


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
