import base64
import json
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Optional
import requests
from astronverse.executorv2.error import *
from astronverse.executorv2.logger import logger

common_advanced = [
    {
        "key": "__res_print__",
        "types": "Bool",
        "title": "打印输出变量值",
        "name": "__res_print__",
    },
    {
        "key": "__delay_before__",
        "types": "Float",
        "title": "执行前延迟(秒)",
        "name": "__delay_before__",
    },
    {
        "key": "__delay_after__",
        "types": "Float",
        "title": "执行后延迟(秒)",
        "name": "__delay_after__",
    },
    {
        "key": "__skip_err__",
        "types": "Str",
        "title": "执行异常时",
        "name": "__skip_err__",
    },
    {
        "key": "__retry_time__",
        "types": "Int",
        "title": "重试次数(次)",
        "name": "__retry_time__",
    },
    {
        "key": "__retry_interval__",
        "types": "Float",
        "title": "重试间隔(秒)",
        "name": "__retry_interval__",
    }
]


def merge_dicts(flow, full_flow):
    keep_level_1 = ["title", "src"]
    keep_level_2 = ["inputList", "outputList"]
    keep_level_3 = ["types", "title", "name", "need_parse", "show"]

    flow["inputList"] = flow.get("inputList", []) + flow.get("advanced", []) + flow.get("exception", [])
    flow["advanced"] = flow["exception"] = []
    del flow["advanced"]
    del flow["exception"]

    def merge_obj(keep_list: list, c1: dict, c2: dict):
        for k in keep_list:
            if k in c2:
                c1[k] = c2[k]

    merge_obj(keep_level_1, flow, full_flow)

    for v in keep_level_2:
        if v in flow:
            full_flow_dict = {}
            for v2 in full_flow.get(v, []):
                full_flow_dict[v2.get("key", "")] = v2
            for v3 in flow.get(v):
                if v3.get("key", "") and v3.get("key") in full_flow_dict:
                    merge_obj(keep_level_3, v3, full_flow_dict[v3.get("key")])
    return flow


class IStorage(ABC):

    @abstractmethod
    def process_list(self, project_id: str, mode: str, version: str) -> list:
        """获取工程的流程列表"""
        pass

    @abstractmethod
    def process_detail(self, project_id: str, mode: str, version: str, process_id: str) -> list:
        """获取流程json"""
        pass

    @abstractmethod
    def module_detail(self, project_id: str, mode: str, version: str, module_id: str) -> str:
        """获取脚本数据"""
        pass

    @abstractmethod
    def param_list(self, project_id: str, mode: str, version: str, process_id: str) -> list:
        """获取工程的配置参数"""
        pass

    @abstractmethod
    def global_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的全局变量"""
        pass

    @abstractmethod
    def pip_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的用户pip依赖详情"""
        pass

    @abstractmethod
    def element_detail(self, project_id: str, mode: str, version: str, element_id: str) -> dict:
        """获取工程的元素数据详情"""
        pass


class HttpStorage(IStorage):

    def __init__(self, svc):
        self.svc = svc
        self.gateway_port = svc.gateway_port

    def __http__(self, shot_url: str, params: Optional[dict], data: Optional[dict], meta: str = "post") -> Any:
        """ post 请求 """
        logger.debug("请求开始 {}:{}:{}".format(shot_url, params, data))

        if meta == "post":
            response = requests.post("http://127.0.0.1:{}{}".format(self.gateway_port, shot_url), json=data, params=params)
        else:
            response = requests.get("http://127.0.0.1:{}{}".format(self.gateway_port, shot_url), params=params)
        if response.status_code != 200:
            raise BaseException(SERVER_ERROR_FORMAT.format(response.status_code), "服务器错误{}".format(response.status_code))

        logger.debug("请求结束 {}:{}".format(shot_url, response.status_code))

        try:
            json_data = response.json()
        except JSONDecodeError:
            base64_encoded_data = base64.b64encode(response.content).decode('utf-8')
            return base64_encoded_data
        if json_data.get("code") != "0000" and json_data.get("code") != "000000":
            msg = json_data.get("message", "")
            raise BaseException(SERVER_ERROR_FORMAT.format(msg), "服务器错误{}".format(json_data))
        return json_data.get("data", {})

    def __process_json_full__(self, atom_list: list) -> list:
        if len(atom_list) == 0:
            return []

        res = self.__http__("/api/robot/atom/getLatestAtomsByList", None, {
            "atomKeyList": atom_list,
        })
        return res

    def process_list(self, project_id: str, mode: str, version: str) -> list:
        """获取工程的流程列表"""

        data = {
            "robotId": project_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        return self.__http__("/api/robot/module/processModuleList", None, data)

    def process_detail(self, project_id: str, mode: str, version: str, process_id: str) -> list:
        """获取流程json"""

        # 基础数据
        data = {
            "robotId": project_id,
            "processId": process_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        res = self.__http__("/api/robot/process/process-json", None, data)
        try:
            flow_list = json.loads(res)
        except Exception as e:
            raise BaseException(PROCESS_ACCESS_ERROR_FORMAT.format(process_id), "工程数据异常 {}".format(e))

        # 附加数据
        atom_key_list = []
        for flow in flow_list:
            atom_key_list.append(flow.get("key"))
        full = self.__process_json_full__(atom_key_list)
        full_dict = {}
        for f in full:
            if f:
                f = json.loads(f.get("atomContent"))
            f["inputList"] = f.get("inputList", []) + common_advanced
            full_dict[f.get("key")] = f

        # 合并
        for k, flow in enumerate(flow_list):
            if flow.get("key") in full_dict:
                full_item = full_dict[flow.get("key")]
                flow_list[k] = merge_dicts(flow, full_item)
        return flow_list

    def module_detail(self, project_id: str, mode: str, version: str, module_id: str) -> str:

        data = {
            "robotId": project_id,
            "moduleId": module_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        res = self.__http__("/api/robot/module/open", None, data)
        if res:
            return res.get("moduleContent", "")
        else:
            return ""

    def param_list(self, project_id: str, mode: str, version: str, process_id: str) -> list:
        """运行参数列表"""

        data = {
            "robotId": project_id,
            "processId": process_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        res = self.__http__("/api/robot/param/all", None, data)
        if res and isinstance(res, str):
            res = json.loads(res)
        return res

    def global_list(self, project_id: str, mode: str, version: str = "") -> list:
        """获取工程的全局变量"""

        params = {
            "robotId": project_id,
        }
        if mode:
            params["mode"] = mode
        if version:
            params["robotVersion"] = int(version)

        return self.__http__("/api/robot/global/all", params, None)

    def pip_list(self, project_id: str, mode: str, version: str = "") -> list:
        data = {
            "robotId": project_id,
        }
        if mode:
            data["mode"] = mode
        if version:
            data["robotVersion"] = int(version)

        return self.__http__("/api/robot/require/list", None, data)

    def element_detail(self, project_id: str, mode: str, version: str, element_id: str) -> dict:
        """获取工程的元素数据详情"""

        params = {
            "robotId": project_id,
            "elementId": element_id,
        }
        if mode:
            params["mode"] = mode
        if version:
            params["robotVersion"] = int(version)
        res = self.__http__("/api/robot/element/detail", params, None)
        if not res:
            raise BaseException(ELEMENT_ACCESS_ERROR_FORMAT.format(element_id), "元素获取异常为空")

        # 处理元素的图片URL，将其转为base64编码保存到elementData中
        if res.get("imageUrl") or res.get("parentImageUrl"):
            element_data = json.loads(res.get("elementData"))
            if element_data.get("type") == "cv":
                image_url = res.get("imageUrl", "")
                parent_image_url = res.get("parentImageUrl")
                if not image_url.endswith("fileId="):
                    image_base64 = self.__http__(image_url, None, None, "get")
                else:
                    image_base64 = ""
                if parent_image_url and not parent_image_url.endswith("fileId="):
                    parent_image_base64 = self.__http__(parent_image_url, None, None, "get")
                else:
                    parent_image_base64 = ""
                element_data["img"]["self"] = image_base64
                element_data["img"]["parent"] = parent_image_base64
                res.update({"elementData": json.dumps(element_data, ensure_ascii=False)})
        return res

