"""
Linux 自启动：当前产品未实现；与 autostart_win / autostart_darwin 暴露相同函数签名，便于统一调度。
"""

from astronverse.scheduler.error import AUTOSTART_NOT_SUPPORTED, BizException

SUPPORTED = False


def check(conf_file: str) -> bool:
    return False


def enable(conf_file: str) -> None:
    raise BizException(AUTOSTART_NOT_SUPPORTED, AUTOSTART_NOT_SUPPORTED.message)


def disable(conf_file: str) -> None:
    pass
