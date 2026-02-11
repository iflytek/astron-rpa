import sys

from astronverse.executor.utils.utils import platform_python_venv_run_dir


class Config:
    # 端口号
    port: int = 0

    # 本地网关端口号
    gateway_port: int = 0

    # 执行id
    exec_id: str = ""

    # 工程id
    project_id: str = ""

    # 主流程名称（中文显示用）
    main_process_name: str = "主流程"

    # 代码缩进规范（4个空格）
    indentation: str = " " * 4

    # 项目生成根目录路径
    gen_core_path: str = "{}/astron/".format(platform_python_venv_run_dir(sys.executable))

    # 组件生成目录
    gen_component_path: str = "{}/astron_extension/".format(platform_python_venv_run_dir(sys.executable))

    # 主入口脚本文件名
    main_file_name: str = "main.py"

    # 日志存储位置
    log_path: str = "./logs/"

    # package cache
    package_cache_dir: str = "./pip_cache/"

    # resource dir
    resource_dir: str = "./"

    # 开启ws日志通信
    open_log_ws: bool = True

    # 是否等待前端ws连接
    wait_web_ws: bool = True

    # 是否开启并等待右下角ws连接
    wait_tip_ws: bool = False

    # 是否是 debug 模式
    debug_mode: bool = False

    # 是否是 debug 模式
    is_custom_component: bool = False
