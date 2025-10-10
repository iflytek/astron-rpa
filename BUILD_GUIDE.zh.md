# 🚀 AstronRPA 快速开始指南

本指南将帮助您快速搭建 AstronRPA 完整环境，包括服务端和客户端的部署。

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
- **Windows**: 10/11 (主要支持)

### 硬件配置
- **CPU**: 2 核心或更多
- **内存**: 4GB 或更多 (推荐 8GB+)
- **磁盘**: 10GB 可用空间
- **网络**: 稳定的互联网连接

## 🛠️ 环境准备

### 1. Python 3.13.x

AstronRPA 需要 Python 3.13.x 版本。

#### Windows
```bash
# 方式1: 官方下载
# 访问 https://www.python.org/downloads/
# 下载 Python 3.13.x 版本并安装
# 安装时建议勾选 "Add Python to PATH"

# 方式2: 使用 Chocolatey
choco install python --version=3.13.0

# 方式3: 使用 Scoop
scoop install python
```

#### 验证安装
```bash
python --version
# 或
python3 --version
# 应该显示 Python 3.13.x
```

#### Python 安装路径说明
安装完成后，您需要记住Python的安装路径，因为后续配置可能会用到：

**常见安装路径：**
- 官方安装包：`C:\Users\{用户名}\AppData\Local\Programs\Python\Python313\`
- Chocolatey安装：`C:\Python313\` 或 `C:\tools\python3\`
- Scoop安装：`C:\Users\{用户名}\scoop\apps\python\current\`

**重要文件位置：**
- Python可执行文件：安装目录下的 `python.exe`
- 例如：`C:\Users\{用户名}\AppData\Local\Programs\Python\Python313\python.exe`

**查找Python安装路径的方法：**
```bash
# 方法1: 使用where命令
where python

# 方法2: 在Python中查看
python -c "import sys; print(sys.executable)"
```

### 2. UV (Python 包管理器)

UV 是新一代的 Python 包管理器，比 pip 更快更可靠。

#### 安装 UV

**Windows (PowerShell)**
```powershell
# 方式1: 使用官方安装脚本
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 方式2: 使用 pip
pip install uv

# 方式3: 使用 Chocolatey
choco install uv
```

#### 验证安装
```bash
uv --version
# 应该显示版本信息
```

**📖 更多信息**: [UV 官方文档](https://docs.astral.sh/uv/)

### 3. Node.js 22+

#### 官方下载
- **官网**: https://nodejs.org/
- **LTS 版本**: 推荐使用 LTS 版本 (22.x)

#### 使用版本管理器

**Windows (使用 nvm-windows)**
```bash
# 下载安装 nvm-windows: https://github.com/coreybutler/nvm-windows
nvm install 22
nvm use 22
```

#### 验证安装
```bash
node --version
# 应该显示 v22.x.x

npm --version
# 应该显示 npm 版本
```

### 4. pnpm 9+

pnpm 是高效的 Node.js 包管理器。

#### 安装 pnpm
```bash
# 方式1: 使用 npm
npm install -g pnpm@latest

# 方式2: 使用官方安装脚本 (Windows PowerShell)
iwr https://get.pnpm.io/install.ps1 -useb | iex

# 方式3: 使用官方安装脚本 (macOS/Linux)
curl -fsSL https://get.pnpm.io/install.sh | sh -

# 方式4: 使用 Homebrew (macOS)
brew install pnpm
```

#### 验证安装
```bash
pnpm --version
# 应该显示 9.x.x 或更高版本
```

**📖 更多信息**: [pnpm 官方文档](https://pnpm.io/)

### 5. Java JDK 8+

#### 官方下载
- **Oracle JDK**: https://www.oracle.com/java/technologies/downloads/
- **OpenJDK**: https://openjdk.org/install/
- **Amazon Corretto**: https://aws.amazon.com/corretto/

#### 使用包管理器

**Windows**
```bash
# 使用 Chocolatey
choco install openjdk

# 使用 Scoop
scoop install openjdk
```

#### 验证安装
```bash
java -version
javac -version
```

### 6. Tauri

#### 前置工具安装

##### 1. Microsoft Visual Studio C++ 生成工具

您需要安装 Microsoft C++ 生成工具。最简单的方法是下载 **Visual Studio 2022 生成工具**。进行安装选择时，请勾选 "**C++ 生成工具**" 和 "**Windows 10 SDK**"。

> **安装要求：** 使用 Visual Studio 生成工具 2022 安装程序，并勾选 "C++ 构建工具" 和 "Windows 10 SDK"。

##### 2. WebView2

> **📝 备注**  
> 在 Windows 10 (Version 1803 和更高版本，已应用所有更新) 和 Windows 11 上，WebView2 运行时作为操作系统的一部分分发。

Tauri 需要 WebView2 才能在 Windows 上呈现网页内容，所以您必须先安装 WebView2。最简单的方法是从微软网站下载和运行**常青版引导程序**。

安装脚本会自动为您下载适合您架构的版本。不过，如果您遇到问题（特别是 Windows on ARM），您可以自己手动选择正确版本。

##### 3. Rust

最后，请前往 https://www.rust-lang.org/zh-CN/tools/install 来安装 rustup (Rust 安装程序)。

> **⚠️ 重要提醒**  
> 为了使更改生效，您必须重新启动终端，在某些情况下需要重新启动 Windows 本身。

**或者，您可以在 PowerShell 中使用 winget 命令安装程序：**

```bash
winget install --id Rustlang.Rustup
```

**📖 更多信息**: [Tauri 官方文档](https://v1.tauri.app/zh-cn/v1/guides/getting-started/prerequisites/)

### 7. 7-Zip (Windows 打包需要)

#### 下载安装
- **官网**: https://www.7-zip.org/
- 下载并安装到系统，或解压到自定义目录

#### 验证安装
```bash
# 如果安装到系统路径
7z

# 或者使用完整路径
"C:\Program Files\7-Zip\7z.exe"
```

### 8. Docker (服务端部署必需)

#### 官方下载
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
- **Docker Engine** (Linux): https://docs.docker.com/engine/install/

#### 验证安装
```bash
docker --version
docker compose --version
```

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

服务端提供 Web 管理界面、API 服务、数据库等核心服务。

### 1. 克隆仓库
```bash
git clone https://github.com/iflytek/astron-rpa.git
cd astron-rpa
```

### 2. 启动服务端
```bash
# 进入 Docker 目录
cd docker

# 启动服务栈
docker compose up -d

# 检查服务状态
docker compose ps
```

### 3. 验证服务端部署
```bash
# 查看服务日志
docker compose logs -f

# 检查各服务健康状态
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

### 4. 访问 Web 界面
- **管理界面**: http://localhost:8080
- **API 文档**: http://localhost:8080/api-docs
- **监控面板**: http://localhost:8080/monitoring

### 5. 服务端管理
```bash
# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看特定服务日志
docker compose logs -f robot-service

# 更新镜像
docker compose pull
docker compose up -d
```

**📖 详细配置**: [服务端部署指南](../docker/QUICK_START.md)

## 💻 客户端部署 (本地)

客户端包含 RPA 执行引擎和桌面管理应用，需要部署到执行 RPA 任务的机器上。

### 一键打包部署方式

适合生产环境和最终用户。

#### Windows 环境

**1. 准备 Python 环境**
确保已安装 Python 3.13.x 到本地目录（如 `C:\Python313`）。
```
提供环境的基本层级结构如下所示：

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


**2. 运行打包脚本**
```bash
cd engine

# 修改build.bat的第9和10行配置，确保环境正确
# 注意!!! 请确保指定的 Python 解释器为纯净安装，未安装额外第三方包，以避免影响最终打包体积
# set PYTHON_EXE=C:\Program Files\Python313\python.exe
# set SEVENZ_EXE=C:\Program Files\7-Zip\7z.exe

# 执行构建流程，请等待操作完成提示
# 当控制台显示 "Complete!" 时表示构建成功
./build.bat
```

**3. 脚本执行流程**
- ✅ 检测/复制 Python 环境到 `python_core`
- ✅ 安装 RPA 引擎依赖包
- ✅ 构建前端 Web 应用
- ✅ 构建 Tauri 桌面应用
- ✅ 创建部署压缩包并移动到前端打包位置

**4. 部署输出**
```
src-tauri/resources    # 完整客户端包
└── python_core.7z     # RPA 执行引擎
```

**5. 构建前端应用**
```bash
cd frontend

# 安装依赖
pnpm install

# 配置环境变量
copy packages\web-app\.env.example packages\web-app\.env

# 构建 Web 应用
pnpm build:web

# 构建桌面应用
pnpm build:tauri-debug
```

**6. 安装msi安装包**
```
打包完成路径为：
\frontend\packages\tauri-app\src-tauri\target\debug\bundle\msi\
```

**7. 修改配置文件**
```
# 在安装目录下recouces/conf.json中修改服务端地址
{"remote_addr": "http://YOUR_SERVER_ADDRESS/", "pypi_remote": ""}
```

### 开发服务器地址
- **Web 应用**: http://localhost:5173
- **桌面应用**: 自动启动窗口
- **主服务 API**: http://localhost:8080
- **AI 服务 API**: http://localhost:8001
- **OpenAPI 服务**: http://localhost:8002

## 🔍 完整部署验证

### 1. 服务端检查
```bash
# 检查 Docker 服务状态
docker compose ps

# 验证 API 响应
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/status

# 访问 Web 界面
# http://localhost:8080
```

### 2. 连接测试
```bash
# 使用 curl 测试 WebSocket 连接
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
     http://localhost:8080/ws

# 在 Web 界面中检查客户端节点状态
# 创建简单测试任务验证执行
```

## ❓ 常见问题

### 服务端相关

**Q: Docker 服务启动失败？**
```bash
# 检查端口占用
netstat -tulpn | grep :8080

# 检查 Docker 状态
docker --version
docker compose --version

# 查看详细错误日志
docker compose logs
```

**Q: 数据库连接失败？**
```bash
# 检查 MySQL 容器状态
docker compose ps mysql

# 查看 MySQL 日志
docker compose logs mysql

# 重启数据库服务
docker compose restart mysql
```

### 客户端相关

**Q: Python 环境复制失败？**
```bash
# 检查 Python 安装路径
where python  # Windows
which python  # Linux/macOS

# 确保 Python 目录存在且可读
# 使用管理员权限运行脚本
```

**Q: 打包脚本执行失败？**
```bash
# 检查 7-Zip 路径
"C:\Program Files\7-Zip\7z.exe"

# 手动指定路径
pack.bat "D:\Tools\7-Zip\7z.exe" "C:\Python313"

# 检查磁盘空间
dir  # Windows 检查可用空间
```

### 连接相关

**Q: 客户端无法连接服务端？**
```bash
# 检查网络连通性
ping localhost
telnet localhost 8080

# 检查防火墙设置
# Windows: 控制面板 > 系统和安全 > Windows Defender 防火墙
# Linux: ufw status

# 检查服务端健康状态
curl http://localhost:8080/health
```

**Q: WebSocket 连接失败？**
```bash
# 检查 WebSocket 端点
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     http://localhost:8080/ws

# 检查代理设置
echo $http_proxy
echo $https_proxy
```

### 构建相关

**Q: 前端构建失败？**
```bash
# 清理缓存
pnpm store prune
rm -rf node_modules pnpm-lock.yaml

# 重新安装
pnpm install

# 检查 Node.js 版本
node --version  # 需要 22+
```

**Q: Tauri 构建失败？**
```bash
# 更新 Rust 工具链
rustup update

# 清理构建缓存
cargo clean

# 检查系统依赖 (Linux)
sudo apt install libwebkit2gtk-4.0-dev build-essential curl wget libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

**Q: 安装 pywinhook 失败报错 swig.exe 不存在？**
```bash
# 错误信息：error: Microsoft Visual C++ 14.0 is required 或 swig.exe not found

# 步骤1：下载 SWIG
# 访问 http://www.swig.org/download.html
# 下载 swigwin-x.x.x.zip 解压到任意目录

# 步骤2：添加到系统环境变量
# 将 swig.exe 所在目录添加到 PATH 环境变量
# 例如：C:\swig\swigwin-4.1.1

# 解决方案3：验证安装
swig -version

# 然后重新安装 pywinhook
pip install pywinhook
```

## 📞 获取帮助

如果遇到问题，可以通过以下方式寻求帮助:

- 📧 **技术支持**: [cbg_rpa_ml@iflytek.com](mailto:cbg_rpa_ml@iflytek.com)
- 💬 **社区讨论**: [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/iflytek/astron-rpa/issues)
- 📖 **完整文档**: [项目文档](../README.md)

## 🎯 下一步

完成部署后，您可以：

1. **📚 学习使用**: 阅读[用户指南](HOW_TO_RUN.md)了解如何创建 RPA 流程
2. **🔧 组件开发**: 参考[组件开发指南](engine/components/)开发自定义组件
3. **🤝 参与贡献**: 查看[贡献指南](CONTRIBUTING.md)参与项目开发
4. **📱 部署到生产**: 参考[生产部署指南](docker/PRODUCTION.md)进行生产环境部署

---

**🎉 恭喜！** 您已成功部署 AstronRPA 服务端和客户端，现在可以开始创建强大的 RPA 自动化流程了！