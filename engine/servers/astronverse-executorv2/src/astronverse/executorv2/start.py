import argparse
import threading
import time

from astronverse.executorv2 import ExecuteStatus
from astronverse.executorv2.apis.ws import Ws
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

    svc = Svc(conf=Config, debug_model=args.debug == "y")

    # Ws服务
    ws = Ws(svc=svc)
    if Config.open_log_ws:
        ws.is_open_web_link = Config.wait_web_ws
        ws.is_open_top_link = Config.wait_tip_ws
        thread_ws = threading.Thread(target=ws.server, args=(), daemon=True)
        thread_ws.start()

    # 录制服务
    pass

    # 右下角日志窗口
    if Config.wait_tip_ws:
        pass

    # 生成代码
    flow = Flow(svc=svc)
    flow.gen_code(project_id=args.project_id, project_name=args.project_name, mode=args.mode, version=args.version)

    # 执行前验证
    if Config.open_log_ws:
        wait_time = 0
        while not ws.check_ws_link():
            time.sleep(0.3)
            wait_time += 0.3
            if wait_time >= 10:
                logger.error("The websocket connection timed out")
                svc.end(ExecuteStatus.CANCEL, "", "")

    # 执行代码
    debug = Debug(svc=svc)
    svc.debug_handler = debug
    debug.start()

    # 执行后验证
    if Config.open_log_ws and Config.wait_web_ws:
        wait_time = 0
        size = svc.report.code.queue.qsize()
        while not svc.report.code.queue.empty():
            time.sleep(0.3)
            wait_time += 0.3
            if wait_time >= 3:
                wait_time = 0
                # 等待日志(n)s内没有任何发送，就不发送了，直接退出
                if size == svc.report.code.queue.qsize():
                    logger.error("The websocket connection send timed out")
                    break
                else:
                    size = svc.report.code.queue.qsize()

    svc.end(ExecuteStatus.SUCCESS, "", "")
    logger.debug("end ok")
