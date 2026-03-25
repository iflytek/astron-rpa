# 🤖 Astron RPA Frequently Asked Questions (FAQ)

> 💡 **Tip:** Items marked with 🆕 are new additions, and those marked with 🔄 are recent updates.

## 📚 Table of Contents

- [🔧 Installation & Deployment](#-installation--deployment)
- [👥 Client Related](#-client-related)
- [⚡ Performance & Loading](#-performance--loading)
- [📖 Feature Usage](#-feature-usage)
- [🐛 Troubleshooting](#-troubleshooting)
- [📞 Get Help](#-get-help)

---

## 🔧 Installation & Deployment

### Q: Can the open-source client run on Linux?

**A:** ❌ **Not yet!** The open-source version of Astron RPA client currently only supports Windows systems.

**Supported Systems:**
- ✅ Windows 10/11

### Q: 🆕 Is it normal for the server atlas container to exit automatically after starting?

**A:** ✅ **Normal!** The Atlas container is used for database Schema migration and will automatically exit upon task completion. As long as the log shows "Schema is synced", it means success.

### Q: 🆕 Agent server cannot connect to RPA service?

**A:** Please check the `.env` file in the Agent deployment directory to ensure `RPA_URL` is set to the actual address of the RPA server (e.g., `http://YOUR_IP:32742`).

### Q: 🆕 Client installation stuck at the last step for a long time?

**A:** 

Please try:
1. Uninstall the old version
2. Manually delete the `data` folder in the installation directory
3. Re-run the installation package

### Q: Prompt "There is a problem with this Windows Installer package" during installation?

**A:**
This is usually because the system lacks necessary runtime components.
**Solution:** Please download and install/update [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).

### Q: 🆕 404 NotFound occurs when starting the client after local build?

**A:** 
It is not recommended to build the client locally by yourself, as you may encounter configuration or environmental issues.
It is recommended to download the official stable installation package (e.g., v1.1.2+) directly from the [Release page](https://github.com/iflytek/astron-rpa/releases).

---

## 👥 Client Related

### Q: Do I need to install a client?

**A:** ✅ **Yes!** RPA currently doesn't have a web version and requires a client to run.

### Q: 🆕 Is there any difference between the open-source version and the enterprise version of RPA?

**A:** The open-source version of the RPA client is universal with the platform version, but you need to pay attention to configuring the corresponding server address.

---

### Q: Do I have to manually build the client?

**A:** ✅ **No!** You can download the msi installer package directly from the [Release version](https://github.com/iflytek/astron-rpa/releases) and install it directly.

---

### Q: How do I quickly deploy the latest code?

**A:** 

#### Server Update Method 1️⃣: Quick Update (Download Latest Image)

Best for production environments, the fastest and simplest update method.

```bash
# 1. Stop old containers
docker-compose down

# 2. Remove old images (optional, to clean up local images)
docker rmi ghcr.io/iflytek/astron-rpa/openapi-service:latest
docker rmi ghcr.io/iflytek/astron-rpa/ai-service:latest
docker rmi ghcr.io/iflytek/astron-rpa/robot-service:latest

# 3. Start new containers and automatically download latest images
docker-compose up -d
```

#### Server Update Method 2️⃣: Local Build (For Developers)

Allows customization, suitable for development and testing environments.

```bash
# 1. Pull the latest code
git pull origin main

# 2. Enter docker directory
cd docker

# 3. Edit docker-compose.yml
# - Comment out the image line
# - Uncomment the build section

# Example configuration:
# services:
#   openapi-service:
#     # image: ghcr.io/iflytek/astron-rpa/openapi-service:latest
#     build:
#       context: ..
#       dockerfile: backend/openapi-service/Dockerfile

# 4. Build and start locally
docker-compose up -d --build

# 5. Wait for build to complete (may take several minutes)
docker-compose logs -f
```

> 💡 **Update Tips:** 
> - Method 1️⃣ is fastest, suitable for production
> - Method 2️⃣ allows customization, suitable for developers
> - Database data is preserved during updates (mysql container data in volumes)

#### Server Update Method 3️⃣: Update Database with ATLAS

Quickly update database schema by starting the ATLAS container for automatic migration.

```bash
# 1. Start the ATLAS container for database migration
docker-compose up -d atlas

# 2. View ATLAS migration logs (ensure migration succeeded)
docker-compose logs -f atlas
```

> 💡 **About ATLAS:**
> - ATLAS is a database version management tool for automatically executing database migration scripts
> - Each server update may include database schema changes that need to be applied via ATLAS
> - Existing data in the database is preserved; only table structures and schema are updated

---

#### Client Update Method 1️⃣: Update Python Packages Directly

Quick development iteration, only updating specific packages.

If you've modified Python packages in the `engine` directory (such as `workflowlib`, `executor`, etc.), you can copy them directly to the client's Python environment:

```bash
# Example: updating workflowlib
# 1. Find the source code location
# engine/shared/astronverse-workflowlib

# 2. Copy to client installation directory
# From: \astron-rpa\engine\shared\astronverse-workflowlib\src\astronverse\workflowlib
# To: C:\Program Files\Astron RPA\data\python_core\Lib\site-packages\astronverse\workflowlib
```

**Common Packages and Locations:**

| 📦 Package | 📂 Source Code Location | 🎯 Target Location |
|---------|----------|--------|
| workflowlib | `engine/shared/astronverse-workflowlib/src/astronverse/workflowlib` | `<install_dir>/data/python_core/Lib/site-packages/astronverse/workflowlib` |
| executor | `engine/servers/astronverse-executor/src/astronverse/executor` | `<install_dir>/data/python_core/Lib/site-packages/astronverse/executor` |
| browser | `engine/components/astronverse-browser/src/astronverse/browser` | `<install_dir>/data/python_core/Lib/site-packages/astronverse/browser` |
| other packages | `engine/<?>/astronverse-*/src/astronverse/*` | `<install_dir>/data/python_core/Lib/site-packages/astronverse/*` |

> 💡 **Restart Tip:** 
> - If updating packages in Servers, you need to restart the client to load the new packages

---

#### Client Update Method 2️⃣: Repackage and Reinstall

Use this when updating multiple packages or need a complete version update.

If you've made extensive changes or want to fully update the client, you can use `build.bat` to package a new client msi installer:

```bash
# 1. Run in the project root directory
.\build.bat

# 2. Wait for build to complete (may take 10-30 minutes)
# New msi installer will be generated in build/dist/ directory

# 3. Use the newly generated msi installer to reinstall
# - Run build/dist/*.msi file directly
# - Or replace it in the release directory for other users to download
```

---

#### Update Methods Comparison

| 🔄 Update Method | 🎯 Use Case | ⚡ Speed | 📚 Complexity |
|---------|---------|------|--------|
| Copy Python packages directly | Quick dev iteration, only update specific packages | 🚀 Fast | 🟢 Simple |
| Repackage msi | Multiple packages update, need complete version | 🐢 Slow | 🟡 Medium |
| Download new Release | New version release, production environment | 🔄 Medium | 🟢 Simple |

> 💡 **Best Practices:** 
> - 🔨 **Development Phase** → Use "Copy packages" for quick iteration
> - ✅ **Feature Complete** → Use "build.bat" to package as complete installer
> - 🚀 **Production** → Use official Release version

---

## ⚡ Performance & Loading

### Q: Why does the software hang on loading?

**A:** 

**Here are some situations encountered in practice:**

#### 1️⃣ **remote_addr** not modified in conf.yaml

**❌ Symptom:** Client hangs on loading page

**✅ Solution:** After installation, modify the server address in `resources/conf.yaml` in the installation directory:

```yaml
# 32742 is the default port, change if modified
remote_addr: http://YOUR_SERVER_ADDRESS:32742/
skip_engine_start: false
```

---

#### 2️⃣ Server hasn't fully started up yet

**❌ Symptom:** Newly started service is still initializing

**✅ Solution:** Wait a while and then restart the client

---

#### 3️⃣ CASDOOR_EXTERNAL_ENDPOINT not modified in .env

**❌ Symptom:** Authentication service cannot be accessed

**✅ Solution:**

```bash
# Modify casdoor service configuration in .env (8000 is the default port)
CASDOOR_EXTERNAL_ENDPOINT="http://{YOUR_SERVER_IP}:8000"
```

---

## 📖 Feature Usage

### Q: 🔄 Why can't I capture web elements? Why does web automation always fail?

**A:** 

🔴 **Most likely you haven't installed the browser plugin**

![](./docs/images/browser-plugin.png)

**Other common reasons:**
1. **Display settings:** Ensure your computer monitor scaling is set to **100%**.
2. **Mode selection:** Use "Browser Plugin" mode for capturing web content; use "Desktop Element" mode for capturing the browser itself (like the address bar).

For more web automation information, see the [Official Guide](https://www.iflyrpa.com/docs/quick-start/web-automation.html)

### Q: 🆕 How to handle web page screenshots and CAPTCHAs?

**A:**

1. Use the "Webpage Screenshot" atomic capability.
2. For text on Canvas or special CAPTCHAs, you can process them by combining OCR or large model image recognition capabilities.

### Q: 🆕 How does the robot operate web drop-down menus with lazy loading (Virtual List) characteristics?

**A:**

For "lazy loading" drop-down menus where the rendered options exceed a certain number (e.g., 200), but the actual HTML only renders a few within the viewport (e.g., 10), normal capturing will fail when scrolling.
**Solutions:**
1. **Keyboard Simulation:** Use "Simulate Keystrokes" (such as the down arrow `Down`) to select options one by one.
2. **XPath Customization:** If the element exists in the DOM although invisible, try getting it via customized XPath.
3. **Image Recognition:** Combine with image recognition clicks for auxiliary positioning.
4. **Scroll Page Operation:** Add scrolling operations to trigger element rendering, and then perform capturing or clicking.

---

### Q: How do I use AI capabilities in workflows?

**A:** 

Before using AI atomic capabilities, you need to configure the corresponding AI parameters when deploying the server.

```yaml
# Large model URL and corresponding API_KEY (compatible with OpenAI format)
AICHAT_BASE_URL="https://api.deepseek.com/v1/"
AICHAT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxx"

# Iflytek Cloud OCR authentication method (get from official website)
XFYUN_APP_ID=dxxxxx38
XFYUN_API_SECRET=ZTFxxxxxxxxxxxxxxxxNDVm
XFYUN_API_KEY=c4xxxxxxxxxxxxxxxx8a7

# Yunma CAPTCHA authentication method
JFBYM_ENDPOINT="http://api.jfbym.com/api/YmServer/customApi"
JFBYM_API_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> ⚠️ **Important:** Restart the server after configuration to ensure it takes effect

---

### Q: How do I make external calls? How do I use MCP?

**A:** 

For external calls, the official [documentation](https://www.iflyrpa.com/docs/open-api/overview.html) has detailed descriptions and API documentation.

The only thing to note is that all URLs need to be changed from the official domain to your own server domain.

```bash
# Official version:
https://newapi.iflyrpa.com/api/rpa-openapi/workflows/get

# Open-source version:
http://{IP_ADDRESS}:32742/api/rpa-openapi/workflows/get
```

> 📌 **Reminder:** All robots that need to be called externally need to be published in the designer first, then configured for external calls in the executor

### Q: 🆕 How to pass parameters (input/output) in RPA workflows?

**A:** 

- **Input parameters:** Define "Process Parameters" in the RPA workflow design, and pass the corresponding Key-Value when calling externally.
- **Output parameters:** Return JSON data through HTTP request nodes or Python scripts, which can be referenced by subsequent nodes via variables.

### Q: What if dependency package downloads fail?

**A:** 

The domestic network environment may cause timeouts when connecting to the official PyPI source.

**✅ Solution:** Configure a domestic mirror source (like Alibaba Cloud).

```ini
# pip configuration example
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
```

### Q: 🆕 How to install third-party Python libraries (such as `ddddocr`) in an intranet environment (offline)?

**A:** 
In an environment without external network access, normal `pip install` or offline packages may fail due to environmental differences.
**✅ Solution (Bottom-level injection):**
1. Prepare the complete dependency files of the required library in an external network environment.
2. Directly copy and integrate the dependency library files into the `python_core` base environment of the RPA client engine (e.g., `<installation_directory>/data/python_core/Lib/site-packages/`).
3. Reset the `venv` environment of the client to trigger environment reconstruction and load the new library.

### Q: 🆕 Can it be used in an intranet?

**A:** ✅ **Yes!** As long as the RPA client and server can communicate normally within the same intranet environment.

### Q: 🆕 Are there any limits on the number of workflows for the free/open-source version?

**A:** The open-source version is generally consistent with the personal version. If there are no special cloud account binding restrictions, there are usually no strict quantity limits. Please refer to the official instructions or Release notes for details.

### Q: 🆕 Virtual desktop fails to run / white screen / prompts "Authorization required to enable"?

**A:** 
1. **Check the "Remote Desktop" switch (most common reason)**: 
   - Even in Windows Pro, the remote desktop feature might be disabled by default.
   - **Operation**: Go to `Settings` -> `System` -> `Remote Desktop`, and ensure the switch is **"On"**.
2. **System Requirements**: Only supports Windows 8, Windows Server 2012, and higher versions.
   - ❌ **Does not support Windows Home**: Home edition lacks RDP components.
3. **Account Password**: 
   - Ensure the current Windows login account **has a password set**. RDP usually does not allow empty password logins.
4. **Permission Settings**: 
   - Try running the RPA client as an **Administrator**.
5. **Stability**: This feature may currently be unstable, it is recommended to prioritize running in a standard desktop environment.

### Q: 🆕 Can AstronRPA add comments in sub-workflows?

**A:** Yes. The workflow designer supports adding comments.

---

## 🐛 Troubleshooting

### Q: How do I collect diagnostic information?

**A:** 

When encountering problems, query the server and engine logs:

```bash
# 1️⃣ Query Docker logs
docker ps -a
docker logs [container_name] > logs.txt

# 2️⃣ Query client logs
# Logs are saved in: installation_directory\data\logs
# If software is installed on C drive: %APPDATA%\astron-rpa\logs
```

### Q: Startup error, white screen, or abnormal interface?

**A:** 

It may be missing `Microsoft Edge WebView2 Runtime` or the version is too low (common in older systems or cloud desktops). Please try updating WebView2 Runtime.

### Q: 🆕 Web element capturing feature frequently fails or causes the browser to crash?

**A:** 

If a crash or complete failure occurs when capturing elements, it may be because other applications running in the system (such as the "Doubao" client) are also trying to take over the browser environment, causing a dual conflict.
**Solution:** Try closing potential interfering applications, adjust configurations, and then restart the RPA client and browser.

### Q: Build or startup prompts "Python copy failed"?

**A:** 

1. **Path issue:** Ensure the project path does not contain Chinese or special characters.
2. **Permission issue:** Try running as an administrator.

### Q: Excel/WPS automation reports "Registry information not detected"?

**A:**

1. **Permission issue:** Try running the client as an administrator (or remove administrator privileges), sometimes mismatched permissions can prevent reading the registry.
2. **Installation issue:** Ensure Office/WPS installation is complete and not corrupted.

### Q: Reports "send uuid empty" or port exception?

**A:**

- **send uuid empty:** Usually the client and server versions are inconsistent, or the connection has not been established. Please update to the latest version and restart the client.
- **Port issue:** Ports `13160`/`13159` are RPA internal scheduling service ports, please ensure they are not blocked or occupied by the firewall.

### Q: The client program keeps in an infinite loop or reports errors?

**A:** Check the logs in `data/logs/picker` or `robot-service`. Sometimes you need to clear the local cache data (delete the `data` directory) and try again.

### Q: The server Redis container keeps restarting?

**A:** 
There may be a startup script compatibility issue in the image (e.g., missing bash).
**Solutions:** 
1. Try changing `bash` to `sh` in the startup command.
2. Or pull the latest `latest` image, which usually has this issue fixed.

---

## 📞 Get Help

### 🌐 Official Channels

| Channel | Link | Response Time |
|------|------|---------|
| 🐙 GitHub Issues | [Submit Issue](https://github.com/iflytek/astron-rpa/issues) | 24-48 hours |
| 💬 Discussions | [Discussion Forum](https://github.com/iflytek/astron-rpa/discussions) | Within a week |

### 📚 Useful Resources

- 🏠 [Project Homepage](https://github.com/iflytek/astron-rpa)
- 📖 [Project Introduction](./README.md)
- 📝 [Complete Installation Guide](./BUILD_GUIDE.md)
- 🐳 [Docker Deployment Guide](./docker/QUICK_START.md)
- 👨‍💻 [Usage Guide](https://www.iflyrpa.com/docs)

---

## 🔄 Update History

| Version | Date | Content |
|------|------|---------|
| v1.0 | 2025-11-26 | Initial Release |
| v1.1 | TBD | Will add more FAQs |
| v1.1.5 | 2026-01-29 | Migrated architecture to Electron; Added Computer Use Agent; Supported data tables; Excel V2 components; Aligned open-source version with SaaS version |

---

> ⏰ **Last Updated:** 2026-02-01  
> 👤 **Maintainer:** DoctorBruce  
> 📜 **License:** Apache-2.0
