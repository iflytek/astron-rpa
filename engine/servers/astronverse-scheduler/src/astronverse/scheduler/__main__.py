from astronverse.scheduler.logger import logger
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="{} service".format("scheduler"))
    parser.add_argument("--conf", type=str, default="../resources/conf.json", help="配置文件")
    parser.add_argument("--venv", type=str, help="配置文件")
    parser.add_argument("--stop", type=bool, default=False, help="关闭服务")
    args = parser.parse_args()
    logger.info("args: {} service[:{}] start".format(args, "astronverse.scheduler"))

    if args.stop:
        from astronverse.scheduler.core.setup.setup import Process

        Process.kill_all_zombie()
    else:
        from astronverse.scheduler.start import start

        start(args)
