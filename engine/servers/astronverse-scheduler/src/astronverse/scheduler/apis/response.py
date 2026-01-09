from enum import Enum


class ResCode(Enum):
    ERR = "5001"
    SUCCESS = "0000"


def res_msg(code: ResCode = ResCode.SUCCESS, msg: str = None, data: dict = None):
    return {"code": code.value, "msg": msg, "data": data}


def exec_res_msg(code: ResCode = ResCode.SUCCESS, msg: str = None, data: dict = None, video_path: str = None):
    if video_path:
        return {"code": code.value, "msg": msg, "data": data, "video_path": video_path}
    else:
        return {"code": code.value, "msg": msg, "data": data}
