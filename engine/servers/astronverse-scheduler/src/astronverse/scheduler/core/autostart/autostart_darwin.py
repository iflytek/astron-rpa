"""
macOS 自启动：用户级 LaunchAgent（~/Library/LaunchAgents）。
与 Windows 侧约定一致：配置文件上级目录下可找到可执行文件 astron-rpa，或 *.app/Contents/MacOS/*。
"""

from __future__ import annotations

import os
import plistlib
import subprocess

from astronverse.scheduler.error import AUTOSTART_EXE_NOT_FOUND, BizException

LAUNCH_AGENT_LABEL = "com.astronverse.scheduler.autostart"

SUPPORTED = True


def _launch_agents_dir() -> str:
    return os.path.expanduser("~/Library/LaunchAgents")


def plist_path() -> str:
    return os.path.join(_launch_agents_dir(), f"{LAUNCH_AGENT_LABEL}.plist")


def resolve_mac_binary(conf_file: str) -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(conf_file)))
    direct = os.path.join(base, "astron-rpa")
    if os.path.isfile(direct) and os.access(direct, os.X_OK):
        return direct
    if not os.path.isdir(base):
        return ""
    for name in sorted(os.listdir(base)):
        if not name.endswith(".app"):
            continue
        macos_dir = os.path.join(base, name, "Contents", "MacOS")
        if not os.path.isdir(macos_dir):
            continue
        for f in sorted(os.listdir(macos_dir)):
            fp = os.path.join(macos_dir, f)
            if os.path.isfile(fp) and os.access(fp, os.X_OK):
                return fp
    return ""


def check(conf_file: str | None = None) -> bool:
    """plist 存在且 ProgramArguments 指向可执行文件。conf_file 预留与 Win/Linux 统一签名。"""
    p = plist_path()
    if not os.path.isfile(p):
        return False
    try:
        with open(p, "rb") as f:
            data = plistlib.load(f)
        args = data.get("ProgramArguments") or []
        if not args:
            return False
        exe = args[0]
        return bool(exe) and os.path.isfile(exe) and os.access(exe, os.X_OK)
    except Exception:
        return False


def _launchctl_load(path: str) -> None:
    subprocess.run(
        ["launchctl", "unload", path],
        capture_output=True,
        text=True,
    )
    r = subprocess.run(
        ["launchctl", "load", path],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        return
    uid = str(os.getuid())
    subprocess.run(
        ["launchctl", "bootstrap", f"gui/{uid}", path],
        capture_output=True,
        text=True,
    )


def _launchctl_unload(path: str) -> None:
    subprocess.run(
        ["launchctl", "unload", path],
        capture_output=True,
        text=True,
    )
    uid = str(os.getuid())
    subprocess.run(
        ["launchctl", "bootout", f"gui/{uid}", path],
        capture_output=True,
        text=True,
    )


def enable(conf_file: str) -> None:
    exe = resolve_mac_binary(conf_file)
    if not exe:
        raise BizException(AUTOSTART_EXE_NOT_FOUND, AUTOSTART_EXE_NOT_FOUND.message)
    os.makedirs(_launch_agents_dir(), exist_ok=True)
    payload = {
        "Label": LAUNCH_AGENT_LABEL,
        "ProgramArguments": [exe],
        "RunAtLoad": True,
    }
    path = plist_path()
    with open(path, "wb") as f:
        plistlib.dump(payload, f)
    _launchctl_load(path)


def disable(conf_file: str | None = None) -> None:
    path = plist_path()
    if not os.path.isfile(path):
        return
    _launchctl_unload(path)
    try:
        os.remove(path)
    except OSError:
        pass
