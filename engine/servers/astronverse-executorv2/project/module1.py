from typing import Any
from rpahelper.helper import Helper, print, logger


def main(*args, **kwargs) -> Any:
    h = Helper(**kwargs)
    params = h.params()

    # 打印所有的变量key
    logger.info(params.keys())

    return True
