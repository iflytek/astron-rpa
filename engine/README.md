English | [简体中文](README.zh.md)
# Engine Meta/Tree Build

Each component generates localized metadata from its own `meta.py`:

```text
engine/components/<component>/resources/<locale>/meta.json
engine/components/<component>/resources/<locale>/tree.json
```

Run the aggregate build from `engine`:

```bash
uv run scripts/build_meta.py
```

The builder reads component paths from `engine/pyproject.toml`, runs each component `meta.py`, and writes:

```text
resources/meta/zh_CN/meta.json
resources/meta/zh_CN/tree.json
resources/meta/en_US/meta.json
resources/meta/en_US/tree.json
```

Build one component directly:

```bash
cd engine/components/astronverse-browser
uv run meta.py
```

