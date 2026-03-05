import argparse
import json
import os
import threading
import time
import traceback
from urllib.parse import unquote
from astronverse.executor.error import *
from astronverse.actionlib import ReportFlow, ReportFlowStatus, ReportType
from astronverse.executor import ExecuteStatus
from astronverse.executor.config import Config
from astronverse.executor.debug.apis.ws import Ws
from astronverse.executor.debug.debug import Debug
from astronverse.executor.debug.debug_svc import DebugSvc
from astronverse.executor.flow.flow import Flow
from astronverse.executor.flow.flow_svc import FlowSvc
from astronverse.executor.utils.utils import str_to_list_if_possible


def flow_start(svc, args):
    package_info = svc.load_package_info()
    try:
        old_version = int(package_info.get("project_info", {}).get("version", ""))
    except Exception as e:
        old_version = 0
    try:
        new_version = int(args.version)
    except Exception as e:
        new_version = 0
    if 0 < old_version == new_version:
        pass
    else:
        flow = Flow(svc=svc)
        flow.gen_component(
            path=svc.conf.gen_component_path, project_id=args.project_id, mode=args.mode, version=args.version
        )
        flow.gen_code(
            path=svc.conf.gen_core_path,
            project_id=args.project_id,
            mode=args.mode,
            version=args.version,
            process_id=args.process_id,
            line=int(args.line),
            end_line=int(args.end_line),
        )


def debug_start(args, flow_svc, svc):
    try:
        # Ws服务
        ws = Ws(svc=svc)
        if Config.open_log_ws:
            ws.is_open_web_link = Config.wait_web_ws
            ws.is_open_top_link = Config.wait_tip_ws
            thread_ws = threading.Thread(target=ws.server, args=(), daemon=True)
            thread_ws.start()

        # 右下角日志窗口（尝试从缓存读取项目信息）
        if Config.wait_tip_ws:
            svc.log_tool.start()

        # 生成代码
        flow_start(svc=flow_svc, args=args)

        # 加载ast_globals
        svc.load_package_info()

        # 生成代码错误消息
        if flow_svc.flow_tip:
            for tip in flow_svc.flow_tip:
                svc.report.info(tip)

        # 特殊参数处理 录制服务
        if args.recording_config:
            try:
                # 1. 解析配置
                raw = json.loads(unquote(args.recording_config))

                # 2. 构建录制配置
                if raw.get("enable"):
                    file_clear_time = raw.get("fileClearTime", 0)
                    if not raw.get("saveType"):
                        file_clear_time = 0
                    config = {
                        "open": raw.get("enable", False),
                        "cut_time": raw.get("cutTime", 0),
                        "scene": raw.get("scene", "always"),
                        "file_path": raw.get("filePath", "./logs/report"),
                        "file_clear_time": file_clear_time,  # 清理录制视频7天
                    }
                    svc.recording_tool.init(args.project_id, args.exec_id, config).start()
            except Exception:
                pass

        # 特殊参数处理 run_param
        run_param = {}
        if args.run_param:
            try:
                # 1. 解码并加载 JSON（文件或字符串）
                raw = unquote(args.run_param) # noqa
                if os.path.exists(raw):
                    with open(raw, encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = json.loads(raw)  # 原始版本的冗余判断已移除，逻辑等价

                # 2. 解析参数列表
                if isinstance(data, list):
                    for p in data:
                        param = flow_svc.param.parse_param({
                            "value": str_to_list_if_possible(p.get("varValue")),
                            "types": p.get("varType"),
                            "name": p.get("varName"),
                        })
                        val = param.show_value()
                        run_param[p.get("varName")] = eval(val, {}, {}) if val else ""
            except Exception:
                pass

        # 生成启动日志
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
                    return

        # 执行代码
        debug = Debug(svc=svc, args=args)
        svc.debug = debug
        svc.debug_handler = debug
        svc.report.info(
            ReportFlow(log_type=ReportType.Flow, status=ReportFlowStatus.TASK_START, msg_str=MSG_TASK_EXECUTION_START)
        )
        data = debug.start(params=run_param)

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
    except BizException as e:
        logger.error("error {} traceback {}".format(e, traceback.format_exc()))
        svc.end(ExecuteStatus.FAIL, reason=e.code.message)
        return
    except Exception as e:
        logger.error("error {} traceback {}".format(e, traceback.format_exc()))
        svc.end(ExecuteStatus.FAIL, reason=MSG_EXECUTION_ERROR)
        return
    logger.debug("end")


def start():
    parser = argparse.ArgumentParser(description="{} service".format("executor"))
    parser.add_argument("--port", default="13158", help="本地端口号", required=False)
    parser.add_argument("--gateway_port", default="13159", help="网关端口", required=False)
    parser.add_argument("--project_id", default="", help="启动的工程id", required=True)
    parser.add_argument("--project_name", default="", help="启动的工程名称[废弃]", required=False)
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
    parser.add_argument("--wait_tip_ws", default="n", help="[ws通信]开启并等待右下角ws连接 y/n", required=False)

    parser.add_argument("--resource_dir", default="", help="资源目录", required=False)
    parser.add_argument("--recording_config", default="", help="录屏", required=False)
    parser.add_argument("--is_custom_component", default="n", help="是否是自定义组件 y/n", required=False)
    args = parser.parse_args()

    logger.debug("start {}".format(args))

    # 配置
    Config.port = args.port
    Config.gateway_port = args.gateway_port
    Config.exec_id = args.exec_id
    Config.project_id = args.project_id
    if args.resource_dir:
        args.resource_dir = unquote(args.resource_dir)
        Config.resource_dir = args.resource_dir

    Config.open_log_ws = args.log_ws == "y"
    Config.wait_web_ws = args.wait_web_ws == "y"
    Config.wait_tip_ws = args.wait_tip_ws == "y"
    Config.debug_mode = args.debug == "y"
    Config.is_custom_component = args.is_custom_component == "y"

    # 上下文
    flow_svc = FlowSvc(conf=Config)
    debug_svc = DebugSvc(conf=Config, debug_model=args.debug == "y")
    debug_start(args=args, flow_svc=flow_svc, svc=debug_svc)