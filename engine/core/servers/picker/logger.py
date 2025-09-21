import sys

from rpaframe.logger.logger import base_logger

argv = sys.argv
base_logger.init("rpa_pick")

logger = base_logger.get_log()


def init():
    pass
