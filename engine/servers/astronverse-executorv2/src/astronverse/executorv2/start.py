import argparse
import os.path
from astronverse.executorv2.logger import logger
from astronverse.executorv2.config import Config
from astronverse.executorv2.flow.flow import Flow
from astronverse.executorv2.flow.svc import Svc
from astronverse.executorv2.pdb.debug import Debug


def start():
    parser = argparse.ArgumentParser(description="{} service".format("executor"))
    parser.add_argument("--port", default="8077", help="本地端口号", required=False)
    parser.add_argument("--gateway_port", default="8003", help="网关端口", required=False)
    parser.add_argument("--project_id", default="", help="启动的工程id", required=True)
    parser.add_argument("--project_name", default="", help="启动的工程名称", required=False)
    parser.add_argument("--mode", default="EDIT_PAGE", help="运行场景", required=False)
    parser.add_argument("--version", default="", help="运行版本", required=False)
    args = parser.parse_args()

    logger.debug("executor start {}".format(args))

    # 生成代码
    svc = Svc(args=args, conf=Config)
    # flow = Flow(svc=svc)
    # flow.gen_code(project_id=args.project_id, project_name=args.project_name, mode=args.mode, version=args.version)

    # 执行代码 - 使用project目录进行多文件调试
    debug = Debug(svc.conf.GEN_CORE_PATH)
    debug.set_breakpoint("main.py", 1)
    debug.set_breakpoint("module1.py", 10)
    debug.cmd_start()
