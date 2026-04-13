简体中文 | [English](README.md)
# 自动构建 meta 配置说明

本目录下的 `meta_build.py` 会作为 `engine` 的 uv 脚本执行，用于自动构建和合并组件的 meta 与 tree 配置。以下为使用说明：

## 功能简介

- 自动执行各组件目录下的 `meta.py`，生成/更新本地 `meta.json` 与 `tree.json`
- 合并所有组件的 `meta.json`，与基础配置 `base_meta.json` 合并，输出到 `resources/meta/meta.json`
- 深度合并所有组件的 `tree.json`，与骨架配置 `tree_frame.json` 合并，输出到 `resources/meta/tree.json`
- 合并所有组件的 `meta_type.json` 类型定义
- 同级节点中叶子原子能力始终排在子树节点之前

## 环境准备

脚本需要在 `engine` 项目根目录通过 [uv](https://docs.astral.sh/uv/) 执行，以复用引擎项目依赖。

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

无需手动配置环境变量。

## 使用方法

1. 进入 `engine` 目录：
  ```bash
  cd engine
  ```
2. 运行脚本：
  ```bash
  uv sync
  uv run scripts/meta_build.py
  ```

## 工作流程

1. **执行组件 meta.py**  
  自动遍历 `components` 目录，执行每个组件下的 `meta.py`，生成/更新对应的 `meta.json` 和 `tree.json`。

2. **合并本地 meta.json**  
  汇总所有组件的 `meta.json`，生成临时文件 `temp_local_meta.json`。

3. **合并本地 tree.json**  
  深度合并所有组件的 `tree.json`，生成临时文件 `temp_local_tree.json`。相同 key 的节点会递归合并其 `atomics`。

4. **构建最终 meta**  
  将本地 meta 与 `resources/meta/base_meta.json` 合并，按 key 排序后输出到 `resources/meta/meta.json`。

5. **构建最终 tree**  
  将本地 tree 与 `resources/meta/tree_frame.json`（骨架配置）深度合并，同时合并类型定义与公共高级参数，输出到 `resources/meta/tree.json`。

## 输出文件

| 文件 | 说明 |
|------|------|
| `engine/scripts/temp_local_meta.json` | 本地组件 meta 合并临时文件 |
| `engine/scripts/temp_local_tree.json` | 本地组件 tree 合并临时文件 |
| `resources/meta/meta.json` | 最终合并后的 meta 配置 |
| `resources/meta/tree.json` | 最终合并后的 tree 配置 |

## 注意事项

- 跳过目录在 `SKIPPED_COMPONENTS` 列表中配置，默认跳过 `astronverse-database`。
- 合并逻辑以本地组件数据为主，骨架配置 `tree_frame.json` 提供树结构框架。

如有问题请联系项目维护者。
