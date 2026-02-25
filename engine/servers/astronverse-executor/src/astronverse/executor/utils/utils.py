import ast
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


def kill_proc_tree(pid, including_parent=True, exclude_pids: list = None):
    """
    递归地杀死指定PID的进程及其所有子进程。
    """
    try:
        # 获取指定PID的进程
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return  # 如果进程不存在，则退出函数

    try:
        children = proc.children(recursive=True)
        for child in children:
            # 递归调用以杀死子进程的子进程
            kill_proc_tree(child, including_parent=True)
    except Exception as e:
        pass

    if including_parent:
        try:
            if exclude_pids:
                if proc.pid in exclude_pids:
                    return

            # 只会杀掉启动当期运行目录下的进程
            proc_cwd = proc.exe()
            if "astron-rpa" not in proc_cwd:
                return

            # 尝试杀死父进程
            proc.kill()
            proc.wait(5)  # 等待进程结束，防止僵尸进程
        except psutil.NoSuchProcess:
            pass


def str_to_list_if_possible(s):
    if not isinstance(s, str):
        return s  # 如果不是字符串，直接返回

    s = s.strip()  # 去除首尾空白
    if not (s.startswith("[") and s.endswith("]")):
        return s  # 明显不是列表字符串，直接返回

    try:
        # 安全地将字符串解析为 Python 字面量（支持列表、字典、元组、数字、字符串等）
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return result
        else:
            return s  # 虽然是 [] 形式，但解析后不是 list（如可能是 tuple）
    except (ValueError, SyntaxError):
        return s  # 解析失败，说明不是有效的列表字符串


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
