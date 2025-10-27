# AstronRPA

<div align="center">

![AstronRPA Logo](./docs/images/icon_128px.png)

**🤖 Enterprise-grade Robotic Process Automation (RPA) Development Platform**

[![License](https://img.shields.io/badge/license-Open%20Source-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/iflytek/astron-rpa)](https://github.com/iflytek/astron-rpa/releases)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![GitHub Stars](https://img.shields.io/github/stars/iflytek/astron-rpa?style=social)](https://github.com/iflytek/astron-rpa/stargazers)

English | [简体中文](README.zh.md)

</div>

## 📋 Overview

AstronRPA is an enterprise-grade Robotic Process Automation (RPA) desktop application. Through a visual designer, it supports low-code/no-code development, enabling users to rapidly build workflows and automate desktop softwares and browser pages.

[Astron Agent](https://github.com/iflytek/astron-agent) is the native Agent platform supported by this project. Users can directly call RPA workflow nodes in Astron Agent, and also use Agent workflows in AstronRPA, achieving efficient collaboration between automation processes and intelligent agent systems, empowering broader business automation scenarios.

### 🎯 Why Choose AstronRPA?

- **🛠️ Comprehensive Automation Support**: Comprehensive coverage of Windows desktop applications and web pages automation. Support for common office software like WPS and Office, financial and ERP systems like Kingdee and YonYou, and various browsers like IE, Edge, and Chrome, enabling end-to-end cross-application automation.
- **🧩 Highly Component-based**: 300+ pre-built atomic capabilities covering UI operations, data processing, and system interactions. Support for visual orchestration and custom component extensions with high flexibility and maintainability.
- **🏭 Enterprise-grade Security & Collaboration**: Built-in excellence center and team marketplace with enterprise modules. Provides terminal monitoring, scheduling modes, robot team sharing and collaborative functions. Build a complete enterprise automation management ecosystem with process security, permission control, and cross-team collaboration.
- **👨‍💻 Developer-friendly Experience**: Low-code, visual process design and debugging environment. Quickly build automation workflows through intuitive drag-and-drop methods, reducing development barriers, improving building efficiency, and enabling business users to participate in automation creation.
- **🤖 Native Agent Empowerment**: Deep integration with Astron Agent platform supporting bi-directional calls between automation processes and AI agents with capability fusion. Achieve seamless connection between task reasoning, decision making, and automated execution, expanding automation boundaries.
- **🌐 Multi-channel Trigger Integration**: Support for direct execution, scheduled tasks, scheduling modes, API calls, and MCP services. Flexible integration capabilities to quickly respond to third-party system integration needs and easily embed in complex business scenarios.

## 🚀 Quick Start

### System Requirements
- 💻 **Client Operating System**: Windows 10/11 (primary support)
- 🧠 **RAM** >= 8 GiB

### **Server**: Using Docker

Recommended for quick deployment:

```bash
# Clone the repository
git clone https://github.com/iflytek/astron-rpa.git
cd astron-rpa

# Enter docker directory
cd docker

# Copy .env
cp .env.example .env

# Modify casdoor service configuration in .env
CASDOOR_EXTERNAL_ENDPOINT="http://{YOUR_SERVER_IP}:8000"

# 🚀 Start all services
docker compose up -d

# 📊 Check service status
docker compose ps
```

- Access the application at `http://localhost:8080`
- For production deployment and security hardening, refer to [Deployment Guide](docker/QUICK_START.md)

### **Client**: Source Deployment/Binary Deployment

#### Environment Dependencies
| Tool | Version | Description |
|-----|---------|------------|
| **Node.js** | >= 22 | JavaScript runtime |
| **Python** | 3.13.x | RPA engine core |
| **Java** | JDK 8+ | Backend runtime |
| **pnpm** | >= 9 | Node.js package manager |
| **rustc** | >= 1.90.0 | Tauri build framework |
| **UV** | 0.8+ | Python package management tool |
| **7-Zip** | - | Create deployment archives |
| **SWIG** | - | Connect Python with C/C++ |

For specific installation instructions and common issues, refer to [Build Guide](./BUILD_GUIDE.md)

#### Direct Download (Recommended)

Download the latest [Release Package](https://github.com/iflytek/astron-rpa/releases)

#### One-Click Build

1. **Prepare Python Environment**
   ```bash
   # Prepare a Python 3.13.x installation directory (can be a local folder or system installation path)
   # The script will copy this directory to create python_core
   ```

2. **Run Build Script**
   ```bash
   # Full build (engine + frontend + desktop app) from project root directory
   ./build.bat --python-exe "C:\Program Files\Python313\python.exe"
   
   # Or use default configuration (if Python is in default path)
   ./build.bat
   
   # Wait for completion
   # Build successful when console displays "Full Build Complete!"
   ```

   > **Note:** Please ensure the specified Python interpreter is a clean installation without additional third-party packages to minimize package size.

   **Build process includes:**
   1. ✅ Detect/copy Python environment to `build/python_core`
   2. ✅ Install RPA engine dependencies
   3. ✅ Compress Python core to `resources/python_core.7z`
   4. ✅ Install frontend dependencies
   5. ✅ Build frontend web application
   6. ✅ Build Tauri desktop application

3. 📦 Install the packaged client installation package

4. ⚙️ After installation, modify the server address in `resources/conf.yaml` in the installation directory:

    ```yaml
    remote_addr: http://YOUR_SERVER_ADDRESS/
    skip_engine_start: false
    ```

## 🏗️ Architecture Overview

The project adopts a frontend-backend separation architecture. The frontend is built with Vue 3 + TypeScript and Tauri for desktop applications; the backend uses Java Spring Boot and Python FastAPI to build microservices supporting business and AI capabilities. The engine layer is based on Python, integrating 20+ RPA components with support for image recognition and UI automation. The entire system is deployed via Docker with high observability and scalability, designed for complex RPA scenarios.

![Architecture Overview](./docs/images/Structure.png "Architecture Overview")

## 📦 Component Ecosystem

### Core Component Packages
- **astronverse.system**: System operations, process management, screenshots
- **astronverse.browser**: Browser automation, web page operations
- **astronverse.gui**: GUI automation, mouse and keyboard operations
- **astronverse.excel**: Excel spreadsheet operations, data processing
- **astronverse.vision**: Computer vision, image recognition
- **astronverse.ai**: AI intelligent service integration
- **astronverse.network**: Network requests, API calls
- **astronverse.email**: Email sending and receiving
- **astronverse.docx**: Word document processing
- **astronverse.pdf**: PDF document operations
- **astronverse.encrypt**: Encryption and decryption functions

### Execution Framework
- **astronverse.actionlib**: Atomic operation definition and execution
- **astronverse.executor**: Workflow execution engine
- **astronverse.picker**: Workflow element picker engine
- **astronverse.scheduler**: Engine scheduler
- **astronverse.trigger**: Engine trigger

### Shared Libraries
- **astronverse.baseline**: RPA framework core
- **astronverse.websocketserver**: WebSocket communication
- **astronverse.websocketclient**: WebSocket communication
- **astronverse.locator**: Element locating technology


## 📚 Documentation

- [📖 User Guide](HOW_TO_RUN.md)
- [🚀 Deployment Guide](docker/QUICK_START.md)
- [📖 API Documentation](backend/openapi-service/api.yaml)
- [🔧 Component Development Guide](engine/components/)
- [🐛 Troubleshooting](docs/TROUBLESHOOTING.md)
- [📝 Changelog](CHANGELOG.md)

## 🤝 Contributing

We welcome any form of contribution! Please check [Contributing Guide](CONTRIBUTING.md)

### Development Guidelines
- ✅ Follow existing code style
- ✅ Add necessary test cases
- ✅ Update relevant documentation
- ✅ Ensure all checks pass

### Contributing Steps
1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 🚀 Push to the branch (`git push origin feature/AmazingFeature`)
5. 📝 Open a Pull Request

## 🌟 Star History

<div align="center">
  <img src="https://api.star-history.com/svg?repos=iflytek/astron-rpa&type=Date" alt="Star History Chart" width="600">
</div>

## 💖 Sponsorship

<div align="center">
  <a href="https://github.com/sponsors/iflytek">
    <img src="https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-pink?style=for-the-badge&logo=github" alt="GitHub Sponsors">
  </a>
  <a href="https://opencollective.com/astronrpa">
    <img src="https://img.shields.io/badge/Sponsor-Open%20Collective-blue?style=for-the-badge&logo=opencollective" alt="Open Collective">
  </a>
</div>

## 📞 Getting Help

- 📧 **Technical Support**: [cbg_rpa_ml@iflytek.com](mailto:cbg_rpa_ml@iflytek.com)
- 💬 **Community Discussion**: [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions)
- 🐛 **Bug Reports**: [Issues](https://github.com/iflytek/astron-rpa/issues)

## 📄 License

This project is open source under the [Open Source License](LICENSE).

---

<div align="center">

**Developed and maintained by iFlytek**

[![Follow](https://img.shields.io/github/followers/iflytek?style=social&label=Follow)](https://github.com/iflytek)
[![Star](https://img.shields.io/github/stars/iflytek/astron-rpa?style=social&label=Star)](https://github.com/iflytek/astron-rpa)
[![Fork](https://img.shields.io/github/forks/iflytek/astron-rpa?style=social&label=Fork)](https://github.com/iflytek/astron-rpa/fork)
[![Watch](https://img.shields.io/github/watchers/iflytek/astron-rpa?style=social&label=Watch)](https://github.com/iflytek/astron-rpa/watchers)

**AstronRPA** - Making RPA development simple and powerful!

If you find this project helpful, please give us a ⭐ Star!

</div>