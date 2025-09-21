import time

from fastapi import APIRouter, Depends

from ...apis.response import ResCode, res_msg
from ...core.svc import Svc, get_svc

router = APIRouter()


@router.post("/start")
def picker_start(svc: Svc = Depends(get_svc)):
    """
    启动拾取
    :return:
    """
    if svc.picker.app_picker.is_alive():
        return res_msg(msg="启动成功", data=None)

    svc.picker.highlighter.run()
    svc.picker.app_picker.run()
    svc.picker.cv_picker.run()
    svc.picker.set_start(True)

    tag = True
    for _ in range(10):
        time.sleep(0.5)
        if not svc.picker.app_picker.is_alive():
            tag = True
        else:
            tag = False
            break
    if tag:
        return res_msg(code=ResCode.ERR, msg="启动失败", data=None)
    return res_msg(msg="启动成功", data=None)


@router.post("/stop")
def picker_stop(svc: Svc = Depends(get_svc)):
    """
    关闭拾取
    :return:
    """
    try:
        svc.picker.set_start(False)
        svc.picker.cv_picker.kill()
        svc.picker.app_picker.kill()
        svc.picker.highlighter.kill()
    except Exception as e:
        pass
    return res_msg(msg="停止成功", data=None)
