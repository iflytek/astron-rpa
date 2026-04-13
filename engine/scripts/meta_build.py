import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Directory constants
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
COMPONENTS_DIR = Path(CURRENT_DIR.parent, "components").resolve()

# Components to skip during meta build
SKIPPED_COMPONENTS = ["astronverse-database"]

# Output file paths
LOCAL_META_FILE = os.path.join(CURRENT_DIR, "temp_local_meta.json")
LOCAL_TREE_FILE = os.path.join(CURRENT_DIR, "temp_local_tree.json")
BASE_META_FILE = os.path.join(PROJECT_ROOT, "resources/meta/base_meta.json")
BASE_TREE_FILE = os.path.join(PROJECT_ROOT, "resources/meta/tree_frame.json")
MERGED_META_FILE = os.path.join(PROJECT_ROOT, "resources/meta/meta.json")
MERGED_TREE_FILE = os.path.join(PROJECT_ROOT, "resources/meta/tree.json")


def color_log(text, color_code):
    """Print colored text in the terminal."""
    print(f"\033[{color_code}m{text}\033[0m")


class LocalManager:
    def __init__(self, components_dir, skipped_components=None):
        self.components_dir = components_dir
        self.skipped = set(skipped_components or [])
        self.failed_folders = set()
        self.folders = [
            f for f in os.listdir(components_dir)
            if os.path.isdir(os.path.join(components_dir, f)) and f not in self.skipped
        ]
        self.selected_folders = self.folders.copy()

    def select_folders(self):
        """Prompt user to select which component folders to include in the meta build process."""
        selected = input("Enter the package number to build: ").strip()
        try:
            selected_idx = int(selected) - 1
            if 0 <= selected_idx < len(self.folders):
                self.selected_folders = [self.folders[selected_idx]]
            else:
                color_log("Invalid selection. Please select a valid package number.", "31")
        except (ValueError, IndexError):
            color_log("Invalid input. Please select one package.", "31")

    def run_meta_scripts(self):
        """Run meta.py in each component directory."""
        color_log("Running meta.py scripts ...", "35")
        for folder in self.folders:
            verse_folder = os.path.join(self.components_dir, folder)
            meta_script = os.path.join(verse_folder, "meta.py")
            if not os.path.isfile(meta_script):
                continue

            color_log(f"Running meta.py in {verse_folder}...", "36")
            try:
                subprocess.run([sys.executable, "meta.py"], cwd=verse_folder, check=True)
            except Exception as e:
                self.failed_folders.add(folder)
                color_log(f"Failed to run meta.py in {verse_folder}: {e}", "31")

    def _iter_merge_folders(self):
        return [folder for folder in self.folders if folder not in self.failed_folders]

    def merge_local_meta(self):
        """Aggregate meta.json files from each component directory."""
        color_log("Merging local meta.json files from component directories...", "35")
        result = {}
        for folder in self._iter_merge_folders():
            meta_json_path = os.path.join(self.components_dir, folder, "meta.json")
            if not os.path.isfile(meta_json_path):
                continue
            with open(meta_json_path, encoding="utf-8") as f:
                data = json.load(f)
                result.update(data)
        with open(BASE_META_FILE, encoding="utf-8") as f:
            base_meta = json.load(f)
            result.update(base_meta)  # 基础 meta 放在最后，覆盖组件 meta 中的同名项
        color_log(f"Merged local meta items count: {len(result)}", "32")
        JsonUtils.save_to_file(result, LOCAL_META_FILE)
        return result

    def merge_local_tree(self):
        """Merge tree.json files from component directories with deep merge."""
        color_log("Merging local tree.json files from component directories...", "35")
        merged_tree = {"atomicTree": [], "atomicTreeExtend": []}

        for folder in self._iter_merge_folders():
            tree_json_path = os.path.join(self.components_dir, folder, "tree.json")
            if not os.path.isfile(tree_json_path):
                continue

            with open(tree_json_path, encoding="utf-8") as f:
                data = json.load(f)
                # 深度合并 atomicTree
                merged_tree["atomicTree"] = self._deep_merge_tree_nodes(
                    merged_tree["atomicTree"], data.get("atomicTree", [])
                )
                # 深度合并 atomicTreeExtend
                merged_tree["atomicTreeExtend"] = self._deep_merge_tree_nodes(
                    data.get("atomicTreeExtend", []), merged_tree["atomicTreeExtend"]
                )

        color_log(
            f"Merged local tree nodes count: {len(merged_tree['atomicTree']) + len(merged_tree['atomicTreeExtend'])}",
            "32",
        )
        JsonUtils.save_to_file(merged_tree, LOCAL_TREE_FILE)
        return merged_tree

    def _deep_merge_tree_nodes(self, target_nodes, source_nodes):
        """
        深度合并两个树节点列表
        - 如果节点的 key 相同，递归合并其 atomics 子节点
        - 如果节点只在 source 中存在，直接添加到 target
        - 已存在相同 key 的兄弟节点不再重复添加
        """
        if not source_nodes:
            return target_nodes if target_nodes else []

        # 创建目标节点的 key 到节点的映射（自动对 target 内部去重）
        target_dict = {node.get("key"): node for node in (target_nodes or []) if node.get("key")}

        # 遍历源节点
        for source_node in source_nodes:
            key = source_node.get("key")
            if not key:
                continue

            if key in target_dict:
                # 已存在相同 key 的兄弟节点，递归合并其 atomics 子节点，不重复添加
                target_node = target_dict[key]

                # 合并 atomics 子节点
                if "atomics" in source_node and source_node["atomics"]:
                    if "atomics" not in target_node or not target_node["atomics"]:
                        # 递归去重后赋值，避免 source 内部有重复
                        target_node["atomics"] = self._deep_merge_tree_nodes([], source_node["atomics"])
                    else:
                        # 递归深度合并子节点
                        target_node["atomics"] = self._deep_merge_tree_nodes(
                            target_node["atomics"], source_node["atomics"]
                        )

                # 优先使用 source 的某些字段值
                for field in ["title", "icon", "sort"]:
                    if field in source_node:
                        target_node[field] = source_node[field]
            else:
                # 目标中不存在该节点，构造新节点并递归去重其子节点后添加
                new_node = {k: v for k, v in source_node.items() if k != "atomics"}
                if "atomics" in source_node and source_node["atomics"]:
                    new_node["atomics"] = self._deep_merge_tree_nodes([], source_node["atomics"])
                target_dict[key] = new_node

        # 返回合并后的节点列表，叶子节点（无 atomics 字段）排在子树节点之前
        merged = list(target_dict.values())
        merged.sort(key=lambda node: 0 if "atomics" not in node else 1)
        return merged

    def _deduplicate_tree_nodes(self, nodes):
        """
        辅助方法：对树节点列表进行去重
        如果有相同 key 的节点，保留第一个并合并其子节点
        """
        if not nodes:
            return []

        nodes_dict = {}
        for node in nodes:
            key = node.get("key")
            if not key:
                continue

            if key not in nodes_dict:
                nodes_dict[key] = node
            else:
                # 合并 atomics 子节点
                existing_node = nodes_dict[key]
                if "atomics" in node and node["atomics"]:
                    if "atomics" not in existing_node:
                        existing_node["atomics"] = []
                    existing_node["atomics"].extend(node["atomics"])

        # 递归处理每个节点的子节点
        result = []
        for node in nodes_dict.values():
            if "atomics" in node and node["atomics"]:
                node["atomics"] = self._deduplicate_tree_nodes(node["atomics"])
            result.append(node)

        return result

    def merge_local_types(self):
        """Merge meta_type.json files from component directories."""
        color_log("Merging meta_type.json files from component directories...", "35")
        result = {}
        for folder in self._iter_merge_folders():
            types_json_path = os.path.join(self.components_dir, folder, "meta_type.json")
            if not os.path.isfile(types_json_path):
                continue
            with open(types_json_path, encoding="utf-8") as f:
                data = json.load(f)
                result.update(data)
        return result

    def build_meta_list(self, local_meta) -> list:
        """Build the merged meta list from local meta data."""
        color_log("Building merged meta list from local meta data...", "35")
        merged_meta = []

        for key, value in local_meta.items():
            merged_meta.append({"atomKey": key, "atomContent": json.dumps(value), "sort": None})

        sorted_meta = sorted(merged_meta, key=lambda x: x["atomKey"])
        JsonUtils.save_to_file(sorted_meta, MERGED_META_FILE)
        color_log(f"Merged meta list items count: {len(sorted_meta)}", "32")
        return sorted_meta

    def build_tree_config(self, local_tree, local_types):
        """Build the tree configuration from local tree data."""
        color_log("Building tree configuration from local tree data...", "35")

        merged_tree = {
            "atomicTree": local_tree.get("atomicTree", []).copy(),
            "atomicTreeExtend": local_tree.get("atomicTreeExtend", []).copy(),
            "types": local_types.copy(),
            "commonAdvancedParameter": [],
        }

        with open(BASE_TREE_FILE, encoding="utf-8") as f:
            base_tree = json.load(f)
            # 只合并 types 和 commonAdvancedParameter，树结构完全由组件 path 驱动
            merged_tree["types"].update(base_tree.get("types", {}))
            merged_tree["commonAdvancedParameter"].extend(base_tree.get("commonAdvancedParameter", []))

        JsonUtils.save_to_file(merged_tree, MERGED_TREE_FILE)
        color_log(
            f"Merged tree nodes count: {len(merged_tree['atomicTree']) + len(merged_tree['atomicTreeExtend'])}", "32"
        )
        return merged_tree


class JsonUtils:
    """Utility class for JSON file operations and data processing"""

    @staticmethod
    def save_to_file(data, file_path):
        """Save JSON data to file"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def add_spaces_around_vars_in_string(text):
        """Adds spaces around @{...} variables in a string if they are missing."""
        if not isinstance(text, str):
            return text
        text = re.sub(r"(\S)(@\{.*?\})", r"\1 \2", text)
        text = re.sub(r"(@\{.*?\})(\S)", r"\1 \2", text)
        return text

    @staticmethod
    def process_data(data):
        """Recursively traverses JSON data and applies the string modification."""
        if isinstance(data, dict):
            return {k: JsonUtils.process_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [JsonUtils.process_data(item) for item in data]
        elif isinstance(data, str):
            return JsonUtils.add_spaces_around_vars_in_string(data)
        else:
            return data


class Translator:
    """Class responsible for translating text using an external translation API"""

    @staticmethod
    def translate_json(file_path, target_language="en"):
        """Translate text in a JSON file using an external translation API"""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        # todo
        pass


class MetaBuilder:
    """Class responsible for building the merged meta and tree structures from local component data."""

    def __init__(self):
        self.local_manager = LocalManager(COMPONENTS_DIR, SKIPPED_COMPONENTS)
        self._build()

    def _build(self):
        color_log("Step 1: Run Meta Scripts and Merge Local Meta", "35")
        self.local_manager.run_meta_scripts()
        local_meta = self.local_manager.merge_local_meta()
        local_types = self.local_manager.merge_local_types()
        local_tree = self.local_manager.merge_local_tree()

        color_log("Step 2: Build Merged Meta and Tree", "35")
        self.meta_list = self.local_manager.build_meta_list(local_meta)
        self.meta_tree = self.local_manager.build_tree_config(local_tree, local_types)


if __name__ == "__main__":
    meta_builder = MetaBuilder()
