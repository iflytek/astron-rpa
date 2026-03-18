import argparse
import time
import traceback
from pathlib import Path
import uvicorn
from astronverse.scheduler.logger import logger
from astronverse.baseline.config.config import load_config
from astronverse.scheduler.apis import router
from astronverse.scheduler.config import Config
from astronverse.scheduler.core.schduler.init import linux_env_check, win_env_check
from astronverse.scheduler.core.server import ServerManager
from astronverse.scheduler.core.servers.async_server import (
    CheckPickProcessAliveServer,
    CheckStartPidExitsServer,
    RpaSchedulerAsyncServer,
    TerminalAsyncServer,
)
from astronverse.scheduler.core.servers.core_server import (
    RpaBrowserConnectorServer,
    RpaRouteServer,
)
from astronverse.scheduler.core.setup.setup import Process
from astronverse.scheduler.core.svc import get_svc
from astronverse.scheduler.utils.utils import check_port
from fastapi import FastAPI

# 0. app实例化，并做初始化
app = FastAPI()
router.handler(app)


def start(args):
    try:
        # 2. 读取配置，并解析到上下文
        conf_path = Path(args.conf.strip('"').replace("\\\\", "\\")).resolve()
        conf_data = load_config(conf_path)

        Config.conf_file = conf_path
        Config.remote_addr = conf_data.get("remote_addr")
        svc = get_svc()
        svc.set_config(Config)

        route_port = getattr(svc, "rpa_route_port", None)
        schedule_port = getattr(svc, "scheduler_port", None)
        logger.info(
            f"[startup] 端口 scheduler={schedule_port} rpa_route={route_port}"
        )

        # 3. 环境检测
        logger.info("[startup] 环境检测开始")
        Process.kill_all_zombie()
        logger.info("[startup] kill_all_zombie 完成")
        win_env_check(svc)
        logger.info("[startup] win_env_check 完成")
        linux_env_check()
        logger.info("[startup] linux_env_check 完成")

        # 4. 服务注册与启动
        logger.info("[startup] ServerManager 注册子服务并启动")
        server_mg = ServerManager(svc)
        server_mg.register(RpaRouteServer(svc))
        server_mg.register(RpaBrowserConnectorServer(svc))
        server_mg.register(RpaSchedulerAsyncServer(svc))
        server_mg.register(TerminalAsyncServer(svc))
        server_mg.register(CheckPickProcessAliveServer(svc))
        server_mg.register(CheckStartPidExitsServer(svc))
        server_mg.register(svc.trigger_server)
        if svc.vnc_server:
            logger.info("[startup] 注册 VNC 服务")
            server_mg.register(svc.vnc_server)
        server_mg.run()
        logger.info("[startup] ServerManager.run() 已执行完毕")

        # 5. 等待本地网关加载完成，并注册服务
        logger.info(
            f"[startup] 等待本地路由 127.0.0.1:{route_port} 可连"
        )
        wait_route_t0 = time.monotonic()
        wait_ticks = 0
        while check_port(port=svc.rpa_route_port):
            wait_ticks += 1
            time.sleep(0.1)
            if wait_ticks % 50 == 0:
                elapsed = time.monotonic() - wait_route_t0
                logger.warning(
                    f"[startup] 路由端口 {route_port} 仍未就绪，已等待 {elapsed:.1f}s"
                )
        logger.info(
            f"[startup] 路由已就绪，耗时 {time.monotonic() - wait_route_t0:.2f}s"
        )
        svc.route_server_is_start = True
        svc.register_server()
        logger.info("[startup] register_server 完成")

        # 6. 向前端发送完成初始化完成消息, 写到了 startup 方法里面

        # 7. 启动服务
        logger.info(
            f"[startup] 启动 uvicorn 0.0.0.0:{schedule_port} workers=1"
        )
        uvicorn.run(
            app="astronverse.scheduler.start:app",
            host="0.0.0.0",
            port=svc.scheduler_port,
            workers=1,
        )
    except Exception as e:
        logger.error("astronverse.scheduler error: {} traceback: {}".format(e, traceback.format_exc()))
