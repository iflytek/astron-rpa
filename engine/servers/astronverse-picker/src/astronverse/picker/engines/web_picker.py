from typing import Optional

import requests as requests
from astronverse.baseline.error.error import BizCode
from astronverse.picker import APP, IElement, PickerDomain, PickerType, Point, Rect
from astronverse.picker.logger import logger
from astronverse.picker.utils.cv import screenshot
from astronverse.picker.utils.process import get_process_name
from astronverse.picker.utils.browser import Browser


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
            left = rect["x"] + self.left_top_point.x
            top = rect["y"] + self.left_top_point.y
            right = rect["right"] + self.left_top_point.x
            bottom = rect["bottom"] + self.left_top_point.y
            self.__rect = Rect(left, top, right, bottom)
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
                data_dict = strategy_svc.data.get("data", {})
                img_dict = data_dict.get("img", {})
                res["img"]["self"] = img_dict.get("self", "")
        if pick_type == PickerType.BATCH:
            batch_path = WEBPicker.get_batch_path(svc.route_port, strategy_svc, self)
            if batch_path:
                res["path"] = batch_path
        return res


class WEBPicker:
    @classmethod
    def get_similar_path(cls, route_port: int, strategy_svc) -> Optional[dict]:
        web_info = Browser.send_browser_extension(
            browser_type=strategy_svc.app.value,
            data=strategy_svc.data.get("data", {}).get("path", []),
            key="similarElement",
            gate_way_port=route_port,
        )
        return web_info

    @classmethod
    def get_batch_path(cls, route_port, strategy_svc, curr_ele: "WEBElement") -> Optional[dict]:
        try:
            # 表头抓取
            batch_type = strategy_svc.data.get("data", {}).get("path", {}).get("batchType")
            if batch_type == "head":
                web_info = Browser.send_browser_extension(
                    browser_type=strategy_svc.app.value,
                    data=curr_ele.web_info,
                    key="tableHeaderBatch",
                    gate_way_port=route_port,
                    timeout=3,
                )
                return web_info
            # 补充相似元素
            if batch_type == "similarAdd":
                web_info = Browser.send_browser_extension(
                    browser_type=strategy_svc.app.value,
                    data=strategy_svc.data.get("data", {}).get("path"),
                    key="similarBatch",
                    gate_way_port=route_port,
                    timeout=3,
                )

                return web_info
            # 是否是表格
            res_data = Browser.send_browser_extension(
                browser_type=strategy_svc.app.value,
                data=curr_ele.web_info,
                key="elementIsTable",
                gate_way_port=route_port,
                timeout=3,
            )
            is_table = res_data.get("isTable")
            # is_table = True 直接抓取两种元素， False 继续执行
            if is_table and batch_type != "similar":  # 表格元素且不以相似元素拾取
                tdb_response = Browser.send_browser_extension(
                    browser_type=strategy_svc.app.value,
                    data=res_data,
                    key="tableDataBatch",
                    gate_way_port=route_port,
                    timeout=3,
                )

                ###
                tcdb_response = Browser.send_browser_extension(
                    browser_type=strategy_svc.app.value,
                    data=res_data,
                    key="tableColumnDataBatch",
                    gate_way_port=route_port,
                    timeout=3,
                )
                # 整合两种数据
                table_res_data = {"isTable": is_table, "tableData": tdb_response, "tableColumnData": tcdb_response}
                return table_res_data
            else:  # 普通元素
                web_info = Browser.send_browser_extension(
                    browser_type=strategy_svc.app.value,
                    data=res_data,
                    key="similarBatch",
                    gate_way_port=route_port,
                    timeout=3,
                )
                return web_info
        except Exception as e:
            raise Exception("插件响应出错", e)

    @classmethod
    def get_element(
        cls, root_control, route_port, strategy_svc, left_top_point: Point, **kwargs
    ) -> Optional[WEBElement]:
        web_info = Browser.send_browser_extension(
            browser_type=strategy_svc.app.value,
            data={"x": strategy_svc.last_point.x - left_top_point.x, "y": strategy_svc.last_point.y - left_top_point.y},
            key="getElement",
            gate_way_port=route_port,
        )
        if not web_info:
            return None

        return WEBElement(
            web_info=web_info,
            left_top_point=left_top_point,
            app=strategy_svc.app,
            root_path=None,
        )


web_picker = WEBPicker()
