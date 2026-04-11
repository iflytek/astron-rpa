import json
import os
from typing import Any, Dict, List

import yaml


class TreeNode:
    """树节点"""

    def __init__(self, key: str, title: str = "", icon: str = ""):
        self.key = key
        self.title = title
        self.icon = icon
        self.atomics = []
        self.children = {}

    def add_atomic(self, atomic_data: Dict[str, Any]):
        """添加原子能力"""
        self.atomics.append(
            {
                "key": atomic_data.get("key", ""),
                "title": atomic_data.get("title", ""),
                "icon": atomic_data.get("icon", ""),
            }
        )

    def add_child(self, key: str, node: "TreeNode"):
        """添加子节点"""
        self.children[key] = node

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，叶子节点排在子树节点之前"""
        # 排序 self.atomics，如果是原子能力，不包含子节点， 则排在子树节点之前
        atomics = list(self.atomics)
        for child in self.children.values():
            atomics.append(child.to_dict())

        result = {"key": self.key, "title": self.title, "icon": self.icon, "atomics": atomics}
        return result


class TreeManager:
    """树形结构管理器，用于生成 tree.json"""

    def __init__(self):
        self.root_nodes = {}
        self.node_config = {}

    def load_node_config_from_yaml(self, yaml_file: str):
        """
        从 YAML 文件加载节点配置

        Args:
            yaml_file: YAML 配置文件路径
        """
        if not os.path.exists(yaml_file):
            return

        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data and "nodes" in data:
            self.node_config = data["nodes"]

    def load_node_config_from_frame_json(self, json_file: str):
        """
        从 tree_frame.json 加载节点配置（树骨架格式）

        Args:
            json_file: tree_frame.json 文件路径
        """
        if not os.path.exists(json_file):
            return

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        config = {}

        def walk(nodes: list, parent_path: str):
            for node in nodes:
                key = node.get("key", "")
                if not key:
                    continue
                path = f"{parent_path}/{key}"
                config[path] = {"title": node.get("title", key), "icon": node.get("icon", "")}
                children = node.get("atomics", [])
                if children:
                    walk(children, path)

        if "atomicTree" in data:
            walk(data["atomicTree"], "/atomicTree")
        if "atomicTreeExtend" in data:
            walk(data["atomicTreeExtend"], "/atomicTreeExtend")

        self.node_config = config

    def set_node_config(self, config: Dict[str, Dict[str, str]]):
        """
        设置节点配置

        Args:
            config: 节点配置字典，格式为:
                {
                    "/web": {"title": "网页自动化", "icon": "web-automation"},
                    "/web/cookie": {"title": "Cookie", "icon": "cookie"}
                }
        """
        self.node_config = config

    def _parse_path(self, path: str) -> List[str]:
        """
        解析路径为层级列表

        Args:
            path: 路径字符串，如 "/web/cookie"

        Returns:
            层级列表，如 ["web", "cookie"]
        """
        if not path or path == "/":
            return []

        # 去除开头的 / 并分割
        parts = path.strip("/").split("/")
        return [p for p in parts if p]

    def _get_or_create_node(self, path: str) -> TreeNode:
        """
        获取或创建节点

        Args:
            path: 完整路径，如 "/web" 或 "/web/cookie"

        Returns:
            TreeNode 实例
        """
        parts = self._parse_path(path)
        if not parts:
            return None

        # 获取节点配置
        node_info = self.node_config.get(path, {})
        key = parts[-1]
        title = node_info.get("title", key)
        icon = node_info.get("icon", "")
        # 如果是根节点
        if len(parts) == 1:
            if key not in self.root_nodes:
                self.root_nodes[key] = TreeNode(key, title, icon)
            return self.root_nodes[key]

        # 递归获取或创建父节点
        parent_path = "/" + "/".join(parts[:-1])
        parent_node = self._get_or_create_node(parent_path)

        # 获取或创建当前节点
        if key not in parent_node.children:
            parent_node.add_child(key, TreeNode(key, title, icon))

        return parent_node.children[key]

    def add_atomic_from_config(self, atomic_key: str, atomic_meta: Dict[str, Any], config_data: Dict[str, Any]):
        """
        从配置添加原子能力

        Args:
            atomic_key: 原子能力的 key
            atomic_meta: 原子能力的元数据（从 meta.json）
            config_data: 配置数据（从 config.yaml）
        """
        # 获取 path 配置
        path_list = config_data.get("path", [])

        if not path_list:
            # 如果没有配置 path，默认放到 /atomicTreeExtend/local
            path_list = ["/atomicTreeExtend/local"]

        # 准备原子能力数据
        atomic_data = {
            "key": atomic_key,
            "title": config_data.get("title", atomic_meta.get("title", "")),
            "icon": config_data.get("icon", atomic_meta.get("icon", "")),
        }

        # 添加到每个路径
        for path in path_list:
            if not path:
                continue

            node = self._get_or_create_node(path)
            if node:
                node.add_atomic(atomic_data)

    def build_from_meta_and_config(self, meta_file: str = "meta.json", config_file: str = "config.yaml"):
        """
        从 meta.json 和 config.yaml 构建树

        Args:
            meta_file: meta.json 文件路径
            config_file: config.yaml 文件路径
        """
        # 读取 meta.json
        if not os.path.exists(meta_file):
            raise FileNotFoundError(f"meta.json not found: {meta_file}")

        with open(meta_file, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

        # 读取 config.yaml
        from astronverse.actionlib.config import config

        config.set_config_file(config_file)

        # 遍历所有原子能力
        for atomic_key, atomic_meta in meta_data.items():
            # 获取配置
            config_data_dict = config.get("atomic", atomic_key)
            if not config_data_dict:
                continue

            self.add_atomic_from_config(atomic_key, atomic_meta, config_data_dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，根据 path 中的根节点名称区分 atomicTree 和 atomicTreeExtend"""
        atomic_tree = []
        atomic_tree_extend = []

        # root_nodes 的 key 为路径第一段，即 "atomicTree" 或 "atomicTreeExtend"
        tree_node = self.root_nodes.get("atomicTree")
        extend_node = self.root_nodes.get("atomicTreeExtend")

        if tree_node:
            for child_node in tree_node.children.values():
                atomic_tree.append(child_node.to_dict())

        if extend_node:
            for child_node in extend_node.children.values():
                atomic_tree_extend.append(child_node.to_dict())

        result = {"atomicTree": atomic_tree}
        if atomic_tree_extend:
            result["atomicTreeExtend"] = atomic_tree_extend

        return result

    def json(self) -> str:
        """生成 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def meta(self, output_file: str = "tree.json") -> str:
        """
        生成 tree.json 文件

        Args:
            output_file: 输出文件路径

        Returns:
            输出文件路径
        """
        data = self.json()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(data)
        return output_file


# 全局实例
treeMg = TreeManager()
