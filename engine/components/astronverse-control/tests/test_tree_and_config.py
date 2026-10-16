"""config.yaml 与生成的 tree.json 一致性测试。

左侧原子能力树完全由 config.yaml 的 icon/path/hidden 驱动。配置漏项时原子能力
会从树上消失（用户无法拖入流程），而路径写错会挂到不存在的分类下——两者都不会
报错，只能靠断言拦住。
"""

from collections import defaultdict

import pytest

LANGS = ("zh_CN", "en_US")


def _collect_leaves(nodes: list, path: str = "") -> dict:
    """遍历树，返回 {atomic_key: (所在路径, 节点数据)}。叶子节点没有 atomics 字段。"""
    leaves = {}
    for node in nodes:
        node_path = f"{path}/{node['key']}"
        if "atomics" in node:
            leaves.update(_collect_leaves(node["atomics"], node_path))
        else:
            leaves[node["key"]] = (path, node)
    return leaves


@pytest.fixture(scope="session")
def tree_leaves(regenerated: dict) -> dict:
    """各语言树上的叶子节点，形如 {lang: {atomic_key: (path, node)}}。

    tree.json 的根键（atomicTree）位于被遍历节点的上一层，需要补进路径前缀，
    才能与 config.yaml 里 /atomicTree/... 的声明对齐。
    """
    return {
        lang: _collect_leaves(regenerated[lang]["tree"]["atomicTree"], "/atomicTree") for lang in LANGS
    }


@pytest.mark.parametrize("lang", LANGS)
def test_tree_contains_only_known_atomics(tree_leaves, base_meta, lang):
    """树上不应出现 meta 里不存在的 key，否则前端点击会拿不到原子定义。"""
    assert set(tree_leaves[lang]) <= set(base_meta)


@pytest.mark.parametrize("lang", LANGS)
def test_atomics_with_path_appear_on_tree(tree_leaves, config_atomic, lang):
    """config.yaml 里配了 path 的原子能力必须出现在树上。"""
    configured = {key for key, value in config_atomic.items() if value.get("path")}
    assert configured - set(tree_leaves[lang]) == set()


@pytest.mark.parametrize("lang", LANGS)
def test_hidden_atomics_stay_off_tree(tree_leaves, config_atomic, lang):
    """标记 hidden 的节点（Catch、Group）只能由父节点带出，不单独展示。"""
    hidden = {key for key, value in config_atomic.items() if value.get("hidden")}
    assert hidden & set(tree_leaves[lang]) == set()


@pytest.mark.parametrize("lang", LANGS)
def test_tree_path_matches_config(tree_leaves, config_atomic, lang):
    """节点的实际挂载路径必须与 config.yaml 声明的 path 一致。"""
    mismatched = {}
    for key, (path, _) in tree_leaves[lang].items():
        expected = config_atomic.get(key, {}).get("path") or []
        if path not in expected:
            mismatched[key] = (path, expected)
    assert mismatched == {}


@pytest.mark.parametrize("lang", LANGS)
def test_tree_icons_match_config(tree_leaves, config_atomic, lang):
    """图标来自 config.yaml，缺失会在树上渲染成空白方块。"""
    mismatched = {
        key: (node["icon"], config_atomic.get(key, {}).get("icon"))
        for key, (_, node) in tree_leaves[lang].items()
        if node["icon"] != config_atomic.get(key, {}).get("icon")
    }
    assert mismatched == {}


@pytest.mark.parametrize("lang", LANGS)
def test_sibling_leaf_order_follows_config(config_atomic, regenerated, lang):
    """同级叶子节点应保持 config.yaml 中 atomic 的声明顺序。"""
    expected = defaultdict(list)
    for key, value in config_atomic.items():
        if value.get("hidden"):
            continue
        for path in value.get("path") or []:
            expected[path].append(key)

    actual = defaultdict(list)

    def walk(nodes, parent_path):
        for node in nodes:
            node_path = f"{parent_path}/{node['key']}"
            children = node.get("atomics", [])
            leaves = [child["key"] for child in children if "atomics" not in child]
            if leaves:
                actual[node_path].extend(leaves)
            if children:
                walk(children, node_path)

    walk(regenerated[lang]["tree"]["atomicTree"], "/atomicTree")
    assert dict(actual) == {path: keys for path, keys in expected.items() if keys}


@pytest.mark.parametrize("lang", LANGS)
def test_tree_has_no_duplicate_atomics(regenerated, lang):
    """同一原子能力重复挂载会在树上出现两次。"""
    keys = []

    def walk(nodes):
        for node in nodes:
            if "atomics" in node:
                walk(node["atomics"])
            else:
                keys.append(node["key"])

    walk(regenerated[lang]["tree"]["atomicTree"])
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("lang", LANGS)
def test_tree_titles_follow_meta_titles(tree_leaves, regenerated, lang):
    """树上的标题应与该语言 meta 的 title 一致，避免两处文案不同步。"""
    meta = regenerated[lang]["meta"]
    mismatched = {
        key: (node["title"], meta[key].get("title"))
        for key, (_, node) in tree_leaves[lang].items()
        if node["title"] != meta[key].get("title")
    }
    assert mismatched == {}


@pytest.mark.parametrize("lang", LANGS)
def test_every_config_entry_has_icon(config_atomic, lang):
    """config.yaml 中的每条 atomic 配置都要带 icon。"""
    assert [key for key, value in config_atomic.items() if not value.get("icon")] == []


def test_config_only_references_registered_atomics(config_atomic, base_meta):
    """config.yaml 残留已删除原子能力的配置，说明清理不彻底。"""
    assert set(config_atomic) - set(base_meta) == set()


def test_config_paths_are_absolute_segments(config_atomic):
    """actionlib 要求 path 形如 /a/b，格式错误会在生成 meta 时抛异常。"""
    invalid = [
        (key, path)
        for key, value in config_atomic.items()
        for path in value.get("path") or []
        if not path.startswith("/") or path.endswith("/") or "//" in path
    ]
    assert invalid == []
