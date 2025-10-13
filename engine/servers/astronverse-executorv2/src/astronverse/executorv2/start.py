import argparse
import os.path

from astronverse.executorv2.logger import logger
from astronverse.executorv2.pdb.debug import Debug


def start():
    parser = argparse.ArgumentParser(description="{} service".format("executor"))
    parser.add_argument("--port", default="8077", help="[系统配置]本地端口号", required=False)
    parser.add_argument("--gateway_port", default="8003", help="[系统配置]网关端口", required=False)
    parser.add_argument("--mode", default="EDIT_PAGE", help="[启动配置]运行场景", required=False)
    parser.add_argument("--version", default="", help="[启动配置]运行版本", required=False)
    parser.add_argument("--project_id", default="", help="[启动配置]启动的工程id", required=True)
    parser.add_argument("--project_name", default="RPA机器人", help="工程名称", required=False)
    parser.add_argument("--process_id", default="", help="[启动配置]启动的流程id", required=False)
    args = parser.parse_args()

    logger.debug("start {}".format(args))

    # 如果启用调试模式
    debug = Debug(os.path.abspath("project/main.py"))
    debug.run_path()



