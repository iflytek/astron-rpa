from enum import Enum
from typing import Optional
from astronverse.picker import IElement, Point, Rect, PickerDomain, PickerType
from astronverse.picker.logger import logger
from astronverse.picker.engines.smart_component.utils import parse_html
from astronverse.picker.utils.cv import screenshot
from astronverse.picker import APP
import json
from astronverse.picker.utils.browser import Browser
from astronverse.picker.utils.process import get_process_name


class WEBElement(IElement):
    def __init__(self, web_info: dict, left_top_point: Point, app: APP, root_path=None):
        self.web_info = web_info
        self.left_top_point = left_top_point
        self.app = app
        self.root_path = root_path

        self.__rect = None  # 缓存 rect

    def rect(self) -> Rect:
        if self.__rect is None:
            rect = self.web_info["rect"]
            self.__rect = Rect(
                rect["x"] + self.left_top_point.x,
                rect["y"] + self.left_top_point.y,
                rect["right"] + self.left_top_point.x,
                rect["bottom"] + self.left_top_point.y,
            )
        return self.__rect

    def tag(self) -> str:
        return self.web_info.get("tag", "")

    def path(self, svc=None, strategy_svc=None) -> dict:
        res = {
            "version": "1",
            "type": PickerDomain.WEB.value,
            "app": self.app.value,
            "path": self.web_info,
            "img": {"self": screenshot(self.rect())},
            "uiapath": [self.root_path],
        }
        pick_type = strategy_svc.data.get("pick_type")
        if pick_type == PickerType.SIMILAR:
            similar_path = WEBPicker.get_similar_path(svc.route_port, strategy_svc)
            if similar_path:
                res["path"] = similar_path
                res["img"]["self"] = strategy_svc.data.get("data", {}).get("img", {}).get("self", "")
        if pick_type == PickerType.BATCH:
            batch_path = WEBPicker.get_batch_path(svc.route_port, strategy_svc, self)
            if batch_path:
                res["path"] = batch_path
        return res


class BizCode(Enum):
    OK = "0000"
    ServerErr = "5001"
    ElemErr = "5002"
    ExecErr = "5003"


class WEBPicker:
    pre_xpath = None

    @classmethod
    def get_similar_path(cls, route_port, strategy_svc) -> Optional[dict]:
        raise Exception("智能组件的相似拾取暂未实现")

    @classmethod
    def get_batch_path(cls, route_port, strategy_svc, curr_ele: "WEBElement") -> Optional[dict]:
        raise Exception("智能组件的批量抓取暂未实现")

    @classmethod
    def get_element(
        cls, root_control, route_port, strategy_svc, left_top_point: Point, **kwargs
    ) -> Optional[WEBElement]:
        web_info = Browser.send_browser_extension(
            browser_type=strategy_svc.app.value,
            data={"x": strategy_svc.last_point.x - left_top_point.x, "y": strategy_svc.last_point.y - left_top_point.y},
            key="getOuterHTML",
            gate_way_port=route_port,
        )
        if not web_info:
            return None

        WEBPicker.pre_xpath = web_info.get("abXpath", "")
        # 处理html
        web_info["outerHTML"] = parse_html(web_info["outerHTML"])

        pid = root_control.ProcessId
        app_name = get_process_name(pid)

        prev_control = None  # 用于保存根节点的子节点
        # 向上遍历直到根节点
        while True:
            parent = root_control.GetParentControl()
            if not parent:
                break
            prev_control = root_control  # 保存当前节点，作为根节点的子节点
            root_control = parent  # 向上移动

        root_control = prev_control

        root_path = {
            "cls": root_control.ClassName,
            "name": root_control.Name,
            "app": app_name,
            "tag_name": "WindowControl",
            "checked": True,
        }
        return WEBElement(web_info=web_info, left_top_point=left_top_point, app=strategy_svc.app, root_path=root_path)

    @classmethod
    def getParentElement(cls, root_control, route_port, strategy_svc, left_top_point: Point, **kwargs):
        url = "http://127.0.0.1:{}/browser_connector/browser/transition".format(route_port)
        data_str = strategy_svc.data.get("data", "{}")
        data_dict = json.loads(data_str) if isinstance(data_str, str) else data_str
        path = data_dict.get("path", {})
        logger.info(f"getParentElement left_top_point: {left_top_point.x},{left_top_point.y}")

        web_info = Browser.send_browser_extension(
            browser_type=strategy_svc.app.value, data=path, key="getParentElement", gate_way_port=route_port
        )

        # 处理html
        web_info["outerHTML"] = parse_html(web_info["outerHTML"])

        pid = root_control.ProcessId
        app_name = get_process_name(pid)

        prev_control = None  # 用于保存根节点的子节点
        # 向上遍历直到根节点
        while True:
            parent = root_control.GetParentControl()
            if not parent:
                break
            prev_control = root_control  # 保存当前节点，作为根节点的子节点
            root_control = parent  # 向上移动

        root_control = prev_control

        root_path = {
            "cls": root_control.ClassName,
            "name": root_control.Name,
            "app": app_name,
            "tag_name": "WindowControl",
            "checked": True,
        }
        return WEBElement(web_info=web_info, left_top_point=left_top_point, app=strategy_svc.app, root_path=root_path)

    @classmethod
    def getChildElement(cls, root_control, route_port, strategy_svc, left_top_point: Point, **kwargs):
        logger.info(f"getChildElement left_top_point: {left_top_point.x},{left_top_point.y}")
        data_str = strategy_svc.data.get("data", "{}")
        data_dict = json.loads(data_str) if isinstance(data_str, str) else data_str
        path = data_dict.get("path", {})

        web_info = Browser.send_browser_extension(
            browser_type=strategy_svc.app.value,
            data={**path, "originXpath": WEBPicker.pre_xpath},
            key="getChildElement",
            gate_way_port=route_port,
        )

        # 处理html
        web_info["outerHTML"] = parse_html(web_info["outerHTML"])

        pid = root_control.ProcessId
        app_name = get_process_name(pid)

        prev_control = None  # 用于保存根节点的子节点
        # 向上遍历直到根节点
        while True:
            parent = root_control.GetParentControl()
            if not parent:
                break
            prev_control = root_control  # 保存当前节点，作为根节点的子节点
            root_control = parent  # 向上移动

        root_control = prev_control

        root_path = {
            "cls": root_control.ClassName,
            "name": root_control.Name,
            "app": app_name,
            "tag_name": "WindowControl",
            "checked": True,
        }
        return WEBElement(web_info=web_info, left_top_point=left_top_point, app=strategy_svc.app, root_path=root_path)


web_picker_smart_component = WEBPicker()
