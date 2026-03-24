import os
import subprocess
import sys

from astronverse.scheduler.utils.utils import EmitType, emit_to_front


def win_env_check(svc):
    """win 环境检测"""
    if sys.platform != "win32":
        return

    try:
        import win32api
        import win32gui
    except Exception as e:
        emit_to_front(EmitType.ALERT, msg={"msg": "系统依赖缺失，执行修复中...", "type": "normal"})
        resource_dir = os.path.dirname(svc.config.conf_file)
        try:
            vc_redist_exe = os.path.join(resource_dir, "VC_redist.x64.exe")
            if os.path.exists(vc_redist_exe):
                subprocess.run([vc_redist_exe, "-quiet"], check=True)
        except Exception as e:
            pass


def darwin_env_check():
    """macOS 环境检测"""
    if sys.platform != "darwin":
        return

    pass


def linux_env_check():
    """Linux 桌面环境检测"""
    if sys.platform == "win32":
        return
    elif sys.platform == "darwin":
        return

    pass
