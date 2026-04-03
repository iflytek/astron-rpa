from enum import Enum
import traceback
from dataclasses import dataclass
from typing import Any
from astronverse.scheduler.error import *
from starlette.requests import Request
from starlette.responses import JSONResponse

from astronverse.scheduler.logger import logger


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


@dataclass
class CustomResponse:
    """自定义的返回值"""

    code: str
    msg: str
    data: Any

    @classmethod
    def tojson(cls, data: Any = None):
        return JSONResponse(cls(CODE_OK.code.value, CODE_OK.message, data=data).__dict__, status_code=CODE_OK.httpcode)


async def http_exception(request: Request, exc: Exception):
    """http通用错误处理"""

    logger.error("http_exception: error:{}".format(exc))
    logger.error("http_exception: traceback:{}".format(traceback.format_exc()))
    return JSONResponse(
        CustomResponse(CODE_INNER.code.value, CODE_INNER.message, {}).__dict__, status_code=CODE_INNER.httpcode
    )


async def http_base_exception(request: Request, exc: BizException):
    """http特殊错误处理"""

    logger.error(
        "http_base_exception: code:{} message:{} httpcode:{} error:{}".format(
            exc.code.code, exc.code.message, exc.code.httpcode, exc.message
        )
    )
    logger.error("http_base_exception: traceback:{}".format(traceback.format_exc()))
    return JSONResponse(
        CustomResponse(exc.code.code.value, exc.code.message, {}).__dict__, status_code=exc.code.httpcode
    )
