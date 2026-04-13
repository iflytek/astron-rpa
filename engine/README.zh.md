# AstronRPA 引擎平台

<div align="center">

**⚙️ 模块化 RPA 自动化引擎**

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-0.8+-blueviolet.svg)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/ruff-0.12+-orange.svg)](https://docs.astral.sh/ruff/)

[English](README.md) | 简体中文

</div>

## 📑 目录

- [📋 概述](#-概述)
- [✨ 核心特性](#-核心特性)
- [🛠️ 技术栈](#️-技术栈)
- [🚀 快速开始](#-快速开始)
- [📦 包结构](#-包结构)
- [🏗️ 架构概览](#️-架构概览)
- [🔗 前端联调](#-前端联调)
- [📏 代码规范](#-代码规范)

## 📋 概述

AstronRPA 引擎是整个 RPA 系统的核心执行层，负责工作流调度、原子能力执行和前端通信。采用 Python + 组件化架构，通过 uv 进行依赖管理，内置 25+ 原子能力组件，涵盖浏览器操作、Excel 处理、AI 集成等常见自动化场景。

引擎通过 WebSocket 与前端（Electron 桌面端）通信，支持工作流的实时调度与执行。

## ✨ 核心特性

- ⚙️ **组件化架构** - 25+ 独立原子能力组件，每个组件为可编辑 Python 包
- 🔌 **实时通信** - 基于 WebSocket 的前后端双向通信
- 🧩 **可扩展设计** - 通过装饰器注册新原子能力，自动生成 meta/tree 配置
- 🚀 **高效开发** - uv 包管理器，依赖同步速度快
- 🔍 **端到端调试** - 单命令启动完整调试环境
- 📊 **自动化构建** - meta/tree 配置自动构建与合并

## 🛠️ 技术栈

**语言**: Python 3.13+
**包管理**: uv + pyproject.toml
**通信协议**: WebSocket
**代码格式化**: Ruff (line-length: 120)
**代码检查**: pylint
**测试框架**: pytest
**组件注册**: 自研 astronverse-actionlib 框架

## 🚀 快速开始

### 系统要求

- **Python**: >= 3.13
- **uv**: >= 0.8
- **操作系统**: Windows 10/11（主要支持）

### 开发环境搭建

```bash
# 进入引擎目录
cd engine

# 安装 uv（如已安装可跳过）
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步所有依赖（含 38 个本地包）
uv sync

# 启动引擎调试（含 meta 自动构建）
uv run main.py

# 查看输出中的 route_port，如：
# [DEV] scheduler route_port=13159
```

### 组件开发

```bash
# 生成单个组件的 meta 配置
cd engine/components/astronverse-browser
uv run meta.py

# 生成所有组件的 meta 并合并为全局配置
cd engine
uv run scripts/meta_build.py

# 运行组件测试
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

详见 [components/README.zh.md](components/README.zh.md)。

## 📦 包结构

### 原子能力组件（25 个）

| 组件 | 说明 |
|-----|------|
| **astronverse-browser** | 浏览器自动化、网页操作 |
| **astronverse-excel** | Excel 表格操作、数据处理 |
| **astronverse-word** | Word 文档处理 |
| **astronverse-pdf** | PDF 文档操作 |
| **astronverse-email** | 邮件发送和接收 |
| **astronverse-vision** | 计算机视觉、图像识别 |
| **astronverse-ai** | AI 智能服务集成 |
| **astronverse-cua** | CUA 操作 |
| **astronverse-system** | 系统操作、进程管理 |
| **astronverse-window** | 窗口管理 |
| **astronverse-winelement** | Windows 元素操作 |
| **astronverse-software** | 软件操作 |
| **astronverse-input** | 键盘鼠标输入 |
| **astronverse-dialog** | 对话框操作 |
| **astronverse-network** | 网络请求、API 调用 |
| **astronverse-openapi** | OpenAPI 集成 |
| **astronverse-encrypt** | 加密解密功能 |
| **astronverse-dataprocess** | 数据处理 |
| **astronverse-datatable** | 数据表操作 |
| **astronverse-script** | 脚本执行 |
| **astronverse-smart** | 智能操作 |
| **astronverse-enterprise** | 企业级功能 |
| **astronverse-report** | 报告生成 |
| **astronverse-verifycode** | 验证码识别 |
| **astronverse-database** | 数据库操作 |

### 公共基础库（7 个）

| 库 | 说明 |
|---|------|
| **astronverse-actionlib** | 原子能力注册框架 |
| **astronverse-workflowlib** | 工作流执行库 |
| **astronverse-baseline** | RPA 框架核心 |
| **astronverse-locator** | 元素定位技术 |
| **astronverse-browser-plugin** | 浏览器插件通信 |
| **astronverse-websocket-server** | WebSocket 服务端 |
| **astronverse-websocket-client** | WebSocket 客户端 |

### 引擎内部服务（6 个）

| 服务 | 说明 |
|-----|------|
| **astronverse-scheduler** | 引擎调度器 |
| **astronverse-executor** | 工作流执行引擎 |
| **astronverse-picker** | 元素拾取引擎 |
| **astronverse-vision-picker** | 视觉拾取引擎 |
| **astronverse-trigger** | 引擎触发器 |
| **astronverse-browser-bridge** | 浏览器桥接服务 |

## 🏗️ 架构概览

```
engine/
├── components/              # 原子能力组件（25 个独立 Python 包）
│   ├── astronverse-browser/
│   ├── astronverse-excel/
│   ├── astronverse-ai/
│   └── ...
├── shared/                  # 公共基础库（7 个）
│   ├── astronverse-actionlib/     # 原子能力注册框架
│   ├── astronverse-workflowlib/   # 工作流执行库
│   ├── astronverse-baseline/      # RPA 框架核心
│   └── ...
├── servers/                 # 引擎内部服务（6 个）
│   ├── astronverse-scheduler/     # 调度器
│   ├── astronverse-executor/      # 执行器
│   └── ...
├── scripts/                 # 构建脚本
│   ├── meta_build.py              # meta/tree 配置构建
│   └── ...
├── binaries/                # 原生二进制文件
├── main.py                  # 调试启动入口
└── pyproject.toml           # 项目依赖声明
```

### 模块关系

```
┌─────────────────────────────────────────────┐
│              main.py (调试入口)               │
│         MetaBuilder → Scheduler              │
└─────────────┬───────────────────┬────────────┘
              │                   │
              ▼                   ▼
┌─────────────────────┐ ┌─────────────────────┐
│   servers/           │ │   scripts/           │
│   scheduler          │ │   meta_build.py      │
│   executor           │ │   (构建 meta/tree)   │
│   picker             │ └─────────┬───────────┘
│   trigger            │           │
└──────────┬──────────┘           ▼
           │             ┌─────────────────────┐
           ▼             │   components/ (25)    │
┌─────────────────────┐ │   config.yaml         │
│   shared/            │ │   meta.py → meta.json │
│   actionlib          │ │   → tree.json         │
│   workflowlib        │ └─────────────────────┘
│   baseline           │
│   websocket-*        │
└─────────────────────┘
```

## 🔗 前端联调

前端（Electron 桌面端）通过 WebSocket 与引擎通信。开发模式下，前端跳过内置引擎启动，直连本地运行的引擎。

**终端 1 — 启动引擎：**
```bash
cd engine
uv run main.py
# 📝 记下输出的 route_port (如 13159)
```

**终端 2 — 启动前端：**
```bash
cd frontend
pnpm install
set PORT=13159 && pnpm dev:desktop
```


## 📏 代码规范

| 工具 | 用途 | 配置文件 |
|-----|------|---------|
| Ruff | 代码格式化与检查 | `.ruff.toml` |
| pylint | 代码静态分析 | - |
| pytest | 单元测试 | - |
| pre-commit | Git 提交钩子 | - |

```bash
# 代码格式化
uv run ruff format .

# 代码检查
uv run ruff check .

# 运行测试
uv run pytest
```

---

如有问题请联系项目维护者。
