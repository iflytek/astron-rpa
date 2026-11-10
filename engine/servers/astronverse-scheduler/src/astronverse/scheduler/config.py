import sys

from astronverse.scheduler.utils.platform_utils import platform_python_run_dir


class Config:
    """
    调度器核心功能
    """

    # 应用名称
    app_name: str = "scheduler"
    # 远程地址
    remote_addr: str = None
    # config源文件
    conf_file: str = None
    # python运行目录
    python_run_dir = platform_python_run_dir(sys.executable)
    # core_python
    python_core = sys.executable
    # base_python
    python_base = sys.executable
    # 虚拟环境dir
    venv_base_dir = "venvs"
    # extra pip index hosts allowed in addition to the built-in list
    pip_mirror_allow_hosts: list = []
    # Scheduler is local by default. Remote operator access must explicitly
    # bind a non-loopback address and provide this token.
    scheduler_bind_host: str = "127.0.0.1"
    scheduler_api_token: str = ""
