from enum import Enum


class ResCode(Enum):
    ERR = "5001"
    SUCCESS = "0000"


def res_msg(code: ResCode = ResCode.SUCCESS, msg: str = None, data: dict = None):
    return {"code": code.value, "msg": msg, "data": data}
