import os
import subprocess
from astronverse.executorv2.logger import logger


def exec_run(exec_args: list, ignore_error: bool = False, timeout=-1):
    """启动子进程并处理错误日志"""

    proc = None
    try:
        logger.debug("准备执行命令: %s", exec_args)

        current_env = os.environ.copy()
        current_env["no_proxy"] = "True"
        proc = subprocess.Popen(exec_args, shell=False, env=current_env)
        if timeout > 0:
            stdout_data, stderr_data = proc.communicate(timeout=timeout)
        else:
            stdout_data, stderr_data = proc.communicate()

        if stderr_data and not ignore_error:
            error_msg = f"命令执行失败!\nSTDERR:\n{stderr_data.decode('utf-8', errors='replace')}"
            raise Exception(error_msg)
    except Exception as e:
        detail_msg = (
            f"[PID={proc.pid if proc else 'N/A'}] 进程异常终止! "
            f"返回码={proc.returncode if proc else 'N/A'}\n"
            f"错误详情:\n{str(e)}"
        )
        logger.error(detail_msg)
        raise Exception(detail_msg) from e