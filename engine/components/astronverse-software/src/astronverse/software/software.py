import os
import platform
import subprocess
import sys
import time
import warnings
import shlex
import psutil
from astronverse.actionlib import AtomicFormType, AtomicFormTypeMeta, AtomicLevel
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.logger import logger
from astronverse.software.core import ISoftwareCore
from astronverse.software.error import (
    INVALID_APP_PATH_ERROR_CODE,
)
from astronverse.software.error import (
    BaseException as SoftwareBaseException,
)

import locale

if sys.platform == "win32":
    from astronverse.software.core_win import SoftwareCore
elif platform.system() == "Linux":
    from astronverse.software.core_unix import SoftwareCore
else:
    raise NotImplementedError(f"Your platform ({platform.system()}) is not supported by (clipboard).")

SoftwareCore: ISoftwareCore = SoftwareCore()
system_encoding = locale.getpreferredencoding()


class Software:
    @staticmethod
    @atomicMg.atomic(
        "Software",
        inputList=[
            atomicMg.param(
                "app_absolute_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": []},
                ),
            ),
            atomicMg.param("app_arguments", required=False, level=AtomicLevel.ADVANCED),
        ],
        outputList=[atomicMg.param("software_open", types="Str")],
    )
    def open(app_absolute_path: str = "", app_arguments: str = "") -> str:
        """
        打开软件
        :param app_absolute_path: 地址
        :param app_arguments: 参数
        :return:
        """

        if not os.path.exists(app_absolute_path):
            raise SoftwareBaseException(
                INVALID_APP_PATH_ERROR_CODE.format(app_absolute_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )

        warnings.filterwarnings("ignore", category=ResourceWarning)
        process = subprocess.Popen(
            [app_absolute_path] + shlex.split(app_arguments),
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        while not process.pid:
            time.sleep(0.3)
        return app_absolute_path

    @staticmethod
    @atomicMg.atomic(
        "Software",
        inputList=[
            atomicMg.param(
                "app_absolute_path",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": []},
                ),
            )
        ],
    )
    def close(app_absolute_path: str):
        """
        关闭软件
        :param app_absolute_path: 地址
        :return:
        """

        if not os.path.exists(app_absolute_path):
            raise SoftwareBaseException(
                INVALID_APP_PATH_ERROR_CODE.format(app_absolute_path),
                "填写的应用程序路径有误，请输入正确的路径！",
            )

        exe_name = os.path.split(app_absolute_path)[1]
        try:
            if sys.platform == "win32":
                # 特殊处理
                if exe_name == "ThunderStart.exe":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "Thunder.exe"],
                        check=False,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
                subprocess.run(
                    ["taskkill", "/F", "/IM", exe_name],
                    check=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.run(
                    ["pkill", exe_name],
                    check=False,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except (subprocess.SubprocessError, OSError) as error:
            logger.error(f"error: Software close {error}")
            return

    @staticmethod
    def exists(app_name: str = "", parent_name: str = "") -> bool:
        """
        exists 软件是否存在
        :param app_name: 软件名称
        :param parent_name: 软件的父级名称
        :return:
        """

        return Software.pid(app_name, parent_name) >= 0

    @staticmethod
    def pid(app_name: str = "", parent_name: str = "") -> int:
        """
        pid 获取正在执行的软件pid
        :param app_name: 软件名称
        :param parent_name: 软件的父级名称
        :return:
        """
        for process in psutil.process_iter():
            try:
                if process.name() != app_name:
                    continue

                if not parent_name:
                    return process.pid

                for parent in process.parents():
                    if parent.name() == parent_name:
                        return process.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return -1

    @staticmethod
    def get_app_path(app_name: str = "") -> str:
        """
        获取软件地址
        """
        return SoftwareCore.get_app_path(app_name)

    @staticmethod
    @atomicMg.atomic("Software", outputList=[atomicMg.param("exec_cmd", types="Dict")])
    def cmd(cmd: str) -> dict:
        with subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding=system_encoding,
            errors="replace",
        ) as process:
            stdout, stderr = process.communicate()
            return {
                "status": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
            }
