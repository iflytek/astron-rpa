from enum import Enum


class ComponentType(Enum):
    """
    枚举组件类型
    """

    # 路由
    ROUTE = 0
    # 拾取
    PICKER = 1
    # 执行器
    EXECUTOR = 2
    # 浏览器通信中间件
    BROWSER_CONNECTOR = 3
    # 调度器
    SCHEDULER = 4
    # CV拾取
    CV_PICKER = 5
    # 触发器
    TRIGGER = 6


class ServerLevel(Enum):
    CORE = 1  # 核心 必须是在启动前启动
    NORMAL = 2  # 普通 可以在启动后启动
