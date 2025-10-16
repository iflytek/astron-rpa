from project import *
from astronverse.actionlib.types import *
import astronverse.report.report


def main(**kwargs):
    pass
    
    astronverse.report.report.Report().print(report_type="info", msg="123", __info__="[1, 'bh748264431104069', '日志打印', {'report_type': '日志类型', 'msg': '日志内容'}]")
    astronverse.report.report.Report().print(report_type="info", msg=1/0, __info__="[2, 'bh748576963711045', '日志打印', {'report_type': '日志类型', 'msg': '日志内容'}]")