import argparse
import os.path
from astronverse.executorv2.logger import logger
from astronverse.executorv2.config import Config
from astronverse.executorv2.flow.flow import Flow
from astronverse.executorv2.svc import Svc
from astronverse.executorv2.run.debug import Debug


def start():
    parser = argparse.ArgumentParser(description="{} service".format("executor"))
    parser.add_argument("--port", default="8077", help="本地端口号", required=False)
    parser.add_argument("--gateway_port", default="8003", help="网关端口", required=False)
    parser.add_argument("--project_id", default="", help="启动的工程id", required=True)
    parser.add_argument("--project_name", default="", help="启动的工程名称", required=False)
    parser.add_argument("--mode", default="EDIT_PAGE", help="运行场景", required=False)
    parser.add_argument("--version", default="", help="运行版本", required=False)
    parser.add_argument("--run_param", default="", help="运行参数", required=False)
    parser.add_argument("--exec_id", default="", help="启动的执行id", required=False)

    parser.add_argument("--process_id", default="", help="[调试]启动的流程id", required=False)
    parser.add_argument("--line", default="0", help="[调试]启动的行号", required=False)
    parser.add_argument("--end_line", default="0", help="[调试]结束的行号", required=False)
    parser.add_argument("--debug", default="n", help="[调试]是否是debug模式 y/n", required=False)

    parser.add_argument("--log_ws", default="y", help="[ws通信]ws总开关 y/n", required=False)
    parser.add_argument("--wait_web_ws", default="y", help="[ws通信]等待前端ws连接 y/n", required=False)
    parser.add_argument("--wait_tip_ws", default="n", help="[ws通信]开启并等待右下角ws连接 y/n", required=False)
    args = parser.parse_args()

    logger.debug("executor start {}".format(args))

    # 生成代码
    Config.port = args.port
    Config.gateway_port = args.gateway_port
    Config.exec_id = args.exec_id
    Config.project_id = args.project_id

    Config.open_log_ws = args.log_ws == "y"
    Config.wait_web_ws = args.wait_web_ws == "y"
    Config.wait_tip_ws = args.wait_tip_ws == "y"

    svc = Svc(conf=Config)

    # 生成代码
    flow = Flow(svc=svc)
    flow.gen_code(project_id=args.project_id, project_name=args.project_name, mode=args.mode, version=args.version)

    # 执行代码
    debug = Debug(svc.conf.gen_core_path)
    svc.debug = debug
    debug.set_breakpoint("main.py", 1)
    debug.set_breakpoint("module1.py", 10)
    debug.cmd_start()
