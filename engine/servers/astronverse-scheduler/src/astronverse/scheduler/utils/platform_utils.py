import os
import platform
import sys


def platform_python_path(dir: str):
    if sys.platform == "win32":
        return os.path.join(dir, r"python.exe")
    elif sys.platform == "darwin":
        return os.path.join(dir, "bin", "python3")
    else:
        return os.path.join(dir, "bin", "python3")


def platform_python_run_dir(dir: str):
    if sys.platform == "win32":
        return os.path.dirname(dir)
    elif sys.platform == "darwin":
        return os.path.dirname(os.path.dirname(dir))
    else:
        return os.path.dirname(os.path.dirname(dir))


def platform_python_venv_path(v_path: str):
    if sys.platform == "win32":
        return os.path.join(v_path, "venv", "Scripts", "python.exe")
    elif sys.platform == "darwin":
        return os.path.join(v_path, "venv", "bin", "python3")
    else:
        return os.path.join(v_path, "venv", "bin", "python3")


def platform_python_venv_run_dir(dir: str):
    if sys.platform == "win32":
        return os.path.dirname(os.path.dirname(os.path.dirname(dir)))
    elif sys.platform == "darwin":
        return os.path.dirname(os.path.dirname(os.path.dirname(dir)))
    else:
        return os.path.dirname(os.path.dirname(os.path.dirname(dir)))


def get_astron_router_path(resource_dir: str) -> str:
    """resource_dir 下按平台子目录放置 astron_router（与仓库 resources/ 布局一致）。"""
    base = os.path.abspath(resource_dir)
    if sys.platform == "win32":
        return os.path.join(base, "win-x64", "astron_router.exe")
    elif sys.platform == "darwin":
        return os.path.join(base, "mac", "astron_router")
    else:
        machine = platform.machine().lower()
        if machine in ("aarch64", "arm64"):
            sub = "linux-arm64"
        else:
            sub = "linux-amd64"
        return os.path.join(base, sub, "astron_router")
