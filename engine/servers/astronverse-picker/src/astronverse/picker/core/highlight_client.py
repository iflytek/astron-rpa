import json
import socket
from astronverse.picker import Rect
from astronverse.picker.logger import logger


class HighLightClient:
    """使用高亮的门面对象-客户端对象"""

    def __init__(self, port=11001):
        self.__socket_port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 退出前先隐藏高亮
        try:
            self.hide_wnd()
        except Exception as e:
            logger.info(f"隐藏高亮出现异常{e}")

    def __send__(self, message):
        self.__socket.sendto(message.encode("utf-8"), ("localhost", self.__socket_port))

    def start_wnd(self, draw_type="normal"):
        template = {"Operation": "start", "Type": draw_type}
        self.__send__(json.dumps(template))

    def hide_wnd(self):
        template = {"Operation": "initialize", "Type": "ESC"}
        self.__send__(json.dumps(template))

    def draw_wnd(self, rects: Rect, msgs="", draw_type="picking"):
        template = {
            "Operation": draw_type,
            "Boxes": [],
            "Type": None,
        }
        if isinstance(rects, list):
            # 处理一下没有msg输入或msg比较少的情况
            if msgs == "":
                msgs = [""] * len(rects)
            if len(msgs) < len(rects):
                msgs = msgs + [""] * (len(rects) - len(msgs))

            for index in range(len(rects)):
                box_info = {
                    "Left": rects[index].left,
                    "Top": rects[index].top,
                    "Right": rects[index].right,
                    "Bottom": rects[index].bottom,
                    "Msg": msgs[index],
                }
                template["Boxes"].append(box_info)
        else:
            box_info = {
                "Left": rects.left,
                "Top": rects.top,
                "Right": rects.right,
                "Bottom": rects.bottom,
                "Msg": msgs,
            }
            template["Boxes"].append(box_info)
        self.__send__(json.dumps(template))


highlight_client = HighLightClient()
