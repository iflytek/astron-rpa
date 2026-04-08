from fastapi import APIRouter
from pydantic import BaseModel
from astronverse.scheduler.apis.response import res_msg
from astronverse.scheduler.core.schduler.init import (
    darwin_get_permissions,
    darwin_open_permission_settings,
)

router = APIRouter()


@router.get("/status")
def mac_permission_status():
    """查询 macOS 3 个权限状态"""
    return res_msg(msg="", data=darwin_get_permissions())


class OpenSettingsReq(BaseModel):
    type: str  # accessibility | screen_recording | full_disk_access


@router.post("/open")
def mac_permission_open(req: OpenSettingsReq):
    """打开对应的系统设置页面"""
    darwin_open_permission_settings(req.type)
    return res_msg(msg="", data={})
