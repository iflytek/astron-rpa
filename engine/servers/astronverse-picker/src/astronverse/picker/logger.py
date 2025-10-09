import sys

from astronverse.baseline.logger.logger import base_logger

argv = sys.argv
base_logger.init("picker")

logger = base_logger.get_log()


def init():
    pass
