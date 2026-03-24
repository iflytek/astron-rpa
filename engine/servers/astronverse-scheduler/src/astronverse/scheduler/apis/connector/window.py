import os
import sys

from astronverse.scheduler.apis.response import res_msg
from astronverse.scheduler.core.svc import Svc, get_svc
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/auto_start/check")
def auto_start_check():
    """
    自启动探测
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"autostart": False})

    from astronverse.scheduler.utils.window import AutoStart

    return res_msg(msg="", data={"autostart": AutoStart.check()})


@router.post("/auto_start/enable")
def auto_start_enable(svc: Svc = Depends(get_svc)):
    """
    自动开启
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"tips": "操作异常，linux暂不支持自启动"})

    from astronverse.scheduler.utils.window import AutoStart

    exe_path = os.path.join(os.path.dirname(os.path.dirname(svc.config.conf_file)), "astron-rpa.exe").lower()
    AutoStart.enable(exe_path)
    return res_msg(msg="", data={"tips": "操作成功"})


@router.post("/auto_start/disable")
def auto_start_disable():
    """
    自启动关闭
    """
    if sys.platform != "win32":
        return res_msg(msg="", data={"tips": "操作异常，linux暂不支持自启动"})

    from astronverse.scheduler.utils.window import AutoStart

    AutoStart.disable()
    return res_msg(msg="", data={"tips": "操作成功"})
