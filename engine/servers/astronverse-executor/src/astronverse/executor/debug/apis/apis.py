from astronverse.executor import ExecuteStatus
from astronverse.executor.debug.apis.ws import wsmg
from astronverse.executor.logger import logger
from astronverse.websocket_server.ws import BaseMsg


def route_init():
    logger.info("路由加载完成")


@wsmg.event("flow", "close")
def close(msg: BaseMsg, svc):
    if svc:
        svc.debug_handler.cmd_force_stop()
        svc.end(ExecuteStatus.CANCEL)
    return {"status": "ok"}


@wsmg.event("flow", "add_break")
async def add_break_list(msg: BaseMsg, svc):
    break_list = msg.data.get("break_list")

    if len(break_list) > 0 and svc:
        for k, v in enumerate(break_list):
            filename = v.get("process_id", v.get("filename", ""))
            if filename:
                svc.debug_handler.set_breakpoint(filename, v.get("line"))
    return {"status": "ok"}


@wsmg.event("flow", "clear_break")
async def clear_bradk(msg: BaseMsg, svc):
    break_list = msg.data.get("break_list")

    if len(break_list) > 0 and svc:
        for k, v in enumerate(break_list):
            filename = v.get("process_id", v.get("filename", ""))
            if filename:
                svc.debug_handler.clear_breakpoint(filename, v.get("line"))
    return {"status": "ok"}


@wsmg.event("flow", "continue")
def debug_continue(msg: BaseMsg, svc):
    if svc:
        svc.debug_handler.cmd_continue()
    return {"status": "ok"}


@wsmg.event("flow", "next")
def debug_next(msg: BaseMsg, svc):
    if svc:
        svc.debug_handler.cmd_next()
    return {"status": "ok"}
