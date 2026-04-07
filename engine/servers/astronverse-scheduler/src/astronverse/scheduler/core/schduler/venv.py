import os
import re
import shutil
import sys

from astronverse.scheduler.error import BizException, EXECUTOR_ERROR
from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.platform_utils import platform_python_venv_path
from astronverse.scheduler.utils.subprocess import SubPopen


def _validate_venv_config(venv_path):
    """
    检查虚拟环境的 pyvenv.cfg 是否正确配置了 include-system-site-packages
    """
    pyvenv_cfg = os.path.join(venv_path, "venv", "pyvenv.cfg")
    if not os.path.exists(pyvenv_cfg):
        return False
    with open(pyvenv_cfg, "r") as f:
        if "include-system-site-packages = true" not in f.read():
            return False
    return True


def _python_core_site_packages(python_core: str) -> str:
    python_run_dir = os.path.dirname(os.path.dirname(os.path.abspath(python_core)))
    return os.path.join(
        python_run_dir,
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
    )


def _ensure_python_core_pth(svc, v_path: str):
    """
    python_core 自身是一个 venv，嵌套创建项目 venv 时不会自动继承 python_core 的 site-packages。
    这里补一条 .pth，确保 astronverse.executor 等运行时模块可见。
    """
    site_packages = os.path.join(
        v_path,
        "venv",
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
    )
    if not os.path.exists(site_packages):
        return

    python_core_site = _python_core_site_packages(svc.config.python_core)
    if not os.path.exists(python_core_site):
        logger.warning("python_core site-packages not found: {}".format(python_core_site))
        return

    pth_file = os.path.join(site_packages, "astronverse_python_core.pth")
    pth_content = python_core_site + "\n"
    try:
        current = None
        if os.path.exists(pth_file):
            with open(pth_file, "r", encoding="utf-8") as f:
                current = f.read()
        if current != pth_content:
            with open(pth_file, "w", encoding="utf-8") as f:
                f.write(pth_content)
    except Exception as e:
        logger.warning("write python_core pth failed: {} {}".format(pth_file, e))

class VenvManager:
    @staticmethod
    def list_temp_venvs(svc):
        """
        枚举素有的虚拟环境
        """
        res = list()
        if not os.path.exists(svc.config.venv_base_dir):
            return res
        for temp_venv in os.listdir(svc.config.venv_base_dir):
            if re.search(r"^temp_venv\d+$", temp_venv):
                res.append(temp_venv)
        res.sort()
        return res

    @staticmethod
    def list_project_venvs(self):
        """
        获取所有的工程虚拟环境
        """
        project_venv_list = list()
        if not os.path.exists(self.svc.config.venv_base_dir):
            return project_venv_list
        for venv in os.listdir(self.svc.config.venv_base_dir):
            if re.search(r"^\d+$", venv):
                project_venv_list.append(os.path.join(self.svc.config.venv_base_dir, venv))
        return project_venv_list

    @staticmethod
    def remove_temp_venv(svc):
        if os.path.exists(svc.config.venv_base_dir):
            files = os.listdir(svc.config.venv_base_dir)
            for file_name in files:
                if file_name.startswith("."):
                    try:
                        # os.remove 无法删除.文件
                        if sys.platform == "win32":
                            os.system("rd /s/q {}".format(os.path.join(svc.config.venv_base_dir, file_name)))
                        else:
                            os.system("rm -rf {}".format(os.path.join(svc.config.venv_base_dir, file_name)))
                    except Exception as e:
                        pass
                if not os.path.exists(os.path.join(svc.config.venv_base_dir, file_name, "venv")):
                    try:
                        # os.remove 无法删除.文件
                        if sys.platform == "win32":
                            os.system("rd /s/q {}".format(os.path.join(svc.config.venv_base_dir, file_name)))
                        else:
                            os.system("rm -rf {}".format(os.path.join(svc.config.venv_base_dir, file_name)))
                    except Exception as e:
                        pass

    @staticmethod
    def create_new(svc, temp_venv_maxsize=1):
        """
        穿件一个新的工程运行的venv
        """

        # 1. 清空temp_venv保证是最新的
        VenvManager.remove_temp_venv(svc)
        temp_venv_list = VenvManager.list_temp_venvs(svc)
        if len(temp_venv_list) >= temp_venv_maxsize:
            return

        # 2. 虚拟环创建
        logger.info("create new venv...")

        # 2.1 名称获取
        temp_venv_num_start = 1
        if temp_venv_list:
            temp_venv_num_start = int(temp_venv_list[-1].split("temp_venv")[-1]) + 1
        env_dir_parent = os.path.join(
            svc.config.venv_base_dir,
            ".temp_venv{}".format(temp_venv_num_start),
        )
        env_dir_temp = os.path.join(env_dir_parent, "venv")

        # 2.2 创建虚拟环境
        cmd = [
            svc.config.python_base,
            "-m",
            "venv",
            "--system-site-packages",
            env_dir_temp,
        ]
        _, err = SubPopen(name="create_venv", cmd=cmd).run(log=True).logger_handler()
        if err:
            logger.error("create venv failed: {}".format(err))
            shutil.rmtree(env_dir_parent, ignore_errors=True)
            return

        # 2.2.1 校验 pyvenv.cfg 确保 include-system-site-packages = true
        if not _validate_venv_config(env_dir_parent):
            shutil.rmtree(env_dir_parent, ignore_errors=True)
            return

        # 2.3 .temp_venv重命名成temp_venv
        os.rename(
            env_dir_parent,
            os.path.join(
                svc.config.venv_base_dir,
                "temp_venv{}".format(temp_venv_num_start),
            ),
        )


def create_project_venv(svc, project_id: str):
    """
    创建一个工程的虚拟环境
    """
    if svc.is_venv:
        return svc.config.python_base

    v_path = os.path.join(svc.config.venv_base_dir, project_id)
    if not os.path.exists(v_path):
        temp_envs = VenvManager.list_temp_venvs(svc)
        if not temp_envs:
            raise BizException(EXECUTOR_ERROR.format("虚拟环境运行时为空"), "empty venv runtime...")
        temp_v = temp_envs[0]
        os.rename(os.path.join(svc.config.venv_base_dir, temp_v), v_path)

    if not _validate_venv_config(v_path):
        shutil.rmtree(v_path, ignore_errors=True)
        raise BizException(EXECUTOR_ERROR.format("虚拟环境配置错误"), "invalid venv config...")
    _ensure_python_core_pth(svc, v_path)
    return platform_python_venv_path(v_path)


def get_project_venv(svc, project_id: str):
    if svc.is_venv:
        return svc.config.python_base

    v_path = os.path.join(svc.config.venv_base_dir, project_id)
    return platform_python_venv_path(v_path)
