import os
import sys
from urllib.parse import urlparse
from astronverse.actionlib import ReportTip
from importlib_metadata import version as check_version
from astronverse.executor.error import MSG_DOWNLOAD_FORMAT, MSG_DOWNLOAD_SUCCESS_FORMAT
from astronverse.executor.logger import logger
from astronverse.executor.utils.utils import exec_run


def compare_versions(v1, v2):
    for i in range(max(len(v1), len(v2))):
        num1 = v1[i] if i < len(v1) else 0
        num2 = v2[i] if i < len(v2) else 0
        if num1 > num2:
            return 1
        elif num1 < num2:
            return -1
    return 0


def find_version(lib, ver, ver_strict) -> bool:
    try:
        v0 = [int(x) for x in check_version(lib).split(".")]
        if ver:
            if not ver_strict:
                # 宽松模式
                v1 = [[int(x) for x in ver.split(".")][0]]
                if compare_versions(v0, v1) >= 0 and compare_versions([v1[0] + 1], v0) > 0:
                    return True
            else:
                # 严格模式
                if compare_versions(v0, [int(x) for x in ver.split(".")]) == 0:
                    return True
        else:
            # 没有版本号，直接返回
            return True
    except Exception as e:
        # 没有library
        pass
    return False


class Package:
    def __init__(self, svc):
        self.svc = svc
        self.library_cache = {}

    def download(self, library: str, version: str, mirror: str = "", version_strict: bool = False, error_try=True):
        # 1. 快速结束
        if not library:
            return

        # 2. cache
        if library in self.library_cache:
            return
        self.library_cache[library] = True

        # 3. 版本检查
        if find_version(library, version, version_strict):
            return

        # 4. 初始化
        self.svc.report.info(ReportTip(msg_str=MSG_DOWNLOAD_FORMAT.format(library)))

        pip_cache_dir = os.path.join(self.svc.conf.package_cache_dir)
        if not os.path.exists(pip_cache_dir):
            os.makedirs(pip_cache_dir)

        # 6. 下载

        # 6.1 下载的名称
        if version:
            if version_strict:
                cmd_name = "{}=={}".format(library, version)
            else:
                v1 = [[int(x) for x in version.split(".")][0]]
                v2 = [v1[0] + 1]
                cmd_name = "{}>={},<{}".format(library, ".".join(str(x) for x in v1), ".".join(str(x) for x in v2))
        else:
            cmd_name = library

        # 6.2 下载的mirror
        if mirror:
            mirror = ["--index-url", mirror, "--trusted-host", urlparse(mirror).hostname]

        # 6.3 下载的命令
        pip_download = [
            sys.executable,
            "-m",
            "pip",
            "download",
            cmd_name,
            "-d",
            pip_cache_dir,
            *mirror,
            "--disable-pip-version-check",
            "--no-cache",
        ]
        pip_install_1 = [
            sys.executable,
            "-m",
            "pip",
            "install",
            cmd_name,
            "--no-index",
            "--find-links={}".format(pip_cache_dir),
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]
        pip_install_2 = [
            sys.executable,
            "-m",
            "pip",
            "install",
            cmd_name,
            "--find-links={}".format(pip_cache_dir),
            *mirror,
            "--no-warn-script-location",
            "--disable-pip-version-check",
        ]

        try:
            exec_run(pip_download, False, 600)
        except Exception as e:
            logger.warning("pip_download error: {}".format(e))
            pass

        def __install_pip(cmd):
            try:
                exec_run(cmd, False, 600)
            except Exception as e:
                # 3. 再检查一遍版本检查
                if find_version(library, version, version_strict):
                    return
                logger.error("__install_pip error:{}".format(e))
                raise e

        try:
            __install_pip(pip_install_1)
        except Exception as e:
            if error_try:
                __install_pip(pip_install_2)
            else:
                raise e

        self.svc.report.info(ReportTip(msg_str=MSG_DOWNLOAD_SUCCESS_FORMAT.format(library)))
