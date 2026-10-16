简体中文 | [English](README.md)
# Engine Meta/Tree 构建

组件的 metadata 由各自目录下的 `meta.py` 生成，产物按语言写入：

```text
engine/components/<component>/resources/<locale>/meta.json
engine/components/<component>/resources/<locale>/tree.json
```

在 `engine` 目录执行汇总构建：

```bash
uv run scripts/build_meta.py
```

脚本会读取 `engine/pyproject.toml` 中的组件，依次执行组件 `meta.py`，然后生成汇总产物：

```text
resources/meta/zh_CN/meta.json
resources/meta/zh_CN/tree.json
resources/meta/en_US/meta.json
resources/meta/en_US/tree.json
```

单独生成组件：

```bash
cd engine/components/astronverse-browser
uv run meta.py
```
