class Config:
    # 远程服务
    REMOTE_ADDR = None  # 服务端远程地址

    # PIPY配置
    PYPI_SERVER_REMOTE = None  # Pypi私仓地址

    # 本地缓存
    PIP_CACHE_DIR = "pip_cache"  # pip cache 文件目录

    # 配置文件
    CONF_FILE = ""


config = Config()
