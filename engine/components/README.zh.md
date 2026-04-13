简体中文 | [English](README.md)
# Components 开发指南

本文档面向 components 模块的开发者，介绍如何开发原子能力组件和进行调试。

---

## 目录

- [环境准备](#环境准备)
- [开发原子能力组件](#开发原子能力组件)
- [端对端调试](#端对端调试)
- [代码规范](#代码规范)

---

## 环境准备

本项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖。

1. 安装 uv（如已安装可跳过）：
  ```bash
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

2. 在 `engine` 目录下同步依赖：
  ```bash
  cd engine
  uv sync
  ```

---

## 开发原子能力组件

### 组件目录结构

每个组件是一个独立的可编辑 Python 包，结构如下：

```
components/astronverse-browser/
├── src/
│   └── astronverse/
│       └── browser/
│           ├── browser_software.py   # 原子能力实现
│           └── ...
├── config.yaml          # 原子能力 UI 配置（标题、图标、参数描述、tree 路径）
├── config_type.yaml     # 类型定义配置
├── meta.py              # meta/tree 生成入口
├── meta.json            # 生成的 meta 输出（勿手动编辑）
├── tree.json            # 生成的 tree 输出（勿手动编辑）
├── meta_type.json       # 生成的类型输出（勿手动编辑）
└── pyproject.toml       # 组件依赖声明
```

### 实现原子能力

在组件的 `src` 目录下，用 `@atomicMg.atomic()` 装饰器注册原子能力：

```python
from astronverse.actionlib.atomic import atomicMg

class BrowserSoftware:
    @atomicMg.atomic()
    def browser_open(self, url: str, browser_type: str = "chrome") -> object:
        # 实现逻辑
        ...
```

- 类名用作 `group_key`，生成的 `key` 格式为 `ClassName.method_name`
- 参数类型注解自动映射为前端表单控件类型
- 返回值须在 `config.yaml` 的 `outputList` 中声明

### 配置 config.yaml

```yaml
atomic:
  BrowserSoftware.browser_open:
    title: 打开浏览器
    icon: open-browser
    comment: 打开 @{browser_type} 并进入 @{url}，输出 @{web_open}
    helpManual: ''
    path:
      - /atomicTree/web        # 在 tree 中的挂载路径，必须为 /path1/path2/... 格式
    inputList:
      - key: url
        title: 初始网址
        tip: 输入要打开的网址
    outputList:
      - key: web_open
        title: 浏览器对象
```

- `path` 支持多个路径，原子能力将同时出现在多个 tree 节点下
- `comment` 中的 `@{key}` 引用必须对应 `inputList` 或 `outputList` 中的定义

### 在 meta.py 中注册

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg

if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(BrowserSoftware, version=get_version())
    atomicMg.meta()                                          # 生成 meta.json

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")                                 # 生成 tree.json
```

### 生成单个组件的 meta

```bash
cd engine/components/astronverse-browser
uv run meta.py
```

### 生成所有组件的 meta，并合并为全局配置

```bash
cd engine
uv run scripts/meta_build.py
```

输出结果：
- `resources/meta/meta.json` — 完整的原子能力配置
- `resources/meta/tree.json` — 完整的功能树配置

---

### 新增原子能力组件

以下以新增一个"文字加密"组件 `astronverse-myencrypt` 为例，演示完整的新增流程。

**第一步：创建组件目录结构**

```
engine/components/astronverse-myencrypt/
├── src/
│   └── astronverse/
│       └── myencrypt/
│           ├── __init__.py       # 枚举定义
│           └── myencrypt.py      # 原子能力实现
├── config.yaml                   # UI 配置
├── meta.py                       # meta 生成入口
└── pyproject.toml                # 依赖声明
```

**第二步：声明依赖 `pyproject.toml`**

```toml
[project]
name = "astronverse-myencrypt"
version = "1.0.0"
description = "my encrypt component."
requires-python = ">=3.13"

dependencies = [
    "astronverse-actionlib",
]

[tool.uv.sources]
astronverse-actionlib = {path = "../../shared/astronverse-actionlib", editable = true}

[tool.hatch.build.targets.wheel]
packages = ["src/astronverse"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**第三步：定义枚举 `src/astronverse/myencrypt/__init__.py`**

```python
from enum import Enum

class CaseType(Enum):
    LOWER = "lower"
    UPPER = "upper"
```

**第四步：实现原子能力 `src/astronverse/myencrypt/myencrypt.py`**

```python
import hashlib
from astronverse.actionlib.atomic import atomicMg
from astronverse.myencrypt import CaseType


class MyEncrypt:
    @atomicMg.atomic()
    def md5_encrypt(self, source_str: str, case_type: CaseType = CaseType.LOWER) -> str:
        result = hashlib.md5(source_str.encode()).hexdigest()
        return result.upper() if case_type == CaseType.UPPER else result
```

**第五步：配置 `config.yaml`**

```yaml
atomic:
  MyEncrypt.md5_encrypt:
    title: MD5加密
    icon: md5-encrypt
    comment: 对 @{source_str} 进行 MD5 加密，输出 @{encrypted_result}
    helpManual: ''
    path:
      - /atomicTree/os/encrypt
    inputList:
      - key: source_str
        title: 待加密字符串
        tip: 输入需要加密的文本
      - key: case_type
        title: 结果大小写
        tip: 选择加密结果的大小写格式
    outputList:
      - key: encrypted_result
        title: 加密结果

options:
  CaseType:
    - value: lower
      label: 小写
    - value: upper
      label: 大写
```

**第六步：编写 `meta.py`**

```python
from astronverse.actionlib.atomic import atomicMg
from astronverse.actionlib.config import config
from astronverse.actionlib.tree import treeMg
from astronverse.myencrypt.myencrypt import MyEncrypt

if __name__ == "__main__":
    config.set_config_file("config.yaml")
    atomicMg.register(MyEncrypt, version="1.0.0")
    atomicMg.meta()

    treeMg.load_node_config_from_frame_json("../../../resources/meta/tree_frame.json")
    treeMg.build_from_meta_and_config("meta.json", "config.yaml")
    treeMg.meta("tree.json")
```

**第七步：将组件注册到 `engine/pyproject.toml`**

新组件需要在 `engine/pyproject.toml` 中声明，才能被 `uv sync` 识别并安装。需要在两处分别追加一行：

1. 在 `dependencies` 列表中添加包名：

```toml
dependencies = [
    # ... 已有条目 ...
    "astronverse-encrypt",
    "astronverse-myencrypt",   # 新增这一行
]
```

2. 在 `[tool.uv.sources]` 中指定本地路径（可编辑模式）：

```toml
[tool.uv.sources]
# ... 已有条目 ...
astronverse-encrypt = {path = "./components/astronverse-encrypt", editable = true}
astronverse-myencrypt = {path = "./components/astronverse-myencrypt", editable = true}  # 新增这一行
```

**第八步：同步依赖并生成 meta**

```bash
# 在 engine 目录下同步依赖，使新组件生效
cd engine
uv sync

# 生成当前组件的 meta
cd components/astronverse-myencrypt
uv run meta.py

# 或一次性重新生成所有组件的全局 meta
cd engine/scripts
uv run meta_build.py
```

执行成功后，组件目录下会自动生成 `meta.json` 和 `tree.json`，同时 `resources/meta/meta.json` 与 `resources/meta/tree.json` 也会更新。



---

## 端对端调试

请查阅 `engine/DEVELOPMENT.zh.md` 文档

### 单独调试组件

可直接运行组件内的具体模块或测试：

```bash
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

---

## 代码规范

- 原子能力的 `path` 字段必须遵循 `/path1/path2/...` 格式，否则构建时会抛出校验错误
- `meta.json`、`tree.json` 等生成文件不应手动编辑，应通过 `meta.py` 重新生成
- 使用 `pylint` 进行代码检查

---

如有问题请联系项目维护者。
