import time
from typing import Any

from astronverse.actionlib.types import WinPick
from rpagui.gui import Gui
from astronverse.workflowlib.helper import Helper
from astronverse.window.window import Window


def main(*args, **kwargs) -> Any:
    h = Helper(**kwargs)
    logger = h.logger()
    params = h.params()

    # -------------测试阶段一--普通的参数和返回值定义------------------

    g_a = params.get("a", 0)
    g_b = params.get("b", {})

    logger.info(g_a)
    logger.info(g_b)

    g_a = 12  # 不会影响到全局变量
    g_b["x"] = 789  # 对象会影响到全局变量

    logger.info(g_a)
    logger.info(g_b)

    # -------------测试阶段二--简单的原子能力调用------------------

    Gui().mouse_move(position_x=10, position_y=10)
    time.sleep(3)
    Gui().mouse_move(position_x=20, position_y=20)

    # -------------测试阶段三--带拾取数据的简单原子能力调用------------------

    pick = WinPick(h.element("1881993937947951104", []))
    Window().top(pick=pick)

    # 返回值定义
    return True
