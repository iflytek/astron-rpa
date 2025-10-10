import logging


class Config:
    # 主进程监端口
    VISION_PICKER_PORT = None
    # 服务启动端口开始端
    LOCAL_PORT_START = 32000
    # 本地日志文件
    LOG_BASE_DIR = "logs"
    # log日志等级
    LOG_LEVEL = logging.DEBUG
    # 高亮程序端口号
    HIGHLIGHT_SOCKET_PORT = 11001
    REMOTE_ADDR = None
