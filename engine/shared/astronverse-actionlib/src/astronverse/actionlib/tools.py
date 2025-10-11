import copy
import json
import time
import uuid as uid
from dataclasses import dataclass
from threading import Event
from typing import Any

from astronverse.actionlib.logger import logger


# ------------------rpawebsocket包内容------------------
def gen_event_id():
    """
    生成uuid
    """

    return "{}".format(str(uid.uuid4()))


@dataclass
class BaseMsg:
    """
    BaseMsg 基础消息
    """

    # 回复事件id 已http的形式使用 适合一来一回的消息
    reply_event_id: str = None
    # 事件id 唯一值
    event_id: str = None
    # 事件发生的时间戳
    event_time: int = None
    # 业务 大业务
    channel: str = None
    # 事件名称 大业务下面的小事件
    key: str = None
    # 用户名，客户标识，同一个客户多个连接，发送时会广播，主要时解决回收不及时问题
    uuid: str = None
    # 消息发送给
    send_uuid: str = None
    # 是否需要ack[无效]
    need_ack: bool = None
    # 是否需要回复
    need_reply: bool = None
    # 数据
    data: dict = None

    def to_reply(self):
        res_msg = copy.deepcopy(self)
        res_msg.reply_event_id = self.event_id
        res_msg.uuid = self.send_uuid
        res_msg.send_uuid = self.uuid
        res_msg.data = None
        res_msg.init()
        return res_msg

    def init(self):
        self.event_id = gen_event_id()
        self.event_time = int(time.time())
        return self

    def tojson(self, filtered_none: bool = True):
        data = self.__dict__
        if filtered_none:
            data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data, ensure_ascii=False)


# ------------------rpawebsocket包内容------------------


def tools(ws, tool, tool_value: Any, time_out_ws=5):
    """
    提供一种区别于report的跟前端通信的机制
    相较于report的区别
    1. 不是通过管道，没有消息延迟。
    2. 消息需要等待前端回复收到。

    目前：没有业务使用
    """

    if not ws:
        return None, None

    wait = Event()
    res = {}
    error = None
    base_msg = BaseMsg(
        channel="flow", key="tools", uuid="$root$", send_uuid="$executor$", data={tool: tool_value}
    ).init()

    def callback(watch_msg: BaseMsg = None, e: Exception = None):
        nonlocal wait, res, error
        if watch_msg:
            logger.debug("info {}".format(watch_msg))
            res = watch_msg.data
        if e:
            # 超时也会继续执行
            logger.error("error: res {}".format(e))
            error = e
        wait.set()

    ws.send_reply(base_msg, time_out_ws, callback)
    wait.wait()
    return res, error
