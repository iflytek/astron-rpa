from typing import Any
from astronverse.workflowlib import print, logger, param
from package import element, element_img, gv


def main(args) -> Any:
    p = param(args)

    # 打印所有流变量key
    logger.info(p.keys())

    return True
