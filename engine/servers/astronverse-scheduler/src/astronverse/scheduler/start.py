import argparse
import time
import traceback
from pathlib import Path

import uvicorn
from astronverse.baseline.config.config import load_config
from fastapi import FastAPI

from astronverse.scheduler.apis import route
from astronverse.scheduler.config import Config
from astronverse.scheduler.core.schduler.init import linux_env_check, repair_pywin32_dependence
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
from astronverse.scheduler.core.svc import get_svc
from astronverse.scheduler.logger import logger
from astronverse.scheduler.utils.utils import check_port

# 0. app实例化，并做初始化
app = FastAPI()
route.handler(app)


def start():
    try:
        # 1. 初始化配置
        parser = argparse.ArgumentParser(description="{} service".format("scheduler"))
        parser.add_argument("--conf", type=str, default="../resources/conf.json", help="配置文件")
        parser.add_argument("--venv", type=str, help="配置文件")
        args = parser.parse_args()

        logger.info("args: {} service[:{}] start".format(args, "astronverse.scheduler"))

        # 2. 读取配置，并解析到上下文
        conf_path = Path(args.conf.strip('"').replace("\\\\", "\\")).resolve()
        conf_data = load_config(conf_path)

        Config.app_server.conf_file = conf_path
        Config.app_server.remote_addr = conf_data.get("remote_addr")
        Config.base_pipy_server.pypi_remote = conf_data.get("pypi_remote")
        svc = get_svc()
        svc.set_config(Config)

        # 3. 环境检测

        # Process.kill_all_zombie()
        repair_pywin32_dependence(svc)
        linux_env_check()

        # 4. 服务注册与启动
        server_mg = ServerManager(svc)
        server_mg.register(RpaRouteServer(svc))
        server_mg.register(RpaBrowserConnectorServer(svc))
        server_mg.register(RpaSchedulerAsyncServer(svc))
        server_mg.register(TerminalAsyncServer(svc))
        # server_mg.register(AtomicUploadAsyncServer(svc))
        server_mg.register(CheckPickProcessAliveServer(svc))
        server_mg.register(CheckStartPidExitsServer(svc))

        server_mg.register(svc.trigger_server)
        if svc.vnc_server:
            server_mg.register(svc.vnc_server)
        server_mg.run()

        # 5. 等待本地网关加载完成，并注册服务
        while check_port(port=svc.rpa_route_port):  # 等待本地路由加载完成
            time.sleep(0.1)
        svc.route_server_is_start = True
        svc.register_server()

        # 6. 向前端发送完成初始化完成消息, 写到了 startup 方法里面

        # 7. 启动服务
        uvicorn.run(
            app="astronverse.scheduler.start:app",
            host="0.0.0.0",
            port=svc.scheduler_port,
            workers=1,
        )
    except Exception as e:
        logger.error("astronverse.scheduler error: {} traceback: {}".format(e, traceback.format_exc()))
