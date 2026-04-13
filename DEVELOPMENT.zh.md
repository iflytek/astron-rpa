<div align="center">

# 🛠️ AstronRPA 开发指南

[![Python Version](https://img.shields.io/badge/Python-3.13.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node Version](https://img.shields.io/badge/Node.js-22+-green?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Java Version](https://img.shields.io/badge/Java-8+-orange?logo=openjdk&logoColor=white)](https://openjdk.org/)

**面向开发者的完整开发环境搭建与模块开发指引**

[环境准备](#-开发环境准备) · [前端开发](#-前端开发) · [引擎开发](#-引擎开发) · [后端开发](#-后端服务开发) · [联调指南](#-前后端联调)

</div>

---

## 📋 目录

- [项目架构概览](#-项目架构概览)
- [开发环境准备](#-开发环境准备)
- [项目结构说明](#-项目结构说明)
- [前端开发](#-前端开发)
- [引擎开发](#-引擎开发)
- [后端服务开发](#-后端服务开发)
- [前后端联调](#-前后端联调)
- [Makefile 工程命令](#-makefile-工程命令)
- [代码规范](#-代码规范)
- [Docker 本地开发](#-docker-本地开发)
- [常见问题](#-常见问题)

---

## 🏗️ 项目架构概览

AstronRPA 采用 **服务端-客户端分布式架构**，由以下模块组成：

| 层级 | 技术栈 | 模块 | 语言 |
|-----|--------|------|------|
| **前端** | Vue 3 + TypeScript + Vite + Electron | Web 应用、桌面应用、浏览器插件 | TypeScript |
| **引擎** | Python + 组件化架构 + WebSocket | 工作流执行、20+ 原子能力组件 | Python 3.13 |
| **后端 (Java)** | Spring Boot + MyBatis-Plus | 机器人管理、资源管理 | Java 8+ |
| **后端 (Python)** | FastAPI + SQLAlchemy | AI 服务、OpenAPI 服务 | Python 3.11+ |

### 架构图

```
┌──────────────────────────────────────────────────────┐
│                  Frontend (Electron)                  │
│              Vue 3 + TypeScript + Vite                │
└──────────────┬─────────────────────┬─────────────────┘
               │ WebSocket           │ HTTP/REST
               ▼                     ▼
┌──────────────────────┐  ┌─────────────────────────────┐
│    Engine (Python)    │  │     Backend Services         │
│  ┌─────────────────┐ │  │  ┌────────────┬────────────┐ │
│  │   scheduler     │ │  │  │ robot-svc  │ resource   │ │
│  │   executor      │ │  │  │ (Java)     │ (Java)     │ │
│  │   20+ 组件      │ │  │  ├────────────┼────────────┤ │
│  └─────────────────┘ │  │  │ ai-svc     │ openapi    │ │
│                       │  │  │ (Python)   │ (Python)   │ │
└───────────────────────┘  │  └────────────┴────────────┘ │
                           └──────────────┬───────────────┘
                                          │
                           ┌──────────────▼───────────────┐
                           │   MySQL · Redis · MinIO       │
                           └───────────────────────────────┘
```

---

## 🔧 开发环境准备

### 必备工具

| 工具 | 版本要求 | 用途 | 安装指引 |
|-----|---------|------|---------|
| **Node.js** | ≥ 22 | 前端开发 | [nodejs.org](https://nodejs.org/) |
| **pnpm** | ≥ 9 | 前端包管理 | `npm install -g pnpm@latest` |
| **Python** | 3.13.x | 引擎 / AI 服务 | [python.org](https://www.python.org/) |
| **uv** | ≥ 0.8 | Python 包管理 | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| **Java JDK** | 8+（robot-service）/ 21+（resource-service） | 后端 Java 服务 | [Adoptium](https://adoptium.net/) |
| **Maven** | ≥ 3.6 | Java 构建 | [maven.apache.org](https://maven.apache.org/) |
| **Docker** | latest | 基础设施服务 | [docker.com](https://www.docker.com/) |
| **Git** | latest | 版本控制 | [git-scm.com](https://git-scm.com/) |

### 按开发场景选择

> 💡 不需要安装所有工具，按您参与的模块选择即可。

| 开发场景 | 需要安装的工具 |
|---------|--------------|
| 仅前端开发 | Node.js, pnpm |
| 仅引擎开发 | Python 3.13, uv |
| 仅后端 Java 服务 | JDK, Maven, Docker（数据库） |
| 仅后端 Python 服务 | Python 3.11+, uv, Docker（数据库） |
| 引擎 + 前端联调 | Node.js, pnpm, Python 3.13, uv |
| 全栈开发 | 全部工具 |

---

## 📂 项目结构说明

```
astron-rpa/
├── frontend/                   # 前端工程 (pnpm monorepo)
│   ├── packages/
│   │   ├── web-app/            # Web 应用
│   │   ├── electron-app/       # Electron 桌面应用
│   │   └── ...
│   └── locales/                # 国际化资源
│
├── engine/                     # RPA 引擎
│   ├── components/             # 原子能力组件 (20+)
│   ├── shared/                 # 公共基础库
│   ├── servers/                # 引擎内部服务
│   ├── scripts/                # 构建脚本
│   └── main.py                 # 调试启动入口
│
├── backend/                    # 后端服务
│   ├── robot-service/          # 机器人核心服务 (Java/Spring Boot)
│   ├── resource-service/       # 资源管理服务 (Java/Spring Boot)
│   ├── ai-service/             # AI 服务 (Python/FastAPI)
│   ├── openapi-service/        # OpenAPI 服务 (Python/FastAPI)
│   └── rpa-auth/               # 认证服务
│
├── docker/                     # Docker 部署配置
├── resources/                  # 运行时资源与配置
├── docs/                       # 项目文档
├── scripts/                    # 全局脚本
├── Makefile                    # 工程自动化命令
└── build.bat                   # 一键构建脚本
```

---

## 🖥️ 前端开发

> **技术栈**: Vue 3 + TypeScript + Vite + Electron + Ant Design Vue  
> **文档**: [frontend/README.zh.md](frontend/README.zh.md)

### 快速开始

```bash
cd frontend

# 📦 安装依赖
pnpm install

# ⚙️ 设置环境变量
pnpm set-env

# 🌐 启动 Web 开发服务器
pnpm dev:web

# 🖥️ 或启动 Electron 桌面开发 (需要后端服务)
pnpm dev:desktop
```

### 常用命令

| 命令 | 说明 |
|-----|------|
| `pnpm dev:web` | 启动 Web 开发服务器 |
| `pnpm dev:desktop` | 启动 Electron 桌面应用（开发模式） |
| `pnpm build:web` | 构建 Web 生产版本 |
| `pnpm build:desktop` | 构建桌面应用安装包 |
| `pnpm test` | 运行 Vitest 单元测试 |
| `pnpm lint:fix` | ESLint 自动修复 |
| `pnpm i18n` | 更新国际化资源 |

### 前端项目结构

前端使用 pnpm workspaces 管理 monorepo，核心包位于 `packages/` 下。详见 [frontend/README.zh.md](frontend/README.zh.md)。

---

## ⚙️ 引擎开发

> **技术栈**: Python 3.13 + uv 包管理 + 组件化架构  
> **文档**: [engine/README.zh.md](engine/README.zh.md)

### 快速开始

```bash
cd engine

# 📦 同步所有依赖（含 20+ 组件包）
uv sync

# 🚀 启动引擎调试（含 meta 构建）
uv run main.py

# 查看输出中的 route_port，如：
# scheduler startup_event: route_port=13159
```

### 组件开发

每个 `engine/components/astronverse-*` 子目录是一个独立的 Python 包（原子能力组件）。

```bash
# 生成单个组件的 meta 配置
cd engine/components/astronverse-browser
uv run meta.py

# 生成所有组件的 meta 并合并为全局配置
cd engine/scripts
uv run meta_build.py

# 运行组件测试
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

详见 [engine/components/README.zh.md](engine/components/README.zh.md)。

---

## 🗄️ 后端服务开发

后端包含 4 个独立微服务：2 个 Java 服务 + 2 个 Python 服务。

### 基础设施依赖

所有后端服务都依赖 MySQL 和 Redis，建议使用 Docker 启动：

```bash
cd docker
docker compose up -d mysql redis
```

---

### robot-service（Java / Spring Boot）

> **端口**: 8040 · **JDK**: 8+ · **框架**: Spring Boot 2.3.11  
> **文档**: [backend/robot-service/README.zh.md](backend/robot-service/README.zh.md)

机器人核心服务，负责机器人管理、流程编排、计划任务、监控审计等。

```bash
cd backend/robot-service

# 构建
mvn clean package -DskipTests

# 启动（使用本地配置）
java -jar target/robot-*.jar --spring.profiles.active=local

# 运行测试
mvn test
```

---

### resource-service（Java / Spring Boot）

> **端口**: 8030 · **JDK**: 21+ · **框架**: Spring Boot 3.2.4  
> **文档**: [backend/resource-service/README.zh.md](backend/resource-service/README.zh.md)

资源管理服务，负责文件上传/下载、S3 对象存储、视频处理。

```bash
cd backend/resource-service

# 构建
mvn clean package -DskipTests

# 启动
java -jar target/resource-*.jar

# 运行测试
mvn test
```

---

### ai-service（Python / FastAPI）

> **端口**: 8010 · **Python**: ≥ 3.13 · **框架**: FastAPI  
> **文档**: [backend/ai-service/README.zh.md](backend/ai-service/README.zh.md)

AI 服务，提供 AI 聊天、OCR 识别、验证码识别、积分管理等能力。

```bash
cd backend/ai-service

# 同步依赖
uv sync

# 启动开发模式
uv run python run.py dev
```

---

### openapi-service（Python / FastAPI）

> **端口**: 8020 · **Python**: ≥ 3.11 · **框架**: FastAPI  
> **文档**: [backend/openapi-service/README.zh.md](backend/openapi-service/README.zh.md)

OpenAPI 服务，负责工作流管理、WebSocket 通信、MCP 协议支持。

```bash
cd backend/openapi-service

# 同步依赖
uv sync

# 启动开发模式
uv run python run.py dev

# 或使用 uvicorn 直接启动
uvicorn app.main:app --port 8020 --reload
```

---

## 🔗 前后端联调

### 引擎 + 前端联调

这是最常见的开发场景，引擎在本地运行，前端 Electron 直连引擎。

**终端 1 — 启动引擎：**
```bash
cd engine
uv sync
uv run main.py
# 📝 记下输出的 route_port (如 13159)
```

**终端 2 — 启动前端：**
```bash
cd frontend
pnpm install
set PORT=13159 && pnpm dev:desktop
```

> 前端会自动跳过内置引擎启动，直连本地 `route_port` 端口的引擎服务。

### 完整栈联调

需要全部服务运行时，使用 Docker 启动基础设施和后端服务：

```bash
# 终端 1: 启动基础设施 + 后端
cd docker
cp .env.example .env
# 修改 .env 中 CASDOOR_EXTERNAL_ENDPOINT 为实际 IP
docker compose up -d

# 终端 2: 启动引擎
cd engine
uv run main.py

# 终端 3: 启动前端
cd frontend
set PORT=13159 && pnpm dev:desktop
```

---

## 📜 Makefile 工程命令

项目根目录的 `Makefile` 提供了统一的工程自动化命令：

```bash
# 查看所有可用命令
make help

# 代码格式化
make fmt              # 所有语言格式化
make fmt-ts           # TypeScript 格式化
make fmt-java         # Java 格式化
make fmt-python       # Python 格式化

# 代码检查
make check            # 快速检查
make check-all        # 全量检查

# 项目状态
make project-status   # 项目状态概览
make dev-setup        # 开发环境设置
```

---

## 📏 代码规范

### 前端 (TypeScript)

| 工具 | 用途 | 配置文件 |
|-----|------|---------|
| ESLint | 代码检查 | `frontend/eslint.config.mjs` |
| Prettier | 代码格式化 | 内置于 ESLint 配置 |
| Vitest | 单元测试 | `frontend/vitest.config.ts` |

```bash
cd frontend
pnpm lint:fix    # 自动修复
pnpm test        # 运行测试
```

### 引擎 (Python)

| 工具 | 用途 | 配置文件 |
|-----|------|---------|
| Ruff | 代码格式化 | `engine/.ruff.toml` |
| pylint | 代码检查 | - |
| pytest | 单元测试 | - |

```bash
cd engine
uv run ruff check .     # 代码检查
uv run ruff format .    # 自动格式化
uv run pytest           # 运行测试
```

### 后端 Java 服务

| 工具 | 用途 | 配置文件 |
|-----|------|---------|
| Checkstyle | 代码风格检查 | `backend/*/checkstyle.xml` |
| PMD | 静态分析 | `backend/*/pmd-ruleset.xml` |
| SpotBugs | Bug 检测 | `backend/*/spotbugs-exclude.xml` |

```bash
cd backend/robot-service
mvn checkstyle:check    # 代码风格检查
mvn pmd:check           # 静态分析
mvn test                # 运行测试
```

---

## 🐳 Docker 本地开发

### 仅启动基础设施

开发后端服务时，通常只需要数据库和缓存：

```bash
cd docker
docker compose up -d mysql redis
```

### 启动全部服务端

```bash
cd docker
cp .env.example .env
# 编辑 .env 配置
docker compose up -d
```

### 服务端口一览

| 服务 | 端口 | 说明 |
|-----|------|------|
| Nginx 网关 | 32742 | 后端 API 统一入口 |
| Casdoor | 8000 | SSO 认证服务 |
| robot-service | 8040 | 机器人核心服务 |
| resource-service | 8030 | 资源管理服务 |
| ai-service | 8010 | AI 服务 |
| openapi-service | 8020 | OpenAPI 服务 |
| MySQL | 3306 | 数据库 |
| Redis | 6379 | 缓存 |

---

## ❓ 常见问题

<details>
<summary><b>Q: uv sync 失败或依赖冲突？</b></summary>

```bash
# 清理 uv 缓存
uv cache clean

# 删除虚拟环境重建
rm -rf .venv
uv sync
```

</details>

<details>
<summary><b>Q: pnpm install 失败？</b></summary>

```bash
# 清理 pnpm 缓存
pnpm store prune

# 删除 node_modules 重装
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

</details>

<details>
<summary><b>Q: 前端无法连接引擎？</b></summary>

- 确认引擎已启动并输出 `route_port`
- 确认前端启动前设置了 `PORT` 环境变量
- 检查端口是否被占用：`netstat -ano | findstr :13159`

</details>

<details>
<summary><b>Q: Java 服务编译失败？</b></summary>

- 检查 JDK 版本：robot-service 需要 JDK 8+，resource-service 需要 JDK 21+
- 检查 Maven 版本：需要 3.6+
- 确认 Maven 仓库可访问（可配置国内镜像）

</details>

<details>
<summary><b>Q: Docker 服务无法启动？</b></summary>

```bash
# 检查端口占用
netstat -ano | findstr :3306
netstat -ano | findstr :6379

# 查看服务日志
docker compose logs -f

# 重启服务
docker compose down
docker compose up -d
```

</details>

---

## 📚 更多文档

| 文档 | 说明 |
|-----|------|
| [BUILD_GUIDE.zh.md](BUILD_GUIDE.zh.md) | 部署与打包指南 |
| [engine/README.zh.md](engine/README.zh.md) | 引擎开发详细文档 |
| [engine/components/README.zh.md](engine/components/README.zh.md) | 原子能力组件开发指南 |
| [frontend/README.zh.md](frontend/README.zh.md) | 前端工程详细文档 |
| [docker/QUICK_START.md](docker/QUICK_START.md) | Docker 部署详细指南 |
| [FAQ.zh.md](FAQ.zh.md) | 常见问题 |

---

<div align="center">

**如有问题请联系项目维护者，或在 [GitHub Issues](https://github.com/iflytek/astron-rpa/issues) 中提交反馈。**

</div>
