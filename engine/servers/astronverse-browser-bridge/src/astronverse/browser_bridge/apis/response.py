import traceback
from dataclasses import dataclass
from typing import Any

from astronverse.browser_bridge.error import CODE_INNER, CODE_OK, BaseException
from astronverse.browser_bridge.logger import logger
from starlette.requests import Request
from starlette.responses import JSONResponse


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


async def http_base_exception(request: Request, exc: BaseException):
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
