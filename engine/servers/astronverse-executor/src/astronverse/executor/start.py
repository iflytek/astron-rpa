import argparse
import json
import os
import threading
import time
from urllib.parse import unquote
from astronverse.actionlib import ReportFlow, ReportType, ReportFlowStatus
from astronverse.executor import ExecuteStatus
from astronverse.executor.debug.apis.ws import Ws
from astronverse.executor.debug.debug import Debug
from astronverse.executor.debug.debug_svc import DebugSvc
from astronverse.executor.error import (
    MSG_FLOW_INIT_START,
    MSG_FLOW_INIT_SUCCESS,
    MSG_TASK_EXECUTION_START,
    MSG_TASK_EXECUTION_END,
)
from astronverse.executor.flow.flow_svc import FlowSvc
from astronverse.executor.logger import logger
from astronverse.executor.config import Config
from astronverse.executor.flow.flow import Flow


def flow_start(args, conf):
    svc = FlowSvc(conf=conf)
    flow = Flow(svc=svc)
    flow.gen_component(
        path=svc.conf.gen_component_path, project_id=args.project_id, mode=args.mode, version=args.version
    )
    flow.gen_code(
        path=svc.conf.gen_core_path,
        project_id=args.project_id,
        project_name=args.project_name,
        mode=args.mode,
        version=args.version,
        process_id=args.process_id,
        line=int(args.line),
        end_line=int(args.end_line),
    )


def debug_start(args, conf):
    svc = DebugSvc(conf=conf, debug_model=args.debug == "y")

    # Ws服务
    ws = Ws(svc=svc)
    if Config.open_log_ws:
        ws.is_open_web_link = Config.wait_web_ws
        ws.is_open_top_link = Config.wait_tip_ws
        thread_ws = threading.Thread(target=ws.server, args=(), daemon=True)
        thread_ws.start()

    # 录制服务
    if args.recording_config.get("enable", False):
        file_clear_time = args.recording_config.get("fileClearTime", 0)
        if not args.recording_config.get("saveType", False):
            file_clear_time = 0
        temp_config = {
            "open": args.recording_config.get("enable", False),
            "cut_time": args.recording_config.get("cutTime", 0),
            "scene": args.recording_config.get("scene", "always"),
            "file_path": args.recording_config.get("filePath", "./logs/report"),
            "file_clear_time": file_clear_time,  # 清理录制视频7天
        }
        svc.recording_tool.init(args.project_id, args.exec_id, temp_config).start()

    # 右下角日志窗口
    if Config.wait_tip_ws:
        svc.log_tool.start()

    # 生成日志
    svc.report.info(ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.INIT, msg_str=MSG_FLOW_INIT_START))
    svc.report.info(
        ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.INIT_SUCCESS, msg_str=MSG_FLOW_INIT_SUCCESS)
    )

    # 执行前验证
    if Config.open_log_ws:
        wait_time = 0
        while not ws.check_ws_link():
            time.sleep(0.3)
            wait_time += 0.3
            if wait_time >= 10:
                logger.error("The websocket connection timed out")
                svc.end(ExecuteStatus.CANCEL)

    # 执行代码
    debug = Debug(svc=svc, args=args)
    svc.debug_handler = debug
    svc.report.info(
        ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.TASK_START, msg_str=MSG_TASK_EXECUTION_START)
    )
    data = debug.start(params=args.run_param)

    # 执行后验证
    if Config.open_log_ws and Config.wait_web_ws:
        wait_time = 0
        size = svc.report.queue.qsize()
        while not svc.report.queue.empty():
            time.sleep(0.3)
            wait_time += 0.3
            if wait_time >= 3:
                wait_time = 0
                # 等待日志(n)s内没有任何发送，就不发送了，直接退出
                if size == svc.report.queue.qsize():
                    logger.error("The websocket connection send timed out")
                    break
                else:
                    size = svc.report.queue.qsize()

    svc.end(ExecuteStatus.SUCCESS, data=data)


def start():
    parser = argparse.ArgumentParser(description="{} service".format("executor"))
    parser.add_argument("--port", default="13158", help="本地端口号", required=False)
    parser.add_argument("--gateway_port", default="13159", help="网关端口", required=False)
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
    parser.add_argument("--wait_web_ws", default="n", help="[ws通信]等待前端ws连接 y/n", required=False)
    parser.add_argument("--wait_tip_ws", default="y", help="[ws通信]开启并等待右下角ws连接 y/n", required=False)

    parser.add_argument("--resource_dir", default="", help="资源目录", required=False)
    parser.add_argument("--recording_config", default="", help="录屏", required=False)
    args = parser.parse_args()

    logger.debug("start {}".format(args))

    # 配置
    Config.port = args.port
    Config.gateway_port = args.gateway_port
    Config.exec_id = args.exec_id
    Config.project_id = args.project_id
    if args.project_name:
        Config.project_name = unquote(args.project_name)
    if args.resource_dir:
        args.resource_dir = unquote(args.resource_dir)
        Config.resource_dir = args.resource_dir

    Config.open_log_ws = args.log_ws == "y"
    Config.wait_web_ws = args.wait_web_ws == "y"
    Config.wait_tip_ws = args.wait_tip_ws == "y"
    Config.debug_mode = args.debug == "y"

    if args.run_param:
        try:
            args.run_param = unquote(args.run_param)
            if os.path.exists(args.run_param):
                with open(args.run_param, "r", encoding="utf-8") as f:
                    args.run_param = json.load(f)
            else:
                args.run_param = json.loads(args.run_param)
        except Exception as e:
            args.run_param = {}
    else:
        args.run_param = {}
    if args.recording_config:
        try:
            args.recording_config = unquote(args.recording_config)
            args.recording_config = json.loads(args.recording_config)
        except Exception as e:
            args.recording_config = {}
    else:
        args.recording_config = {}

    # 生成代码
    flow_start(conf=Config, args=args)

    # 执行代码
    debug_start(conf=Config, args=args)

    logger.debug("end")
