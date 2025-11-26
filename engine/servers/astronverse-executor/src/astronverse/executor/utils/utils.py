import os
import subprocess
import sys

import psutil
from astronverse.executor.logger import logger


def platform_python_venv_run_dir(dir: str):
    if sys.platform == "win32":
        path = os.path.dirname(os.path.dirname(os.path.dirname(dir)))
    else:
        path = os.path.dirname(os.path.dirname(os.path.dirname(dir)))
    return path


def kill_proc_tree(pid, including_parent=True):
    """
    递归地杀死指定PID的进程及其所有子进程。
    :param pid: 要杀死的进程的PID。
    :param including_parent: 是否包括父进程本身。
    """

    work_dir = os.getcwd()
    try:
        # 获取指定PID的进程
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return  # 如果进程不存在，则退出函数

    try:
        # 获取所有子进程
        children = proc.children(recursive=True)
        for child in children:
            kill_proc_tree(child.pid, including_parent=True)  # 递归调用以杀死子进程的子进程
    except Exception as e:
        pass

    if including_parent:
        try:
            # 只会杀掉当前运行目录下的进程
            proc_cwd = proc.exe()
            if work_dir not in proc_cwd:
                return
            # 尝试杀死父进程
            proc.kill()
            proc.wait(5)  # 等待进程结束，防止僵尸进程
        except psutil.NoSuchProcess:
            pass


def exec_run(exec_args: list, ignore_error: bool = False, timeout=-1):
    """启动子进程并处理错误日志"""

    logger.debug("准备执行命令: %s", exec_args)
    proc = subprocess.Popen(
        exec_args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "no_proxy": "*"},
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    try:
        proc.wait(timeout=timeout if timeout > 0 else None)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise TimeoutError("error: timeout") from None

    if proc.returncode != 0 and not ignore_error:
        raise BaseException(f"error: return code({proc.returncode})")
