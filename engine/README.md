# AstronRPA Engine Platform

<div align="center">

**⚙️ Modular RPA Automation Engine**

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-0.8+-blueviolet.svg)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/ruff-0.12+-orange.svg)](https://docs.astral.sh/ruff/)

English | [简体中文](README.zh.md)

</div>

## 📑 Table of Contents

- [📋 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
- [📦 Package Structure](#-package-structure)
- [🏗️ Architecture Overview](#️-architecture-overview)
- [🔗 Frontend Integration](#-frontend-integration)
- [📏 Code Standards](#-code-standards)

## 📋 Overview

The AstronRPA engine is the core execution layer of the entire RPA system, responsible for workflow scheduling, atomic capability execution, and frontend communication. It uses a Python + component-based architecture, managed by uv, with 25+ built-in atomic capability components covering common automation scenarios such as browser operations, Excel processing, and AI integration.

The engine communicates with the frontend (Electron desktop app) via WebSocket, enabling real-time workflow scheduling and execution.

## ✨ Key Features

- ⚙️ **Component Architecture** - 25+ independent atomic capability components, each as an editable Python package
- 🔌 **Real-time Communication** - Bidirectional frontend-backend communication via WebSocket
- 🧩 **Extensible Design** - Register new atomic capabilities with decorators, auto-generate meta/tree configs
- 🚀 **Efficient Development** - uv package manager for fast dependency syncing
- 🔍 **End-to-End Debugging** - Single command to start the full debug environment
- 📊 **Automated Build** - Auto meta/tree configuration build and merge

## 🛠️ Tech Stack

**Language**: Python 3.13+
**Package Management**: uv + pyproject.toml
**Communication**: WebSocket
**Code Formatting**: Ruff (line-length: 120)
**Code Linting**: pylint
**Testing**: pytest
**Component Registration**: In-house astronverse-actionlib framework

## 🚀 Quick Start

### System Requirements

- **Python**: >= 3.13
- **uv**: >= 0.8
- **OS**: Windows 10/11 (primary support)

### Development Setup

```bash
# Navigate to the engine directory
cd engine

# Install uv (skip if already installed)
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync all dependencies (38 local packages)
uv sync

# Start engine debug (includes auto meta build)
uv run main.py

# Check the route_port in output, e.g.:
# [DEV] scheduler route_port=13159
```

### Component Development

```bash
# Generate meta config for a single component
cd engine/components/astronverse-browser
uv run meta.py

# Generate meta for all components and merge into global config
cd engine
uv run scripts/meta_build.py

# Run component tests
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

See [components/README.md](components/README.md) for details.

## 📦 Package Structure

### Atomic Capability Components (25)

| Component | Description |
|-----------|-------------|
| **astronverse-browser** | Browser automation, web operations |
| **astronverse-excel** | Excel spreadsheet operations, data processing |
| **astronverse-word** | Word document processing |
| **astronverse-pdf** | PDF document operations |
| **astronverse-email** | Email sending and receiving |
| **astronverse-vision** | Computer vision, image recognition |
| **astronverse-ai** | AI service integration |
| **astronverse-cua** | CUA operations |
| **astronverse-system** | System operations, process management |
| **astronverse-window** | Window management |
| **astronverse-winelement** | Windows element operations |
| **astronverse-software** | Software operations |
| **astronverse-input** | Keyboard and mouse input |
| **astronverse-dialog** | Dialog operations |
| **astronverse-network** | Network requests, API calls |
| **astronverse-openapi** | OpenAPI integration |
| **astronverse-encrypt** | Encryption and decryption |
| **astronverse-dataprocess** | Data processing |
| **astronverse-datatable** | Data table operations |
| **astronverse-script** | Script execution |
| **astronverse-smart** | Smart operations |
| **astronverse-enterprise** | Enterprise features |
| **astronverse-report** | Report generation |
| **astronverse-verifycode** | CAPTCHA recognition |
| **astronverse-database** | Database operations |

### Shared Base Libraries (7)

| Library | Description |
|---------|-------------|
| **astronverse-actionlib** | Atomic capability registration framework |
| **astronverse-workflowlib** | Workflow execution library |
| **astronverse-baseline** | RPA framework core |
| **astronverse-locator** | Element locating technology |
| **astronverse-browser-plugin** | Browser plugin communication |
| **astronverse-websocket-server** | WebSocket server |
| **astronverse-websocket-client** | WebSocket client |

### Internal Engine Services (6)

| Service | Description |
|---------|-------------|
| **astronverse-scheduler** | Engine scheduler |
| **astronverse-executor** | Workflow execution engine |
| **astronverse-picker** | Element picker engine |
| **astronverse-vision-picker** | Vision picker engine |
| **astronverse-trigger** | Engine trigger |
| **astronverse-browser-bridge** | Browser bridge service |

## 🏗️ Architecture Overview

```
engine/
├── components/              # Atomic capability components (25 independent Python packages)
│   ├── astronverse-browser/
│   ├── astronverse-excel/
│   ├── astronverse-ai/
│   └── ...
├── shared/                  # Shared base libraries (7)
│   ├── astronverse-actionlib/     # Atomic capability registration framework
│   ├── astronverse-workflowlib/   # Workflow execution library
│   ├── astronverse-baseline/      # RPA framework core
│   └── ...
├── servers/                 # Internal engine services (6)
│   ├── astronverse-scheduler/     # Scheduler
│   ├── astronverse-executor/      # Executor
│   └── ...
├── scripts/                 # Build scripts
│   ├── meta_build.py              # meta/tree configuration build
│   └── ...
├── binaries/                # Native binaries
├── main.py                  # Debug entry point
└── pyproject.toml           # Project dependency declaration
```

### Module Relationships

```
┌─────────────────────────────────────────────┐
│            main.py (Debug Entry)             │
│         MetaBuilder → Scheduler              │
└─────────────┬───────────────────┬────────────┘
              │                   │
              ▼                   ▼
┌─────────────────────┐ ┌─────────────────────┐
│   servers/           │ │   scripts/           │
│   scheduler          │ │   meta_build.py      │
│   executor           │ │   (Build meta/tree)  │
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

## 🔗 Frontend Integration

The frontend (Electron desktop app) communicates with the engine via WebSocket. In development mode, the frontend skips the built-in engine startup and connects directly to the locally running engine.

**Terminal 1 — Start the engine:**
```bash
cd engine
uv run main.py
# 📝 Note the route_port from the output (e.g., 13159)
```

**Terminal 2 — Start the frontend:**
```bash
cd frontend
pnpm install
set PORT=13159 && pnpm dev:desktop
```


## 📏 Code Standards

| Tool | Purpose | Config File |
|------|---------|-------------|
| Ruff | Code formatting & linting | `.ruff.toml` |
| pylint | Static code analysis | - |
| pytest | Unit testing | - |
| pre-commit | Git commit hooks | - |

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Run tests
uv run pytest
```

---

If you have any questions, please contact the project maintainers.
