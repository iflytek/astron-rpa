<div align="center">

# 🚀 AstronRPA 快速开始指南

[![Python Version](https://img.shields.io/badge/Python-3.13.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node Version](https://img.shields.io/badge/Node.js-22+-green?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange)](LICENSE)

**快速、简单、强大的 RPA 自动化平台部署指南**

[快速开始](#-环境准备) · [服务端部署](#-服务端部署-docker) · [客户端部署](#-客户端部署-本地) · [常见问题](#-常见问题)

</div>

---

## 📋 目录

- [系统要求](#-系统要求)
- [环境准备](#-环境准备)
- [部署架构说明](#-部署架构说明)
- [服务端部署 (Docker)](#-服务端部署-docker)
- [客户端部署 (本地)](#-客户端部署-本地)
- [开发环境搭建](#-开发环境搭建)
- [常见问题](#-常见问题)

## 💻 系统要求

### 操作系统
| 操作系统 | 版本要求 | 支持状态 |
|---------|---------|---------|
| Windows | 10/11 | ✅ 主要支持 |

### 硬件配置
| 配置项 | 最低要求 | 推荐配置 |
|-------|---------|---------|
| **CPU** | 2 核心 | 4 核心+ |
| **内存** | 4GB | 8GB+ |
| **磁盘** | 10GB 可用空间 | 20GB+ |
| **网络** | 稳定的互联网连接 | - |

### 环境依赖
| 工具 | 版本要求 | 说明 |
|-----|---------|------|
| **Node.js** | >= 22 | JavaScript 运行时 |
| **Python** | 3.13.x | RPA 引擎核心 |
| **Java** | JDK 8+ | 后端服务运行时 |
| **pnpm** | >= 9 | Node.js 包管理器 |
| **rustc** | >= 1.90.0 | Tauri 应用构建 |
| **UV** | 0.8+ | Python 包管理工具 |
| **7-Zip** | - | 创建部署归档文件 |
| **SWIG** | - | 连接 Python 与 C/C++ |

## 🛠️ 环境准备

### 1️⃣ Python (3.13.x)

> 🐍 **核心依赖** · AstronRPA 需要 Python 3.13.x 版本作为 RPA 引擎核心

<details>
<summary>📦 <b>安装方式（点击展开）</b></summary>

#### 方式 1: 官方下载（推荐）
```bash
# 访问 https://www.python.org/downloads/
# 下载 Python 3.13.x 版本并安装
```

#### 方式 2: 使用 Chocolatey
```bash
choco install python --version=3.13.0
```

</details>

#### 📍 Python 安装路径说明

安装完成后，您需要记住 Python 的安装路径，因为后续配置可能会用到：

| 安装方式 | 典型路径 |
|---------|---------|
| 🟢 官方安装包 | `C:\Users\{用户名}\AppData\Local\Programs\Python\Python313\` |
| 🔵 Chocolatey | `C:\Python313\` 或 `C:\tools\python3\` |

**💡 重要提示：**
- ✓ Python 可执行文件：`{安装目录}\python.exe`
- ✓ 示例：`C:\Users\{用户名}\AppData\Local\Programs\Python\Python313\python.exe`

### 2️⃣ UV (0.8+)

> ⚡ **快速包管理** · 新一代 Python 包管理器，比 pip 快 10-100 倍

<details>
<summary>📦 <b>安装方式（点击展开）</b></summary>

```powershell
# 方式 1: 官方安装脚本（推荐）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 方式 2: 使用 pip
pip install uv

# 方式 3: 使用 Chocolatey
choco install uv
```

</details>

#### ✅ 验证安装
```bash
uv --version
# ✓ 应该显示类似：uv 0.8.x (xxxxx)
```

**📖 了解更多**: [UV 官方文档](https://docs.astral.sh/uv/)

### 3️⃣ pnpm (9+)

> 📦 **高效包管理** · 节省磁盘空间的 Node.js 包管理器

<details>
<summary>📦 <b>安装方式（点击展开）</b></summary>

```bash
# 方式 1: 使用 npm（推荐）
npm install -g pnpm@latest

# 方式 2: Windows PowerShell
iwr https://get.pnpm.io/install.ps1 -useb | iex

# 方式 3: macOS/Linux
curl -fsSL https://get.pnpm.io/install.sh | sh -

# 方式 4: Homebrew (macOS)
brew install pnpm
```

</details>

#### ✅ 验证安装
```bash
pnpm --version
# ✓ 应该显示 9.x.x 或更高版本
```

**📖 了解更多**: [pnpm 官方文档](https://pnpm.io/)


### 4️⃣ Tauri

> 🪟 **桌面应用框架** · 用于构建跨平台桌面应用

#### 🔧 前置工具安装

<details>
<summary><b>步骤 1: Microsoft Visual Studio C++ 生成工具</b></summary>

<br>

您需要安装 Microsoft C++ 生成工具。最简单的方法是下载 **Visual Studio 2022 生成工具**。

**安装时请勾选：**
- ✅ C++ 生成工具
- ✅ Windows 10 SDK

> **💡 提示：** 使用 Visual Studio 生成工具 2022 安装程序

</details>

<details>
<summary><b>步骤 2: WebView2</b></summary>

<br>

> **📝 备注**  
> Windows 10 (Version 1803+) 和 Windows 11 已预装 WebView2

Tauri 需要 WebView2 才能在 Windows 上呈现网页内容。从微软网站下载和运行**常青版引导程序**即可。

**🔍 故障排除：** 如果遇到问题（特别是 Windows on ARM），请手动选择适合您架构的版本。

</details>

<details>
<summary><b>步骤 3: Rust</b></summary>

<br>

前往 [Rust 安装地址](https://www.rust-lang.org/zh-CN/tools/install) 来安装 rustup (Rust 安装程序)。

**或者使用 winget 安装：**
```bash
winget install --id Rustlang.Rustup
```

> **⚠️ 重要提醒**  
> 安装后必须重新启动终端，某些情况下需要重新启动 Windows。

</details>

**📖 了解更多**: [Tauri 官方文档](https://v1.tauri.app/zh-cn/v1/guides/getting-started/prerequisites/)


### 5️⃣ Docker

> 🐳 **容器化平台** · 用于服务端快速部署

<details>
<summary>📥 <b>下载安装（点击展开）</b></summary>

| 平台 | 下载链接 |
|-----|---------|
| 🪟 Windows/Mac | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| 🐧 Linux | [Docker Engine](https://docs.docker.com/engine/install/) |

</details>

#### ✅ 验证安装
```bash
docker --version
docker compose --version
# ✓ 确认 Docker 和 Docker Compose 都已正确安装
```

---

### 6️⃣ 7-Zip

> 📦 **压缩工具** · 用于创建部署归档文件

<details>
<summary>📥 <b>下载安装（点击展开）</b></summary>

**官网下载：** https://www.7-zip.org/

下载并安装到系统，或解压到自定义目录

</details>

#### ✅ 验证安装
```bash
# 如果安装到系统路径
7z

# 或者使用完整路径
"C:\Program Files\7-Zip\7z.exe"
```

---

### 7️⃣ SWIG

> 🔗 **接口生成器** · 用于连接 Python 与 C/C++ 程序

<details>
<summary>📥 <b>安装步骤（点击展开）</b></summary>

#### 步骤 1：下载 SWIG
访问 http://www.swig.org/download.html  
下载 `swigwin-x.x.x.zip` 解压到任意目录

#### 步骤 2：添加到系统环境变量
将 `swig.exe` 所在目录添加到 PATH 环境变量  
例如：`C:\swig\swigwin-4.1.1`

#### 步骤 3：验证安装
```bash
swig -version
# ✓ 确认 SWIG 已正确安装
```

</details>

## 🏗️ 部署架构说明

AstronRPA 采用 **服务端-客户端** 架构：

```
┌─────────────────────────────────────┐
│              客户端                  │
│  ┌─────────────┐ ┌─────────────────┐ │
│  │  桌面应用    │ │   RPA 执行引擎   │ │
│  │ (Tauri App) │ │  (Python Engine)│ │
│  └─────────────┘ └─────────────────┘ │
│             │                       │
│             │ WebSocket/HTTP        │
└─────────────┼───────────────────────┘
              │
              │ 网络连接
              │
┌─────────────┼───────────────────────┐
│             ▼        服务端          │
│  ┌─────────────┐ ┌─────────────────┐ │
│  │   Web 界面   │ │   后端服务       │ │
│  │  (Vue App)  │ │ (Java + Python) │ │
│  └─────────────┘ └─────────────────┘ │
│         ┌─────────────────────────┐   │
│         │     数据库 + Redis      │   │
│         └─────────────────────────┘   │
└─────────────────────────────────────┘
```

### 部署说明

1. **服务端部署** - 使用 Docker 快速部署
   - Web 管理界面 
   - 后端 API 服务
   - 数据库和缓存
   - AI 服务

2. **客户端部署** - 使用打包脚本部署
   - RPA 执行引擎
   - 桌面管理应用
   - 连接到服务端进行任务执行

## 🌐 服务端部署 (Docker)

> **快速部署** · 使用 Docker Compose 一键启动所有服务端组件

服务端提供 Web 管理界面、API 服务、数据库等核心服务。

---

### 📦 部署步骤

#### 步骤 1️⃣: 克隆仓库

```bash
git clone https://github.com/iflytek/astron-rpa.git
cd astron-rpa
```

#### 步骤 2️⃣: 启动服务端

```bash
# 进入 Docker 目录
cd docker

# 🚀 启动所有服务
docker compose up -d

# 📊 检查服务状态
docker compose ps
```

<details>
<summary>💡 <b>预期输出示例</b></summary>

```
NAME                STATUS              PORTS
robot-service       Up 30 seconds       0.0.0.0:8080->8080/tcp
ai-service          Up 30 seconds       0.0.0.0:8001->8001/tcp
openapi-service     Up 30 seconds       0.0.0.0:8002->8002/tcp
mysql               Up 30 seconds       0.0.0.0:3306->3306/tcp
redis               Up 30 seconds       0.0.0.0:6379->6379/tcp
```

</details>

#### 步骤 3️⃣: 验证服务端部署

```bash
# 📝 查看服务日志
docker compose logs -f

# ✅ 检查各服务健康状态
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

#### 步骤 4️⃣: 访问 Web 界面

| 服务 | 地址 | 说明 |
|-----|------|------|
| 🖥️ **管理界面** | http://localhost:8080 | 主要管理控制台 |
| 📚 **API 文档** | http://localhost:8080/api-docs | Swagger API 文档 |
| 📊 **监控面板** | http://localhost:8080/monitoring | 系统监控面板 |

---

### 🔧 服务端管理命令

```bash
# 🛑 停止服务
docker compose down

# 🔄 重启服务
docker compose restart

# 📋 查看特定服务日志
docker compose logs -f robot-service

# ⬆️ 更新镜像
docker compose pull
docker compose up -d
```

**📖 详细配置**: [服务端部署指南](../docker/QUICK_START.md)



## 💻 客户端部署 (本地)

> **本地部署** · 在执行 RPA 任务的机器上部署引擎和桌面应用

客户端包含 RPA 执行引擎和桌面管理应用，需要部署到执行 RPA 任务的机器上。

---

### 🎯 一键打包部署方式

适合生产环境和最终用户。

#### 🪟 Windows 环境

<details>
<summary><b>步骤 1️⃣: 准备 Python 环境</b></summary>

<br>

确保已安装 Python 3.13.x 到本地目录（如 `C:\Python313`）。

**环境目录结构：**
```
Python313/
├─ DLLs/
├─ Doc/
├─ include/
├─ Lib/
├─ libs/
├─ Scripts/
├─ tcl/
│
├─ LICENSE.txt
├─ NEWS.txt
├─ python.exe
├─ python3.dll
├─ python313.dll
├─ pythonw.exe
├─ vcruntime140.dll
└─ vcruntime140_1.dll
```

> **⚠️ 重要提示：** 请使用纯净的 Python 安装，避免安装额外第三方包，以减小打包体积。

</details>

<details>
<summary><b>步骤 2️⃣: 运行打包脚本</b></summary>

<br>

### 基础用法

在项目根目录执行构建脚本：

```bash
# 🚀 完整构建（引擎 + 前端）
./build.bat --python-exe "C:\Program Files\Python313\python.exe"

# 或使用默认配置（如果 Python 在默认路径）
./build.bat

# ⏳ 请等待操作完成
# ✅ 当控制台显示 "Full Build Complete!" 时表示构建成功
```

**执行流程：**
1. ✅ 检测/复制 Python 环境到 `build/python_core`
2. ✅ 安装 RPA 引擎依赖包
3. ✅ 压缩 Python 核心到 `resources/python_core.7z`
4. ✅ 安装前端依赖
5. ✅ 构建前端 Web 应用
6. ✅ 构建 Tauri 桌面应用

### 高级选项

查看所有可用参数：

```bash
./build.bat --help
```

**常用参数组合：**

```bash
# 🔧 指定 Python 路径
./build.bat --python-exe "D:\Python313\python.exe"

# 🔧 指定 7-Zip 路径
./build.bat --sevenz-exe "D:\7-Zip\7z.exe"

# ⏭️ 只构建引擎，跳过前端
./build.bat --skip-frontend

# ⏭️ 只构建前端，跳过引擎
./build.bat --skip-engine

# 🔀 组合使用短参数
./build.bat -p "D:\Python313\python.exe" -s "D:\7-Zip\7z.exe"
```

**参数说明：**
| 参数 | 简写 | 说明 |
|------|------|------|
| `--python-exe <路径>` | `-p` | 指定 Python 可执行文件路径 |
| `--sevenz-exe <路径>` | `-s` | 指定 7-Zip 可执行文件路径 |
| `--skip-engine` | - | 跳过引擎（Python）构建 |
| `--skip-frontend` | - | 跳过前端构建 |
| `--help` | `-h` | 显示帮助信息 |

### 手动构建前端

如果需要单独手动构建前端，可以执行以下步骤：

<details>
<summary>点击展开手动构建步骤</summary>

```bash
cd frontend

# 📦 安装依赖
pnpm install

# ⚙️ 配置环境变量
copy packages\web-app\.env.example packages\web-app\.env

# 🏗️ 构建 Web 应用
pnpm build:web

# 🖥️ 构建桌面应用
pnpm build:tauri-debug
```

> **提示：** 使用 `build.bat --skip-engine` 可以自动完成上述前端构建步骤。

</details>

</details>

<details>
<summary><b>步骤 3️⃣: 安装 MSI 安装包</b></summary>

<br>

**打包完成路径：**
```
\frontend\packages\tauri-app\src-tauri\target\debug\bundle\msi\
```

双击 MSI 文件进行安装。

</details>

<details>
<summary><b>步骤 6️⃣: 配置服务端地址</b></summary>

<br>

在安装目录下的 `resources/conf.json` 中修改服务端地址：

```json
{
  "remote_addr": "http://YOUR_SERVER_ADDRESS/",
  "pypi_remote": ""
}
```

> **💡 提示：** 将 `YOUR_SERVER_ADDRESS` 替换为实际的服务端地址

</details>

---

### 📦 部署输出

```
src-tauri/resources/
└── python_core.7z     # RPA 执行引擎打包文件
```

---

### 🌐 开发服务器地址

| 服务 | 地址 | 说明 |
|-----|------|------|
| 🌐 **Web 应用** | http://localhost:5173 | 开发前端界面 |
| 🖥️ **桌面应用** | 自动启动窗口 | Tauri 桌面客户端 |
| 🔌 **主服务 API** | http://localhost:8080 | Robot 服务 API |
| 🤖 **AI 服务 API** | http://localhost:8001 | AI 智能服务 |
| 🔗 **OpenAPI 服务** | http://localhost:8002 | OpenAPI 服务 |

---

## 🔍 完整部署验证

### ✅ 步骤 1: 服务端检查

```bash
# 📊 检查 Docker 服务状态
docker compose ps

# 🔍 验证 API 响应
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/status

# 🌐 访问 Web 界面
# 浏览器打开: http://localhost:8080
```

<details>
<summary>💡 <b>健康检查预期响应</b></summary>

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "up",
    "redis": "up",
    "api": "up"
  }
}
```

</details>

### ✅ 步骤 2: 连接测试

```bash
# 🔌 测试 WebSocket 连接
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
     http://localhost:8080/ws
```

**后续验证：**
- ✓ 在 Web 界面中检查客户端节点状态
- ✓ 创建简单测试任务验证执行

## ❓ 常见问题

### 🌐 服务端相关

<details>
<summary><b>Q: Docker 服务启动失败？</b></summary>

<br>

```bash
# 🔍 检查端口占用
netstat -tulpn | grep :8080

# ✅ 检查 Docker 状态
docker --version
docker compose --version

# 📋 查看详细错误日志
docker compose logs
```

**常见原因：**
- ❌ 端口被占用（8080、3306、6379）
- ❌ Docker 服务未启动
- ❌ 资源不足（内存/磁盘空间）

</details>

<details>
<summary><b>Q: 数据库连接失败？</b></summary>

<br>

```bash
# 📊 检查 MySQL 容器状态
docker compose ps mysql

# 📝 查看 MySQL 日志
docker compose logs mysql

# 🔄 重启数据库服务
docker compose restart mysql
```

</details>

---

### 💻 客户端相关

<details>
<summary><b>Q: Python 环境复制失败？</b></summary>

<br>

```bash
# 🔍 检查 Python 安装路径
where python  # Windows
which python  # Linux/macOS
```

**解决方案：**
- ✓ 确保 Python 目录存在且可读
- ✓ 使用管理员权限运行脚本
- ✓ 检查磁盘空间是否充足

</details>

<details>
<summary><b>Q: 打包脚本执行失败？</b></summary>

<br>

```bash
# ✅ 检查 7-Zip 路径
"C:\Program Files\7-Zip\7z.exe"

# 🔧 手动指定路径
pack.bat "D:\Tools\7-Zip\7z.exe" "C:\Python313"

# 💾 检查磁盘空间
dir  # Windows 检查可用空间
```

</details>

---

### 🔌 连接相关

<details>
<summary><b>Q: 客户端无法连接服务端？</b></summary>

<br>

```bash
# 🌐 检查网络连通性
ping localhost
telnet localhost 8080

# 🛡️ 检查防火墙设置
# Windows: 控制面板 > 系统和安全 > Windows Defender 防火墙
# Linux: ufw status

# ✅ 检查服务端健康状态
curl http://localhost:8080/health
```

**常见原因：**
- ❌ 服务端未启动
- ❌ 防火墙拦截
- ❌ 网络不通
- ❌ 配置文件中地址错误

</details>

<details>
<summary><b>Q: WebSocket 连接失败？</b></summary>

<br>

```bash
# 🔌 检查 WebSocket 端点
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     http://localhost:8080/ws

# 🔍 检查代理设置
echo $http_proxy
echo $https_proxy
```

**解决方案：**
- ✓ 确认服务端 WebSocket 服务正常
- ✓ 检查是否有代理影响连接
- ✓ 验证防火墙规则

</details>

---

### 🏗️ 构建相关

<details>
<summary><b>Q: 前端构建失败？</b></summary>

<br>

```bash
# 🧹 清理缓存
pnpm store prune
rm -rf node_modules pnpm-lock.yaml

# 📦 重新安装
pnpm install

# ✅ 检查 Node.js 版本
node --version  # 需要 22+
```

**常见原因：**
- ❌ Node.js 版本不符合要求
- ❌ 依赖包版本冲突
- ❌ 缓存损坏

</details>

<details>
<summary><b>Q: Tauri 构建失败？</b></summary>

<br>

```bash
# ⬆️ 更新 Rust 工具链
rustup update

# 🧹 清理构建缓存
cargo clean

# 📦 检查系统依赖 (Linux)
sudo apt install libwebkit2gtk-4.0-dev build-essential curl wget \
  libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

</details>

<details>
<summary><b>Q: 安装 pywinhook 失败报错 swig.exe 不存在？</b></summary>

<br>

**错误信息：**
```
error: Microsoft Visual C++ 14.0 is required
或
swig.exe not found
```

**解决步骤：**

1️⃣ **下载 SWIG**
   - 访问 http://www.swig.org/download.html
   - 下载 `swigwin-x.x.x.zip` 解压到任意目录

2️⃣ **添加到系统环境变量**
   - 将 `swig.exe` 所在目录添加到 PATH 环境变量
   - 例如：`C:\swig\swigwin-4.1.1`

3️⃣ **验证安装**
   ```bash
   swig -version
   ```

4️⃣ **重新安装 pywinhook**
   ```bash
   pip install pywinhook
   ```

</details>

## 📞 获取帮助

<div align="center">

**遇到问题？我们随时为您提供帮助！**

</div>

| 渠道 | 链接 | 说明 |
|-----|------|------|
| 📧 **技术支持** | [cbg_rpa_ml@iflytek.com](mailto:cbg_rpa_ml@iflytek.com) | 直接联系技术团队 |
| 💬 **社区讨论** | [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions) | 与社区交流心得 |
| 🐛 **问题报告** | [GitHub Issues](https://github.com/iflytek/astron-rpa/issues) | 提交 Bug 和功能建议 |
| 📖 **完整文档** | [项目文档](README.zh.md) | 查阅详细使用文档 |

---

## 🎯 下一步

<div align="center">

**✨ 恭喜您完成部署！现在可以开启 RPA 自动化之旅了 ✨**

</div>

<br>


| 步骤 | 内容 | 链接 |
|-----|------|------|
| 1️⃣ | **📚 学习使用** | 阅读 [用户指南](README.zh.md) 了解如何创建 RPA 流程 |
| 2️⃣ | **🔧 组件开发** | 参考 [组件开发指南](engine/components/) 开发自定义组件 |
| 3️⃣ | **🤝 参与贡献** | 查看 [贡献指南](CONTRIBUTING.md) 参与项目开发 |
| 4️⃣ | **📱 部署到生产** | 参考 [生产部署指南](docker/PRODUCTION.md) 进行生产环境部署 |

---

<div align="center">

### 🎉 部署完成！

**您已成功部署 AstronRPA 服务端和客户端**

现在可以开始创建强大的 RPA 自动化流程了！

<br>

![AstronRPA](https://img.shields.io/badge/AstronRPA-Ready-success?style=for-the-badge)

**Happy Automating! 🤖✨**

</div>