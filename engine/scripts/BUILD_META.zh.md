简体中文 | [English](BUILD_META.md)
# build_meta.py 构建脚本说明

`build_meta.py` 作为 `engine` 的 uv 脚本执行，用于构建和合并组件的 meta 与 tree 配置。

## 功能简介

- 组件列表由 `engine/pyproject.toml` 统一管理，无需手动维护
- **平台感知构建**：构建产物仅包含当前平台支持的原子能力，不同平台产物相互独立
- 自动执行各组件目录下的 `meta.py`，生成/更新多语言产物
- 合并所有组件的多语言 `meta.json`，按 key 排序后输出
- 深度合并所有组件的多语言 `tree.json`，与内置类型定义合并输出
- 支持多语言输出，当前支持 `zh_CN` 和 `en_US`

## 环境准备

脚本需要在 `engine` 项目根目录通过 [uv](https://docs.astral.sh/uv/) 执行。

1. 安装 uv（如已安装可跳过）：
  ```bash
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
2. 同步依赖并运行：
  ```bash
  cd engine
  uv sync
  uv run scripts/build_meta.py
  ```

## 工作流程

1. **加载组件列表**  
   从 `engine/pyproject.toml` 的 `[tool.uv.sources]` 中提取所有 `path` 包含 `components/` 的包作为构建目标。新增或移除组件只需修改 `pyproject.toml`，构建脚本自动感知。

2. **执行组件 meta.py**  
   遍历组件列表，执行每个组件下的 `meta.py`，生成/更新对应 `resources/{locale}/` 下的 `meta.json`、`tree.json`、`meta_type.json`。执行失败的组件会被跳过并记录，不影响其他组件继续构建。

3. **按语言循环构建**（`zh_CN` 和 `en_US`）：

   a. **合并本地 meta.json（含平台过滤）**  
     汇总所有组件 `resources/{locale}/meta.json`，过滤掉不支持当前平台的原子能力，生成临时文件 `temp_local_meta.json`。

   b. **合并本地 meta_type.json**  
     合并所有组件 `resources/{locale}/meta_type.json` 的类型定义。

   c. **合并本地 tree.json**  
     深度合并所有组件 `resources/{locale}/tree.json`，生成临时文件 `temp_local_tree.json`。相同 key 的节点会递归合并其 `atomics` 子节点。

   d. **构建最终 meta**  
     将合并后的 meta 按 atomKey 排序，输出到 `resources/meta/{locale}/meta.json`。

   e. **构建最终 tree**  
     将合并后的 tree 与内置类型配置（由 `astronverse-actionlib` 的 `get_types_config` / `get_common_advanced_parameters` 提供）合并。内置类型优先级高于组件注册类型，最终输出到 `resources/meta/{locale}/tree.json`。

## 平台支持机制

构建产物是平台特定的，不同平台独立构建，产物中不包含 `platform` 字段。

### 1. 包级别平台限制

通过 `engine/pyproject.toml` 中的 Python Environment Markers 声明，由 `uv` 在安装时控制：

```toml
dependencies = [
    # 所有平台
    "astronverse-system",
    "astronverse-browser",

    # 仅 Windows
    "astronverse-word; sys_platform == 'win32'",
    "astronverse-winelement; sys_platform == 'win32'",
]
```

在 macOS/Linux 上执行 `uv sync` 时，`sys_platform == 'win32'` 的包不会被安装。构建脚本在加载组件列表时，会同时读取 `[project.dependencies]` 中的平台 marker 和 `[tool.uv.sources]` 中的路径，自动跳过当前平台不支持的组件。

### 2. 原子能力级别平台限制

对于同一组件内不同平台支持的原子能力，在装饰器中声明（与 `sys.platform` 保持一致）：

```python
# 支持所有平台（默认，不声明 platform）
@atomicMg.atomic()
def list_processes(self):
    pass

# 仅支持 Windows
@atomicMg.atomic(platform="win32")
def get_window_handle(self, pid: int):
    pass

# 支持多个平台（逗号分隔）
@atomicMg.atomic(platform="win32,darwin")
def get_clipboard_text(self):
    pass
```

构建时，`platform` 字段不匹配当前 `sys.platform` 的原子能力会被直接过滤，不出现在产物中。

**平台标识（与 `sys.platform` 一致）：**
- `win32` — Windows
- `darwin` — macOS
- `linux` — Linux

## 输出文件

| 文件 | 说明 |
|------|------|
| `engine/scripts/temp_local_meta.json` | 本地组件 meta 合并临时文件（最后一个 locale 的结果） |
| `engine/scripts/temp_local_tree.json` | 本地组件 tree 合并临时文件（最后一个 locale 的结果） |
| `resources/meta/zh_CN/meta.json` | 最终合并后的 meta 配置（中文） |
| `resources/meta/zh_CN/tree.json` | 最终合并后的 tree 配置（中文） |
| `resources/meta/en_US/meta.json` | 最终合并后的 meta 配置（英文） |
| `resources/meta/en_US/tree.json` | 最终合并后的 tree 配置（英文） |

## 注意事项

- 内置类型定义由 `astronverse-actionlib` 的 `get_types_config` 和 `get_common_advanced_parameters` 提供，优先级高于组件注册的类型。
- 执行时若某个组件的 `meta.py` 失败，该组件会被跳过，不影响其他组件继续构建。
