import base64
import json
import os
from urllib.parse import urlparse, parse_qs
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Optional
import requests
from astronverse.actionlib.logger import logger


class Storage(ABC):
    @abstractmethod
    def element_detail(self, project_id: str, element_id: str, mode: str, version: str = "") -> dict:
        """Get element detail data for a project"""
        pass

    @abstractmethod
    def element_vision_detail(self, url: str) -> str:
        """Get element image (base64 string) by URL"""
        pass


class StorageCache:
    def __init__(self, base_dir: str = "resource", resource_cache: bool = True):
        self.base_dir = base_dir
        self.resource_cache = resource_cache
        self.memory = {}
        self.resource_type_conf = {
            "element": {"file_ext": "json", "binary": False},
            "image": {"file_ext": "png", "binary": True},
        }

    def get(self, resource_type: str, resource_id: str) -> Optional[Any]:
        if resource_type not in self.resource_type_conf:
            raise Exception("Resource type does not exist: {}".format(resource_type))
        conf = self.resource_type_conf[resource_type]
        if resource_type not in self.memory:
            self.memory[resource_type] = {}

        data = self.memory.get(resource_type, {}).get(resource_id, None)
        if data is not None:
            return data

        local_data_path = os.path.join(self.base_dir, resource_type, "{}.{}".format(resource_id, conf.get("file_ext")))
        if self.resource_cache and os.path.exists(local_data_path):
            if conf.get("binary"):
                with open(local_data_path, "rb") as f:
                    raw_bytes = f.read()
                data = base64.b64encode(raw_bytes).decode("utf-8")
            else:
                with open(local_data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            self.memory[resource_type][resource_id] = data
            return data

        return None

    def set(self, resource_type: str, resource_id: str, data: Any):
        if resource_type not in self.resource_type_conf:
            raise Exception("Resource type does not exist: {}".format(resource_type))
        conf = self.resource_type_conf[resource_type]
        if resource_type not in self.memory:
            self.memory[resource_type] = {}
        dir_path = os.path.join(self.base_dir, resource_type)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        self.memory[resource_type][resource_id] = data
        local_data_path = os.path.join(self.base_dir, resource_type, "{}.{}".format(resource_id, conf.get("file_ext")))
        if self.resource_cache:
            if resource_type == "element":
                with open(local_data_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            elif resource_type == "image":
                binary_bytes = base64.b64decode(data) if isinstance(data, str) else data
                with open(local_data_path, "wb") as f:
                    f.write(binary_bytes)


class HttpStorage(Storage):
    def __init__(self, gateway_port: str = None, mode: str = "EDIT_PAGE"):
        self.gateway_port = gateway_port

        if mode in ["PROJECT_LIST", "EDIT_PAGE"]:
            resource_cache = False
        else:
            resource_cache = True
        self.cache_manager = StorageCache(resource_cache=resource_cache)

    def __http__(self, shot_url: str, params: Optional[dict], data: Optional[dict], meta: str = "post") -> Any:
        """HTTP request helper"""
        cookies = {}
        logger.debug("Request start {}:{}:{}".format(shot_url, params, data))
        if meta == "post":
            response = requests.post(
                "http://127.0.0.1:{}{}".format(self.gateway_port, shot_url), json=data, cookies=cookies, params=params
            )
        else:
            response = requests.get(
                "http://127.0.0.1:{}{}".format(self.gateway_port, shot_url), cookies=cookies, params=params
            )
        if response.status_code != 200:
            raise Exception("Server error: HTTP {}".format(response.status_code))
        try:
            json_data = response.json()
            logger.debug("Request end {}:{}".format(shot_url, json_data))
            if json_data.get("code") != "000000":
                msg = json_data.get("message", "")
                raise Exception("Server error: {}".format(msg or json_data))
            return json_data.get("data", {})
        except JSONDecodeError:
            base64_encoded_data = base64.b64encode(response.content).decode("utf-8")
            return base64_encoded_data

    def element_detail(self, project_id: str, element_id: str, mode: str, version: str = "") -> dict:
        """Get element detail data for a project"""

        res = self.cache_manager.get("element", element_id)
        if res is not None:
            return res

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
            raise Exception("Failed to get element data for {}: empty response".format(element_id))

        element_data = json.loads(res.get("elementData"))
        if not element_data.get("img"):
            element_data["img"] = {"self": "", "parent": ""}
        if element_data.get("type") == "cv":
            element_data["img"]["self"] = self.element_vision_detail(res.get("imageUrl"))
            element_data["img"]["parent"] = self.element_vision_detail(res.get("parentImageUrl"))
        res.update({"elementData": element_data})
        self.cache_manager.set("element", element_id, res)
        return res

    def element_vision_detail(self, url: str) -> str:
        """Get element image (base64 string) by URL"""
        if not url:
            return ""
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        img_id = qs.get("fileId", [None])[0]

        res = self.cache_manager.get("image", img_id)
        if res is not None:
            return res

        res = self.__http__(url, None, None, "get") or ""

        self.cache_manager.set("image", img_id, res)
        return res
