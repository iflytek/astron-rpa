import os
import re
import sys

from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.platform_utils import platform_python_venv_path
from astronverse.scheduler.utils.subprocess import SubPopen


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
            env_dir_temp,
            "--system-site-packages",
        ]
        _, err = SubPopen(name="create_venv", cmd=cmd).run(log=True).logger_handler()
        if err:
            logger.error("create venv failed: {}".format(err))

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
            raise Exception("empty venv runtime...")
        temp_v = temp_envs[0]
        os.rename(os.path.join(svc.config.venv_base_dir, temp_v), v_path)
    return platform_python_venv_path(v_path)


def get_project_venv(svc, project_id: str):
    if svc.is_venv:
        return svc.config.python_base

    v_path = os.path.join(svc.config.venv_base_dir, project_id)
    return platform_python_venv_path(v_path)
