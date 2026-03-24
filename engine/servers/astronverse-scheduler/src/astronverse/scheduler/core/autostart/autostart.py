"""
按平台选择自启动实现（darwin / win32 / linux）。
"""

import sys


def get_impl():
    if sys.platform == "darwin":
        from astronverse.scheduler.core.autostart import autostart_darwin
        return autostart_darwin
    elif sys.platform == "win32":
        from astronverse.scheduler.core.autostart import autostart_win
        return autostart_win
    else:
        from astronverse.scheduler.core.autostart import autostart_linux
        return autostart_linux
