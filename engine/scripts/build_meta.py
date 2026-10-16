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
ACTIONLIB_SRC = PROJECT_ROOT / "engine" / "shared" / "astronverse-actionlib" / "src"
ENGINE_PYPROJECT = PROJECT_ROOT / "engine" / "pyproject.toml"

# Components to skip during meta build
# Output file paths
LOCAL_META_FILE = os.path.join(CURRENT_DIR, "temp_local_meta.json")
LOCAL_TREE_FILE = os.path.join(CURRENT_DIR, "temp_local_tree.json")
RESOURCES_META_DIR = PROJECT_ROOT / "resources" / "meta"

SUPPORTED_LOCALES = ["zh_CN", "en_US"]


def color_log(text, color_code):
    """Print colored text in the terminal."""
    print(f"\033[{color_code}m{text}\033[0m")


def parse_pyproject() -> list[str]:
    """
    从 engine/pyproject.toml 解析组件列表。
    组件来源：[tool.uv.sources] 中 path 包含 'components/' 的条目，
    同时结合 [project.dependencies] 中的平台 marker 过滤当前平台不支持的包。

    Returns:
        list: 当前平台支持的组件目录名列表
    """
    if not ENGINE_PYPROJECT.exists():
        color_log(f"Warning: {ENGINE_PYPROJECT} not found", "33")
        return []

    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            color_log("Warning: tomllib/tomli not available", "33")
            return []

    with open(ENGINE_PYPROJECT, "rb") as f:
        data = tomllib.load(f)

    # 从 [project.dependencies] 解析平台 marker，构建 pkg_name -> 是否支持当前平台 的映射
    # 格式示例："astronverse-word; sys_platform == 'win32'"
    current_platform = sys.platform
    platform_allowed: dict[str, bool] = {}
    for dep in data.get("project", {}).get("dependencies", []):
        dep = dep.strip()
        if ";" in dep:
            pkg_part, marker = dep.split(";", 1)
            pkg_name = pkg_part.strip().rstrip()
            marker = marker.strip()
            # 仅处理 sys_platform == '...' 形式
            m = re.search(r"sys_platform\s*==\s*['\"](\w+)['\"]", marker)
            if m:
                platform_allowed[pkg_name] = m.group(1) == current_platform
        else:
            pkg_name = dep.strip().rstrip()
            platform_allowed[pkg_name] = True

    # 从 [tool.uv.sources] 提取 components/ 下的包目录名，跳过当前平台不支持的包
    sources = data.get("tool", {}).get("uv", {}).get("sources", {})
    folders = []
    skipped = []
    for pkg_name, source in sources.items():
        path = source.get("path", "")
        if "components/" not in path:
            continue
        # 若 dependencies 中声明了该包但当前平台不支持，则跳过
        if platform_allowed.get(pkg_name) is False:
            skipped.append(pkg_name)
            continue
        folder_name = Path(path).name
        folders.append(folder_name)

    if skipped:
        color_log(f"Skipped {len(skipped)} components not supported on {current_platform}: {skipped}", "33")
    color_log(f"Loaded {len(folders)} components from pyproject.toml", "32")
    return folders


class LocalManager:
    def __init__(self, components_dir):
        self.components_dir = components_dir
        self.failed_folders = set()
        # 组件列表来自 pyproject.toml
        self.folders = parse_pyproject()
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

    def merge_local_meta(self, locale: str = "zh_CN"):
        """Aggregate meta.json files from each component directory."""
        color_log(f"Merging local meta.json files from component directories [{locale}]...", "35")
        current_platform = sys.platform
        result = {}
        filtered_count = 0
        for folder in self._iter_merge_folders():
            meta_json_path = os.path.join(self.components_dir, folder, "resources", locale, "meta.json")
            if not os.path.isfile(meta_json_path):
                continue
            with open(meta_json_path, encoding="utf-8") as f:
                data = json.load(f)
                for key, item in data.items():
                    if "path" in item:
                        del item["path"]
                    # 平台过滤：platform 声明了但不匹配当前平台则跳过，产物不保留 platform 字段
                    item_platform = item.pop("platform", None)
                    if item_platform:
                        supported = [p.strip() for p in item_platform.split(",")]
                        if current_platform not in supported:
                            filtered_count += 1
                            continue
                    result[key] = item
        color_log(f"Merged local meta items count: {len(result)} (filtered {filtered_count})", "32")
        JsonUtils.save_to_file(result, LOCAL_META_FILE)
        return result

    def merge_local_tree(self, locale: str = "zh_CN"):
        """Merge tree.json files from component directories with deep merge."""
        color_log(f"Merging local tree.json files from component directories [{locale}]...", "35")
        merged_tree = {"atomicTree": [], "atomicTreeExtend": []}

        for folder in self._iter_merge_folders():
            tree_json_path = os.path.join(self.components_dir, folder, "resources", locale, "tree.json")
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
        - 若节点存在 sort 字段，优先使用节点的sort值进行排序
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

        # 返回合并后的节点列表，按 TREE_FRAME 原始顺序排序，未在 TREE_FRAME 中的节点排在前面
        # 若节点存在 sort 字段，优先使用节点的sort值进行排序，按数值大小从小到大排序
        merged = list(target_dict.values())
        order_index = self._get_frame_order_index()
        merged = [(idx, node) for idx, node in enumerate(merged)]
        merged.sort(
            key=lambda item: (
                0 if item[1].get("sort") is not None else 1,
                item[1].get("sort", float("inf")),
                0 if item[1].get("key") not in order_index else 1,
                order_index.get(item[1].get("key"), item[0]),
            )
        )
        return [node for _, node in merged]

    def _get_frame_order_index(self) -> dict:
        """从 TREE_FRAME 构建 key -> 全局排序索引的平铺映射（懒加载）。"""
        if hasattr(self, "_frame_order_index"):
            return self._frame_order_index

        src = str(ACTIONLIB_SRC)
        if src not in sys.path:
            sys.path.insert(0, src)
        from astronverse.actionlib.tree_default import TREE_FRAME

        index: dict = {}
        counter = [0]

        def _walk(nodes):
            for node in nodes:
                key = node.get("key")
                if key:
                    index[key] = counter[0]
                    counter[0] += 1
                if node.get("atomics"):
                    _walk(node["atomics"])

        _walk(TREE_FRAME.get("atomicTree", []))
        _walk(TREE_FRAME.get("atomicTreeExtend", []))

        self._frame_order_index = index
        return index

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

    def merge_local_types(self, locale: str = "zh_CN"):
        """Merge meta_type.json files from component directories."""
        color_log(f"Merging meta_type.json files from component directories [{locale}]...", "35")
        result = {}
        for folder in self._iter_merge_folders():
            types_json_path = os.path.join(self.components_dir, folder, "resources", locale, "meta_type.json")
            if not os.path.isfile(types_json_path):
                continue
            with open(types_json_path, encoding="utf-8") as f:
                data = json.load(f)
                result.update(data)
        return result

    def build_meta_list(self, local_meta, locale: str = "zh_CN") -> list:
        """Build the merged meta list from local meta data."""
        color_log(f"Building merged meta list [{locale}]...", "35")
        merged_meta = []

        for key, value in local_meta.items():
            merged_meta.append({"atomKey": key, "atomContent": json.dumps(value), "sort": None})

        sorted_meta = sorted(merged_meta, key=lambda x: x["atomKey"])
        out_file = RESOURCES_META_DIR / locale / "meta.json"
        JsonUtils.save_to_file(sorted_meta, out_file)
        color_log(f"Merged meta list [{locale}] items count: {len(sorted_meta)}", "32")
        return sorted_meta

    def build_tree_config(self, local_tree, local_types, locale: str = "zh_CN"):
        """Build the tree configuration from local tree data."""
        color_log("Building tree configuration from local tree data...", "35")

        inside = self.build_inside_types_config(locale=locale)

        merged_tree = {
            "atomicTree": local_tree.get("atomicTree", []).copy(),
            "atomicTreeExtend": local_tree.get("atomicTreeExtend", []).copy(),
            "types": local_types.copy(),
            "commonAdvancedParameter": [],
        }

        # 内置 types 覆盖外部组件注册的类型（高优先级）
        merged_tree["types"].update(inside["types"])
        merged_tree["commonAdvancedParameter"].extend(inside["commonAdvancedParameter"])

        out_file = RESOURCES_META_DIR / locale / "tree.json"
        JsonUtils.save_to_file(merged_tree, out_file)
        color_log(
            f"Merged tree nodes count: {len(merged_tree['atomicTree']) + len(merged_tree['atomicTreeExtend'])}", "32"
        )
        return merged_tree

    def build_inside_types_config(self, locale: str = "zh_CN") -> dict:
        """
        使用内置 Python 模块构建 types 和 commonAdvancedParameter，
        替代从 tree_frame.json 读取的方式。

        Args:
            locale: 语言代码，如 "zh_CN"（默认）或 "en_US"

        Returns:
            {"types": {...}, "commonAdvancedParameter": [...]}
        """
        src = str(ACTIONLIB_SRC)
        if src not in sys.path:
            sys.path.insert(0, src)

        from astronverse.actionlib.advanced_default import get_common_advanced_parameters
        from astronverse.actionlib.types_default import get_types_config

        types_config = get_types_config(locale)
        common_advanced = get_common_advanced_parameters(locale)

        color_log(f"Built inside types config: {len(types_config)} types, locale={locale}", "32")
        return {
            "types": types_config,
            "commonAdvancedParameter": common_advanced,
        }


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
        self.local_manager = LocalManager(COMPONENTS_DIR)
        self._build()

    def _build(self):
        color_log("Step 1: Run Meta Scripts", "35")
        self.local_manager.run_meta_scripts()

        color_log("Step 2: Build Merged Meta and Tree for each locale", "35")
        for locale in SUPPORTED_LOCALES:
            color_log(f"--- Building locale: {locale} ---", "33")
            local_meta = self.local_manager.merge_local_meta(locale)
            local_types = self.local_manager.merge_local_types(locale)
            local_tree = self.local_manager.merge_local_tree(locale)
            self.local_manager.build_meta_list(local_meta, locale)
            self.local_manager.build_tree_config(local_tree, local_types, locale)


if __name__ == "__main__":
    meta_builder = MetaBuilder()
