from astronverse.scheduler.apis.response import res_msg
from astronverse.scheduler.core.autostart.autostart import get_impl
from astronverse.scheduler.core.svc import Svc, get_svc
from astronverse.scheduler.error import AUTOSTART_NOT_SUPPORTED, BizException
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/auto_start/check")
def auto_start_check(svc: Svc = Depends(get_svc)):
    """
    自启动探测
    """
    impl = get_impl()
    return res_msg(msg="", data={"autostart": impl.check(svc.config.conf_file)})


@router.post("/auto_start/enable")
def auto_start_enable(svc: Svc = Depends(get_svc)):
    """
    自动开启
    """
    impl = get_impl()
    try:
        impl.enable(svc.config.conf_file)
    except BizException as e:
        return res_msg(msg="", data={"tips": e.code.message})
    return res_msg(msg="", data={"tips": "操作成功"})


@router.post("/auto_start/disable")
def auto_start_disable(svc: Svc = Depends(get_svc)):
    """
    自启动关闭
    """
    impl = get_impl()
    if not getattr(impl, "SUPPORTED", True):
        return res_msg(msg="", data={"tips": AUTOSTART_NOT_SUPPORTED.message})
    impl.disable(svc.config.conf_file)
    return res_msg(msg="", data={"tips": "操作成功"})
