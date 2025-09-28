import os
import sys


def platform_python_path(dir: str):
    if sys.platform == "win32":
        path = os.path.join(dir, r"python.exe")
    else:
        path = os.path.join(dir, "bin", "python3.7")
    return path


def platform_python_run_dir(dir: str):
    if sys.platform == "win32":
        path = os.path.dirname(dir)
    else:
        path = os.path.dirname(os.path.dirname(dir))
    return path


def platform_python_venv_path(v_path: str):
    if sys.platform == "win32":
        path = os.path.join(v_path, "venv", r"Scripts\python.exe")
    else:
        path = os.path.join(v_path, "venv", "bin", "python3.7")
    return path


def platform_shell(win_shell=True, linux_shell=False):
    if sys.platform == "win32":
        return win_shell
    else:
        return linux_shell
