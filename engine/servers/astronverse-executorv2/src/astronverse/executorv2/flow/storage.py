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
    def process_list(self, project_id: str, mode: str) -> list:
        """获取工程的流程列表"""
        pass

    @abstractmethod
    def process_json(self, project_id: str, process_id: str, mode: str) -> list:
        """获取流程json"""
        pass

    @abstractmethod
    def process_param_list(self, project_id: str, process_id: str, mode: str) -> list:
        """获取工程的配置参数"""
        pass

    @abstractmethod
    def module_detail(self, project_id: str, module_id: str, mode: str) -> str:
        """获取脚本数据"""
        pass

    @abstractmethod
    def global_list(self, project_id: str, mode: str) -> list:
        """获取工程的全局变量"""
        pass

    @abstractmethod
    def element_detail(self, project_id: str, element_id: str, mode: str) -> dict:
        """获取工程的元素数据详情"""
        pass

    @abstractmethod
    def user_pip_list(self, project_id: str, mode: str) -> list:
        """获取工程的用户pip依赖详情"""
        pass

    @abstractmethod
    def get_remote_var_key(self) -> str:
        """获取远程参数的加密密钥"""
        pass

    @abstractmethod
    def get_remote_var_value(self, key: str) -> dict:
        """获取远程参数值"""
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

        res = self.__http__("/api/robot/atom/getByVersionList", None, {
            "atomList": atom_list,
        })
        return res

    def process_list(self, project_id: str, mode: str) -> list:
        """获取工程的流程列表"""
        return self.__http__("/api/robot/module/processModuleList", None, {
            "robotId": project_id,
            "mode": mode
        })

    def process_json(self, project_id: str, process_id: str, mode: str) -> list:
        """获取流程json"""

        # 获取最简化的流程数据
        res = self.__http__("/api/robot/process/process-json", None, {
            "robotId": project_id,
            "processId": process_id,
            "mode": mode,
        })
        try:
            flow_list = json.loads(res)
        except Exception as e:
            raise BaseException(PROCESS_ACCESS_ERROR_FORMAT.format(process_id), "工程数据异常 {}".format(e))

        # 获取公共数据
        atom_list = {}
        for flow in flow_list:
            atom_list["{}-{}".format(flow.get("key"), flow.get("version"))] = {
                "key": flow.get("key"),
                "version": flow.get("version")
            }
        full = self.__process_json_full__(list(atom_list.values()))
        full_dict = {}
        for f in full:
            if f:
                f = json.loads(f)
            f["inputList"] = f.get("inputList", []) + common_advanced
            full_dict["{}-{}".format(f.get("key"), f.get("version"))] = f

        # 合并成需要的流程数据
        for k, flow in enumerate(flow_list):
            if "{}-{}".format(flow.get("key"), flow.get("version")) in full_dict:
                full_item = full_dict["{}-{}".format(flow.get("key"), flow.get("version"))]
                flow_list[k] = merge_dicts(flow, full_item)
        return flow_list

    def module_detail(self, project_id: str, module_id: str, mode: str) -> str:
        res = self.__http__("/api/robot/module/open", None, {
            "robotId": project_id,
            "moduleId": module_id,
            "mode": mode,
        })
        if res:
            return res.get("moduleContent", "")

    def process_param_list(self, project_id: str, process_id: str, mode: str) -> list:
        """运行参数列表"""

        res = self.__http__("/api/robot/param/all", None, {
            "robotId": project_id,
            "processId": process_id,
            "mode": mode,
        })
        if res and isinstance(res, str):
            res = json.loads(res)
        return res

    def global_list(self, project_id: str, mode: str) -> list:
        """获取工程的全局变量"""

        return self.__http__("/api/robot/global/all", {
            "robotId": project_id,
            "mode": mode
        }, None)

    def user_pip_list(self, project_id: str, mode: str) -> list:
        res = self.__http__("/api/robot/require/list", None, {
            "robotId": project_id,
            "mode": mode,
        })
        return res

    def get_remote_var_key(self) -> str:
        res = self.__http__("/api/robot/robot-shared-var/shared-var-key", None, None, "get")
        if res:
            return res.get("key", "")

    def element_detail(self, project_id: str, element_id: str, mode: str) -> dict:
        """获取工程的元素数据详情"""
        res = self.__http__("/api/robot/element/detail", {
            "robotId": project_id,
            "elementId": element_id,
            "mode": mode,
        }, None)
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

    def get_remote_var_value(self, key: str) -> dict:
        res = self.__http__("/api/robot/robot-shared-var/get-batch-shared-var", None, {"ids": [key]}, "post")
        if res and len(res) > 0:
            return res[0]
