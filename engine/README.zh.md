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

修改组件参数时，应同步更新 Python 定义和对应 `locale/<locale>.json` 中的文本，图标和树路径仍放在 `config.yaml`。使用上述命令重新生成元数据，并部署匹配的客户端代码。元数据决定设计器中的参数表单，不会改写已保存流程中的参数；受影响的流程需单独编辑并重新发布。

浏览器参数、邮件已读状态、附件保存和数据库驱动配置见[常见问题](../FAQ.zh.md)。
