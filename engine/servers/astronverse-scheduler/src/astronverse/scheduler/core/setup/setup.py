import locale
import os
import subprocess
import sys
import time

import psutil
from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.utils import exe_path_matches_astron_install, kill_proc_tree

system_encoding = locale.getpreferredencoding()

# 与 RPA 常见子进程一致：Windows 用完整映像名；POSIX 用去掉 .exe 的前缀做进程名预筛。
_TASK_IMAGE_NAMES = ("python.exe", "astron_router.exe", "ConsoleApp1.exe", "winvnc.exe")
_POSIX_NAME_PREFIXES = tuple(img.replace(".exe", "").lower() for img in _TASK_IMAGE_NAMES)


class Process:
    """进程管理类"""

    @staticmethod
    def kill_all_zombie():
        """杀死所有的僵尸进程"""
        zombie_processes = Process.get_python_proc_in_current_dir()
        for z_p in zombie_processes:
            kill_proc_tree(z_p)

    @staticmethod
    def _get_python_proc_in_current_dir_win():
        """
        Windows 专用：查找「可能是本机 Astron 相关」的进程，供 kill_all_zombie 逐个杀进程树。

        分三步：
        1) 用 tasklist 按固定映像名（python / 路由 / 拾取 / vnc）收集候选 PID，避免枚举全系统进程。
        2) 排除当前调度器进程及其所有父进程，防止误杀自己。
        3) 对剩余 PID 用 exe 路径过滤：必须落在 exe_path_matches_astron_install 认定的安装目录内，
           避免误杀其他目录下的 python.exe / 同名程序。
        """
        # 第一步：按映像名拉候选 PID（与 RPA 常见子进程名一致）
        all_process_ids = []
        for process_name in _TASK_IMAGE_NAMES:
            output = subprocess.check_output(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV"],
                encoding=system_encoding,
                errors="replace",
            )
            for line in output.splitlines()[1:]:
                parts = line.split(",")
                if len(parts) > 1:
                    pid = parts[1].strip('"')
                    all_process_ids.append(int(pid))

        if not all_process_ids:
            return []

        # 第二步：当前进程链上的 PID 都不杀（scheduler 自身与 Electron 等父进程）
        self_proc_id_list = []
        try:
            proc = psutil.Process(os.getpid())
            while proc:
                self_proc_id_list.append(proc.pid)
                proc = proc.parent()
        except psutil.NoSuchProcess:
            pass

        # 第三步：exe 路径必须属于 Astron 安装，再加入待杀列表
        all_process = list()
        for pid in all_process_ids:
            try:
                if pid in self_proc_id_list:
                    continue
                proc = psutil.Process(pid)
                proc_exe = proc.exe()
                if not exe_path_matches_astron_install(proc_exe):
                    continue
                all_process.append(proc)
            except Exception:
                pass
        return all_process

    @staticmethod
    def _get_python_proc_in_current_dir_posix():
        """
        macOS / Linux 等 POSIX：无 tasklist，用 psutil 枚举全机进程，供 kill_all_zombie 杀进程树。

        与 _get_python_proc_in_current_dir_win 同一套映像名单：_TASK_IMAGE_NAMES；
        POSIX 侧将「.exe 去掉」得到 _POSIX_NAME_PREFIXES，用进程名 pn 是否以其中任一项为前缀做预筛
        （startswith，不用子串 in，避免误匹配）。

        分三步：
        1) 排除当前进程及其父进程链，避免自杀。
        2) pn 命中任一前缀后再看 exe；否则跳过，减少无关进程的 exe 读取。
        3) exe 路径必须通过 exe_path_matches_astron_install（与 kill_proc_tree 约定一致）。
        """
        # 第一步：当前进程链，不杀
        self_proc_id_list = []
        try:
            proc = psutil.Process(os.getpid())
            while proc:
                self_proc_id_list.append(proc.pid)
                proc = proc.parent()
        except psutil.NoSuchProcess:
            pass

        # 第二、三步：名称前缀命中后再校验安装路径
        out = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                pid = p.info["pid"]
                if pid in self_proc_id_list:
                    continue
                pn = (p.info.get("name") or "").lower()
                if not any(pn.startswith(prefix) for prefix in _POSIX_NAME_PREFIXES):
                    continue
                proc = psutil.Process(pid)
                exe = proc.exe()
                if not exe_path_matches_astron_install(exe):
                    continue
                out.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return out

    @staticmethod
    def get_python_proc_in_current_dir():
        """获取所有在当前目录Python进程（按 win32 → darwin → 其他 POSIX 分发）。"""

        if sys.platform == "win32":
            return Process._get_python_proc_in_current_dir_win()
        elif sys.platform == "darwin":
            return Process._get_python_proc_in_current_dir_posix()
        else:
            return Process._get_python_proc_in_current_dir_posix()

    @staticmethod
    def get_root_process(proc):
        """
        获取根节点进程号(第一个不是python的进程)
        """
        if "python" in proc.name().lower():
            p_proc = proc.parent()
            return Process.get_root_process(p_proc)
        else:
            return proc

    @staticmethod
    def pid_exist_check():
        # 一开始就启动获取root进程号，往往不是rpa进程号，这里异步3秒获取
        time.sleep(3)
        self = psutil.Process(os.getpid())
        root = Process.get_root_process(self)
        root_id = root.pid
        root_name = root.name()
        logger.debug(f"[CheckStartPidExits] 监控 root pid={root_id} name={root_name}")
        while True:
            time.sleep(1)
            try:
                if not psutil.pid_exists(root_id) or psutil.Process(root_id).name() != root_name:
                    logger.warning(f"[CheckStartPidExits] 根进程变化 pid={root_id}，清理退出")
                    # 首先递归杀一遍子进程
                    kill_proc_tree(psutil.Process(os.getpid()), exclude_pids=[os.getpid()])
                    # 再找到当前的启动路径的所有python进程杀一遍
                    Process.kill_all_zombie()
                    # 自行杀掉
                    kill_proc_tree(psutil.Process(os.getpid()))
            except Exception as e:
                logger.exception(e)
