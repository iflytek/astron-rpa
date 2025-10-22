from astronverse.executorv2 import ExecuteStatus
from astronverse.executorv2.apis.ws import wsmg
from astronverse.executorv2.svc import Svc
from astronverse.executorv2.logger import logger
from astronverse.websocket_server.ws import BaseMsg


def route_init():
    logger.info("路由加载完成")


@wsmg.event("flow", "close")
def close(msg: BaseMsg, svc: Svc):
    if svc:
        svc.end(ExecuteStatus.CANCEL, "", "")
    return {"status": "ok"}


@wsmg.event("flow", "add_break")
async def add_break_list(msg: BaseMsg, svc: Svc):
    break_list = msg.data.get("break_list")

    if len(break_list) > 0 and svc:
        for k, v in enumerate(break_list):
            process_info = svc.get_process_info(v.get("process_id"))
            if process_info:
                svc.debug.set_breakpoint(process_info.process_file_name, v.get("line"))
    return {"status": "ok"}


@wsmg.event("flow", "clear_break")
async def clear_bradk(msg: BaseMsg, svc: Svc):
    break_list = msg.data.get("break_list")

    if len(break_list) > 0 and svc:
        for k, v in enumerate(break_list):
            process_info = svc.get_process_info(v.get("process_id"))
            if process_info:
                svc.debug.clear_breakpoint(process_info.process_file_name, v.get("line"))
    return {"status": "ok"}


@wsmg.event("flow", "continue")
def debug_continue(msg: BaseMsg, svc: Svc):
    if svc:
        svc.debug.cmd_continue()
    return {"status": "ok"}


@wsmg.event("flow", "next")
def debug_next(msg: BaseMsg, svc: Svc):
    if svc:
        svc.debug.cmd_next()
    return {"status": "ok"}
