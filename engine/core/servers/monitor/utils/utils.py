import os

import psutil


def kill_proc_tree(
    proc: psutil.Process = None,
    including_parent: bool = True,
    exclude_pids: list = None,
):
    """
    递归地杀死指定PID的进程及其所有子进程。
    """
    work_dir = os.getcwd()
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
            if work_dir not in proc_cwd:
                return
            # 尝试杀死父进程
            proc.kill()
            proc.wait(5)  # 等待进程结束，防止僵尸进程
        except psutil.NoSuchProcess:
            pass
