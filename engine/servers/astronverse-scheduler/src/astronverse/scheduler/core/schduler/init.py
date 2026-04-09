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


def darwin_check_accessibility() -> bool:
    """检测辅助功能权限"""
    if sys.platform != "darwin":
        return True
    try:
        from ApplicationServices import AXIsProcessTrusted
        return bool(AXIsProcessTrusted())
    except Exception:
        return False


def darwin_check_screen_recording() -> bool:
    """检测屏幕录制权限（macOS 11+，官方 API）"""
    if sys.platform != "darwin":
        return True
    try:
        import Quartz
        # CGRequestScreenCaptureAccess 会将应用加入系统设置列表，首次调用触发授权弹窗
        Quartz.CGRequestScreenCaptureAccess()
        return bool(Quartz.CGPreflightScreenCaptureAccess())
    except Exception:
        return False


def darwin_check_full_disk_access() -> bool:
    """检测完全磁盘访问权限（无官方 API，读受保护文件判断）"""
    if sys.platform != "darwin":
        return True
    # 优先读 TCC.db，几乎所有 Mac 都有
    protected = os.path.expanduser("~/Library/Application Support/com.apple.TCC/TCC.db")
    try:
        with open(protected, "rb"):
            return True
    except PermissionError:
        return False
    except FileNotFoundError:
        # 兜底：读 Safari History
        fallback = os.path.expanduser("~/Library/Safari/History.db")
        try:
            with open(fallback, "rb"):
                return True
        except PermissionError:
            return False
        except Exception:
            return True  # 无法判断，默认放行


def darwin_get_permissions() -> dict:
    """返回3个权限的状态"""
    return {
        "accessibility": darwin_check_accessibility(),
        "screen_recording": darwin_check_screen_recording(),
        "full_disk_access": darwin_check_full_disk_access(),
    }


def darwin_open_permission_settings(permission_type: str):
    """打开对应的系统设置页面"""
    url_map = {
        "accessibility":    "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        "screen_recording": "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture",
        "full_disk_access": "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles",
    }
    url = url_map.get(permission_type)
    if url:
        subprocess.run(["open", url])


def darwin_env_check():
    """macOS 环境检测"""
    if sys.platform != "darwin":
        return

    permissions = darwin_get_permissions()
    missing = [k for k, v in permissions.items() if not v]
    if missing:
        emit_to_front(EmitType.ALERT, msg={
            "type": "mac_permission",
            "permissions": permissions,
        })


def linux_env_check():
    """Linux 桌面环境检测"""
    if sys.platform == "win32":
        return
    elif sys.platform == "darwin":
        return

    pass
