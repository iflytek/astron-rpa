# 🤖 Astron RPA 常见问题解答 (FAQ)

## 📚 文档目录

- [🔧 安装与部署](#安装与部署)
- [👥 客户端相关](#客户端相关)
- [⚡ 性能与加载](#性能与加载)
- [📖 功能使用](#功能使用)
- [🐛 故障排查](#故障排查)
- [📞 获取帮助](#获取帮助)

---

## 🔧 安装与部署

### Q: 开源版本是否能在 Linux 上运行？

**A:** ❌ **暂时不行！** 开源版本的 Astron RPA 目前仅支持 Windows 系统。

**支持的系统：**
- ✅ Windows 10/11

---

### Q: 我是否一定需要手动构建客户端？

**A:** ✅ **不需要！** 您可以直接下载 [Release 版本](https://github.com/iflytek/astron-rpa/releases) 的 msi 安装包直接安装。

---

## 👥 客户端相关

### Q: 是否需要安装客户端？

**A:** ✅ **需要！** RPA 目前没有 Web 版本，需要客户端运行。

---

### Q: 我是否一定需要手动构建客户端？

**A:** ✅ **不需要！** 您可以直接下载 [Release 版本](https://github.com/iflytek/astron-rpa/releases) 的 msi 安装包直接安装。

---

### Q: 如何快速部署最新的代码？

**A:** 

#### 服务端更新方式 1️⃣：快速更新（下载最新镜像）

适合生产环境，最简单快速的更新方法。

```bash
# 1. 停止旧容器
docker-compose down

# 2. 删除旧镜像（可选，如果想清理本地镜像）
docker rmi ghcr.io/iflytek/astron-rpa/openapi-service:latest
docker rmi ghcr.io/iflytek/astron-rpa/ai-service:latest
docker rmi ghcr.io/iflytek/astron-rpa/robot-service:latest

# 3. 启动新容器并自动下载最新镜像
docker-compose up -d
```

#### 服务端更新方式 2️⃣：本地编译（适合开发者）

允许自定义修改，适合开发测试环境。

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 进入 docker 目录
cd docker

# 3. 编辑 docker-compose.yml
# - 注释掉 image 行
# - 取消注释 build 部分

# 示例配置：
# services:
#   openapi-service:
#     # image: ghcr.io/iflytek/astron-rpa/openapi-service:latest
#     build:
#       context: ..
#       dockerfile: backend/openapi-service/Dockerfile

# 4. 本地编译并启动
docker-compose up -d --build

# 5. 等待编译完成（可能需要几分钟）
docker-compose logs -f
```

> 💡 **更新提示：** 
> - 方式 1️⃣ 最快速，适合生产环境
> - 方式 2️⃣ 允许自定义修改，适合开发者
> - 更新过程中数据库数据会保留（mysql 容器数据在 volumes 中）

---

#### 客户端更新方式 1️⃣：直接更新 Python 包

快速开发调试，仅修改部分包。

如果你修改了 `engine` 目录下的 Python 包（如 `workflowlib`、`executor` 等），可以直接复制到客户端的 Python 环境中：

```bash
# 以修改 workflowlib 为例
# 1. 找到源代码位置
# engine/shared/astronverse-workflowlib

# 2. 复制到客户端安装目录
# 从：\astron-rpa\engine\shared\astronverse-workflowlib\src\astronverse\workflowlib
# 复制到：C:\Program Files\Astron RPA\data\python_core\Lib\site-packages\astronverse\workflowlib
```

**常见包及其位置：**

| 📦 包名 | 📂 源代码位置 | 🎯 目标位置 |
|---------|----------|--------|
| workflowlib | `engine/shared/astronverse-workflowlib/src/astronverse/workflowlib` | `<安装目录>/data/python_core/Lib/site-packages/astronverse/workflowlib` |
| executor | `engine/servers/astronverse-executor/src/astronverse/executor` | `<安装目录>/data/python_core/Lib/site-packages/astronverse/executor` |
| browser | `engine/components/astronverse-browser/src/astronverse/browser` | `<安装目录>/data/python_core/Lib/site-packages/astronverse/browser` |
| 其他包 | `engine/<?>/astronverse-*/src/astronverse/*` | `<安装目录>/data/python_core/Lib/site-packages/astronverse/*` |

> 💡 **重启提示：** 
> - 如果是 Servers 中的包，更新后需要重启客户端以加载新的包

---

#### 客户端更新方式 2️⃣：重新打包安装

多个包更新或需要完整版本时使用。

如果修改的内容较多或者想要完整更新客户端，可以通过 `build.bat` 打包新的客户端 msi 安装包：

```bash
# 1. 在项目根目录运行
.\build.bat

# 2. 等待编译完成（可能需要 10-30 分钟）
# 新的 msi 安装包会生成在 build/dist/ 目录下

# 3. 使用新生成的 msi 安装包覆盖安装
# - 直接运行 build/dist/*.msi 文件
# - 或替换到发布目录供其他用户下载
```

---

#### 更新方式对比表

| 🔄 更新方式 | 🎯 适用场景 | ⚡ 速度 | 📚 复杂度 |
|---------|---------|------|--------|
| 直接复制 Python 包 | 快速开发调试，仅修改部分包 | 🚀 快 | 🟢 简单 |
| 重新打包 msi | 多个包更新，需要完整版本 | 🐢 慢 | 🟡 中等 |
| 下载新 Release | 发布新版本，生产环境更新 | 🔄 中 | 🟢 简单 |

> 💡 **最佳实践：** 
> - 🔨 **开发阶段** → 使用"直接复制"快速迭代
> - ✅ **功能完成** → 使用"build.bat"打包成完整安装包
> - 🚀 **生产环境** → 使用官方 Release 版本

---

## ⚡ 性能与加载

### Q: 为什么软件打开卡在加载？

**A:** 

**以下是几种实践中遇到过的情况：**

#### 1️⃣ 未修改 conf.yaml 中的 **remote_addr**

**❌ 问题现象：** 客户端卡在加载页面

**✅ 解决方案：** 安装好后在安装目录下的 `resources/conf.yaml` 中修改服务端地址：

```yaml
# 32742 为默认端口，如有修改自行变更
remote_addr: http://YOUR_SERVER_ADDRESS:32742/
skip_engine_start: false
```

---

#### 2️⃣ 服务端还没启动完全

**❌ 问题现象：** 新启动的服务还在初始化中

**✅ 解决方案：** 等待一段时间后重启客户端

---

#### 3️⃣ 未修改 .env 中的 CASDOOR_EXTERNAL_ENDPOINT

**❌ 问题现象：** 认证服务无法访问

**✅ 解决方案：**

```bash
# 修改 .env 中 casdoor 的服务配置（8000 为默认端口）
CASDOOR_EXTERNAL_ENDPOINT="http://{YOUR_SERVER_IP}:8000"
```

---

## 📖 功能使用

### Q: 为什么拾取不到网页元素？为什么运行网页原子能力总是失败？

**A:** 

🔴 **很可能是你没有安装浏览器插件**

![](./docs/images/browser-plugin.png)

其他网页自动化说明可详见 [官方使用指南](https://www.iflyrpa.com/docs/quick-start/web-automation.html)

---

### Q: 如何在流程中使用 AI 能力？

**A:** 

在使用 AI 原子能力之前，需要在部署服务端的时候配置对应的 AI 相关参数。

```yaml
# 大模型 URL 以及对应的 API_KEY（OpenAI 范式均可）
AICHAT_BASE_URL="https://api.deepseek.com/v1/"
AICHAT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxx"

# 讯飞云 OCR 鉴权方式（需要去官网获取）
XFYUN_APP_ID=dxxxxx38
XFYUN_API_SECRET=ZTFxxxxxxxxxxxxxxxxNDVm
XFYUN_API_KEY=c4xxxxxxxxxxxxxxxx8a7

# 云码验证码鉴权方式
JFBYM_ENDPOINT="http://api.jfbym.com/api/YmServer/customApi"
JFBYM_API_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> ⚠️ **重要：** 配置完后重启服务端，确保配置生效

---

### Q: 如何进行外部调用？如何使用 MCP？

**A:** 

关于外部调用，在官方版的 [使用文档](https://www.iflyrpa.com/docs/open-api/overview.html) 中有详细介绍和接口文档。

唯一需要注意的是，所有 URL 需要从官方版的域名改为自己部署服务器的域名。

```bash
# 官方版：
https://newapi.iflyrpa.com/api/rpa-openapi/workflows/get

# 开源版：
http://{IP_ADDRESS}:32742/api/rpa-openapi/workflows/get
```

> 📌 **提醒：** 所有想要被外部调用的机器人需要在设计器中发版，然后在执行器中进行外部调用配置

---

## 🐛 故障排查

### Q: 如何收集问题诊断信息？

**A:** 

当遇到问题时，请查询服务端和引擎端日志：

```bash
# 1️⃣ 查询 Docker 日志
docker ps -a
docker logs [container_name] > logs.txt

# 2️⃣ 查询客户端日志
# 日志保存在：安装目录下\data\logs
# 如果软件安装在 C 盘：%APPDATA%\astron-rpa\logs
```

---

## 📞 获取帮助

### 🌐 官方渠道

| 渠道 | 链接 | 响应时间 |
|------|------|---------|
| 🐙 GitHub Issues | [提交问题](https://github.com/astronverse/astron-rpa/issues) | 24-48 小时 |
| 💬 Discussions | [讨论区](https://github.com/astronverse/astron-rpa/discussions) | 一周内 |

### 📚 常用资源

- 🏠 [项目主页](https://github.com/astronverse/astron-rpa)
- 📖 [项目介绍](./README.zh.md)
- 📝 [完整安装指南](./BUILD_GUIDE.zh.md)
- 🐳 [Docker 部署指南](./docker/QUICK_START.md)
- 👨‍💻 [使用指南](https://www.iflyrpa.com/docs)

---

## 🔄 更新历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2025-11-26 | 初始版本发布 |
| v1.1 | TBD | 将添加更多常见问题 |

---

> ⏰ **最后更新：** 2025-11-26  
> 👤 **维护者：** DoctorBruce  
> 📜 **许可证：** Apache-2.0

