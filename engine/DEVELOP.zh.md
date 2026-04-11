简体中文 | [English](DEVELOP.md)
# Engine 开发指南

本文档面向 engine 模块的开发者，介绍如何开发原子能力组件以及如何进行端对端调试。

---

## 目录结构

```
engine/
├── components/          # 原子能力组件（每个子目录为一个独立 Python 包）
│   ├── astronverse-browser/
│   ├── astronverse-excel/
│   └── ...
├── shared/              # 公共基础库
│   ├── astronverse-actionlib/   # 原子能力注册框架
│   ├── astronverse-workflowlib/ # 工作流执行库
│   └── ...
├── main.py              # 调试启动入口（含 meta 构建）
├── meta_build.py        # meta/tree 配置构建脚本
└── pyproject.toml       # 项目依赖声明
```

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

- 方法的类名作为 `group_key`，生成的 `key` 格式为 `ClassName.method_name`
- 参数类型注解会自动映射为前端表单控件类型
- 返回值需在 `config.yaml` 的 `outputList` 中声明

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

- `path` 支持多个路径，原子能力会同时出现在多个 tree 节点下
- `comment` 中的 `@{key}` 引用必须在 `inputList` 或 `outputList` 中有对应定义

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
uv run meta_build.py
```

生成结果：
- `resources/meta/meta.json` — 全量原子能力配置
- `resources/meta/tree.json` — 全量 tree 配置

---

## 端对端调试

### 调试入口

`main.py` 是调试专用入口，启动时会：
1. 调用 `MetaBuilder` 重新构建全量 meta/tree 配置
2. 启动调度器（scheduler），与前端建立 WebSocket 连接

```bash
cd engine
uv run main.py
```
3. 查看启动后的route_port，用于启动客户端连接引擎服务的连接端口。
```bash
route_port=13159
```

### 配置调试环境

修改根目录 `/resources/config.yaml` 文件中 `skip_engine_start` 为 `true`, 跳过客户端启动 Engine， （会导致进程间通信失效，调试无影响）
说明：打安装包时`skip_engine_start` 应设置为 `false`


### 前端联调

前端（Electron 桌面端）通过 `server.ts` 控制 engine 进程的启动与通信：

- 开发模式下，前端通过 `config.skip_engine_start = true` 跳过 engine 进程启动，直接连接本地运行的 engine
- engine 默认端口为 `13159`，可通过环境变量 `PORT` 修改
- engine 启动后通过 `||emit||` 前缀的 stdout 消息向前端推送事件

前后端联调步骤：

1. 先启动 engine：
   ```bash
   cd engine
   uv run main.py
   ```
2. 在前端工程中启动前端开发服务器：
   ```bash
   cd frontend
   set PORT={route_port} && pnpm dev:desktop
   ```

### 单独调试组件

可直接运行组件内的具体模块或测试：

```bash
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

---

## 代码规范

- 代码格式化使用 `ruff`，配置见 `.ruff.toml`
- 原子能力的 `path` 字段必须符合 `/path1/path2/...` 格式，否则构建时会抛出校验错误
- `meta.json`、`tree.json` 等生成文件不应手动编辑，应通过 `meta.py` 重新生成

---

如有问题请联系项目维护者。
