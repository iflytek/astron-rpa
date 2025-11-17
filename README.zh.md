# AstronRPA

<div align="center">

![AstronRPA Logo](./docs/images/icon_128px.png)

**🤖 首个完整开源的企业级RPA桌面应用**

[![License](https://img.shields.io/badge/license-Open%20Source-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/iflytek/astron-rpa)](https://github.com/iflytek/astron-rpa/releases)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![GitHub Stars](https://img.shields.io/github/stars/iflytek/astron-rpa?style=social)](https://github.com/iflytek/astron-rpa/stargazers)

[English](README.md) | 简体中文

</div>

## 📋 概述
AstronRPA 是一款企业级机器人流程自动化（RPA）桌面应用。通过可视化设计器支持低代码/无代码开发，用户能快速构建工作流，实现桌面软件和浏览器页面的自动化。

[Astron Agent](https://github.com/iflytek/astron-agent) 是本项目原生支持的Agent平台，用户可在 Astron Agent 中直接调用 RPA 流程节点，也可在 AstronRPA 中使用 Agent 的工作流，实现自动化流程与智能体系统的高效协同，赋能更广泛的业务自动化场景。

## 🎯 为什么选择 AstronRPA？

- **🛠️ 全面自动化支持**：全面覆盖 Windows 桌面各类软件与浏览器页面的自动化，支持包括 WPS、Office 等常用办公软件，金蝶、用友、SAP 等财务及 ERP 系统，以及 IE、Edge、Chrome 等多种浏览器，实现跨应用的端到端自动化。
- **🧩 高度组件化**：内置 300 余项常用原子能力，覆盖UI操作、数据处理、系统交互等常见场景，支持图形化编排与自定义组件扩展，具备高度的灵活性与可维护性。
- **🏭 企业级安全协同**：内置卓越中心、团队市场等企业级模块，提供终端监控，调度模式，机器人团队共享等协作功能。构建完整的企业级自动化管理生态，有效保障流程安全、权限管控与跨团队协作。
- **👨‍💻 开发体验友好**：提供低代码、可视化的流程设计与调试环境，通过直观的拖拉拽方式即可快速构建自动化流程，大幅降低开发门槛，提升搭建效率，赋能业务人员参与自动化创建。
- **🤖 原生 Agent 赋能**：深度集成 Astron Agent 平台，支持自动化流程与 AI 智能体的双向调用与能力融合，实现任务推理、决策判断与自动化执行的无缝衔接，拓展自动化边界。
- **🌐 多渠道触发集成**：支持直接运行、计划任务、调度模式、API 调用及 MCP 服务等多种执行方式，轻松对接各类业务场景。具备灵活的接入能力，可快速响应第三方系统集成需求，轻松嵌入各类复杂业务场景。

## 🚀 快速开始

### 系统要求
- 💻 **客户端操作系统**：Windows 10/11（主要支持）
- 🧠 **RAM** >= 8 GiB

### **服务端**: 使用 Docker

推荐使用 Docker 进行快速部署：

```bash
# 克隆项目
git clone https://github.com/iflytek/astron-rpa.git
cd astron-rpa

# 进入 docker 目录
cd docker

# 复制.env
cp .env.example .env

# 修改.env中casdoor的服务配置
CASDOOR_EXTERNAL_ENDPOINT="http://{YOUR_SERVER_IP}:8000"

# 🚀 启动所有服务
docker compose up -d

# 📊 检查服务状态
docker compose ps
```

- 在浏览器访问 `http://localhost:8080`
- 生产部署及安全加固请参考 [部署文档](docker/QUICK_START.md)

### **客户端**: 源码部署/安装包部署

#### 环境依赖
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

具体的依赖安装方式以及常见问题请参考 [构建文档](./BUILD_GUIDE.zh.md)

#### 直接下载（推荐）

使用最新的[Release安装包](https://github.com/iflytek/astron-rpa/releases)

#### 一键构建

1. **准备 Python 环境**
   ```bash
   # 准备一个 Python 3.13.x 安装目录（可以是本地文件夹或系统安装路径）
   # 脚本会复制该目录来创建 python_core
   ```

2. **运行构建脚本**
   ```bash
   # 在项目根目录执行完整构建（引擎 + 前端 + 桌面应用）
   ./build.bat --python-exe "C:\Program Files\Python313\python.exe"
   
   # 或使用默认配置（如果 Python 在默认路径）
   ./build.bat
   
   # 等待操作完成
   # 当控制台显示 "Full Build Complete!" 时表示构建成功
   ```

   > **注意：** 请确保指定的 Python 解释器为纯净安装，未安装额外第三方包，以减小打包体积。

   **构建流程包含：**
   1. ✅ 检测/复制 Python 环境到 `build/python_core`
   2. ✅ 安装 RPA 引擎依赖包
   3. ✅ 压缩 Python 核心到 `resources/python_core.7z`
   4. ✅ 安装前端依赖
   5. ✅ 构建前端 Web 应用
   6. ✅ 构建 Tauri 桌面应用

3. 📦 安装打包完成的客户端安装包

4. ⚙️ 安装好后在安装目录下的 `resources/conf.yaml` 中修改服务端地址：

    ```yaml
    remote_addr: http://YOUR_SERVER_ADDRESS/
    skip_engine_start: false
    ```

## 🏗️ 架构概览

本项目采用前后端分离架构，前端基于 Vue 3 + TypeScript 与 Tauri 构建桌面应用；后端以 Java Spring Boot 与 Python FastAPI 构建微服务，支撑业务与 AI 能力；引擎层基于 Python，集成 20+ RPA 组件，支持图像识别与 UI 自动化；整体通过 Docker 部署，具备高可观测性与扩展性，专为复杂 RPA 场景设计。

![Architecture Overview](./docs/images/Structure-zh.png "Architecture Overview")

## 📦 组件生态

### 核心组件包
- **astronverse.system**：系统操作、进程管理、截图
- **astronverse.browser**：浏览器自动化、网页操作
- **astronverse.gui**：图形界面自动化、鼠标键盘操作
- **astronverse.excel**：Excel 表格操作、数据处理
- **astronverse.vision**：计算机视觉、图像识别
- **astronverse.ai**：AI 智能服务集成
- **astronverse.network**：网络请求、API 调用
- **astronverse.email**：邮件发送和接收
- **astronverse.docx**：Word 文档处理
- **astronverse.pdf**：PDF 文档操作
- **astronverse.encrypt**：加密解密功能

### 执行框架
- **astronverse.actionlib**：原子操作定义和执行
- **astronverse.executor**：工作流执行引擎
- **astronverse.picker**：工作流拾取元素引擎
- **astronverse.scheduler**：引擎调度器
- **astronverse.trigger**：引擎触发器

### 共享库
- **astronverse.baseline**：RPA 框架核心
- **astronverse.websocketserver**：WebSocket 通信
- **astronverse.websocketclient**：WebSocket 通信
- **astronverse.locator**：元素定位技术


## 📚 文档链接

- [📖 使用指南](https://www.iflyrpa.com/docs/)
- [🚀 部署指南](docker/QUICK_START.md)
- [📖 API 文档](backend/openapi-service/api.yaml)
- [🔧 组件开发指南](engine/components/)
- [🐛 故障排除](docs/TROUBLESHOOTING.md)
- [📝 更新日志](CHANGELOG.md)

## 🤝 参与贡献

我们欢迎任何形式的贡献！请查看 [贡献指南](CONTRIBUTING.md)

### 开发规范
- ✅ 遵循现有代码风格
- ✅ 添加必要的测试用例
- ✅ 更新相关文档
- ✅ 确保所有检查通过

### 贡献步骤
1. 🍴 Fork 本仓库
2. 🌿 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💾 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 🚀 推送到分支 (`git push origin feature/AmazingFeature`)
5. 📝 打开一个 Pull Request

## 🌟 Star 历史

<div align="center">
  <img src="https://api.star-history.com/svg?repos=iflytek/astron-rpa&type=Date" alt="Star 历史图表" width="600">
</div>

## 💖 赞助支持

<div align="center">
  <a href="https://github.com/sponsors/iflytek">
    <img src="https://img.shields.io/badge/赞助-GitHub%20Sponsors-pink?style=for-the-badge&logo=github" alt="GitHub Sponsors">
  </a>
  <a href="https://opencollective.com/astronrpa">
    <img src="https://img.shields.io/badge/赞助-Open%20Collective-blue?style=for-the-badge&logo=opencollective" alt="Open Collective">
  </a>
</div>

## 📞 获取帮助

- 📧 **技术支持**: [cbg_rpa_ml@iflytek.com](mailto:cbg_rpa_ml@iflytek.com)
- 💬 **社区讨论**: [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions)
- 🐛 **问题反馈**: [Issues](https://github.com/iflytek/astron-rpa/issues)

## 📄 开源协议

本项目基于 [开源协议](LICENSE) 开源。

---

<div align="center">

**由科大讯飞开发维护**

[![Follow](https://img.shields.io/github/followers/iflytek?style=social&label=关注)](https://github.com/iflytek)
[![Star](https://img.shields.io/github/stars/iflytek/astron-rpa?style=social&label=Star)](https://github.com/iflytek/astron-rpa)
[![Fork](https://img.shields.io/github/forks/iflytek/astron-rpa?style=social&label=Fork)](https://github.com/iflytek/astron-rpa/fork)
[![Watch](https://img.shields.io/github/watchers/iflytek/astron-rpa?style=social&label=关注)](https://github.com/iflytek/astron-rpa/watchers)

**AstronRPA** - 让 RPA 开发变得简单而强大！

如果您觉得这个项目对您有帮助，请给我们一个 ⭐ Star！

</div>
