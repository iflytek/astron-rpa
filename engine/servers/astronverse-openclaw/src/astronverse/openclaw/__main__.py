import argparse

from astronverse.openclaw.config import config
from astronverse.openclaw.logger import logger
from astronverse.openclaw.server.server import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="astronverse-openclaw service")
    parser.add_argument("--port", default="8099", help="服务端口号", required=False)
    parser.add_argument("--host", default="127.0.0.1", help="服务绑定地址", required=False)
    args = parser.parse_args()

    config.port = int(args.port)
    config.host = args.host

    logger.info("start astronverse-openclaw %s", args)

    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)
