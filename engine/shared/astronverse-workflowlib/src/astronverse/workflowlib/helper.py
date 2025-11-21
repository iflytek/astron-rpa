"""为了兼容, 可以删除"""

from astronverse.workflowlib.report import print
from astronverse.actionlib.report import IReport, report

logger: IReport = report

print = print


class Helper:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def params(self):
        return self.kwargs
