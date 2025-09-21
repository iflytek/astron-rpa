import base64
import json
import subprocess
import sys
from enum import Enum

from setup.logger import logger


class EmitType(Enum):
    """
    定义向前端传递消息类型
    """

    SYNC = "sync"  # 阻塞消息，用于组件更新
    TIP = "tip"  # 后台提示信息，非阻塞


def string_to_base64(input_string):
    """
    支付串转base64
    """
    string_bytes = input_string.encode("utf-8")
    encoded_bytes = base64.b64encode(string_bytes)
    encoded_string = encoded_bytes.decode("utf-8")
    return encoded_string


def emit_to_front(emit_type: EmitType, msg=None):
    """
    向控制台输出信息，传递到 tauri main.rs标准输出中，触发给前端
    使用print暂时行不通，原因未知
    """
    data = {"type": emit_type.value, "msg": msg}
    logger.info("emit msg to front: {}".format(data))
    data = json.dumps(data)
    if sys.platform == "win32":
        subprocess.run(
            ["echo", "||emit|| {}".format(string_to_base64(data))],
            shell=True,
            check=True,
        )
    else:
        subprocess.run(
            ["echo", "||emit|| {}".format(string_to_base64(data))],
            shell=False,
            check=True,
        )
