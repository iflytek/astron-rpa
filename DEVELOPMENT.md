<div align="center">

# 🛠️ AstronRPA Development Guide

[![Python Version](https://img.shields.io/badge/Python-3.13.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node Version](https://img.shields.io/badge/Node.js-22+-green?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Java Version](https://img.shields.io/badge/Java-8+-orange?logo=openjdk&logoColor=white)](https://openjdk.org/)

**Complete development environment setup and module development guide**

[Setup](#-development-environment-setup) · [Frontend](#-frontend-development) · [Engine](#-engine-development) · [Backend](#-backend-service-development) · [Integration](#-frontend-backend-integration)

</div>

---

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Development Environment Setup](#-development-environment-setup)
- [Project Structure](#-project-structure)
- [Frontend Development](#-frontend-development)
- [Engine Development](#-engine-development)
- [Backend Service Development](#-backend-service-development)
- [Frontend-Backend Integration](#-frontend-backend-integration)
- [Makefile Commands](#-makefile-commands)
- [Code Standards](#-code-standards)
- [Docker for Local Development](#-docker-for-local-development)
- [FAQ](#-faq)

---

## 🏗️ Architecture Overview

AstronRPA uses a **client-server distributed architecture** composed of the following modules:

| Layer | Tech Stack | Modules | Language |
|-------|-----------|---------|----------|
| **Frontend** | Vue 3 + TypeScript + Vite + Electron | Web app, desktop app, browser extension | TypeScript |
| **Engine** | Python + component architecture + WebSocket | Workflow execution, 20+ atomic components | Python 3.13 |
| **Backend (Java)** | Spring Boot + MyBatis-Plus | Robot management, resource management | Java 8+ |
| **Backend (Python)** | FastAPI + SQLAlchemy | AI service, OpenAPI service | Python 3.11+ |

### Architecture Diagram

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
│  │   20+ components│ │  │  ├────────────┼────────────┤ │
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

## 🔧 Development Environment Setup

### Required Tools

| Tool | Version | Purpose | Install Guide |
|------|---------|---------|---------------|
| **Node.js** | ≥ 22 | Frontend development | [nodejs.org](https://nodejs.org/) |
| **pnpm** | ≥ 9 | Frontend package management | `npm install -g pnpm@latest` |
| **Python** | 3.13.x | Engine / AI service | [python.org](https://www.python.org/) |
| **uv** | ≥ 0.8 | Python package management | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| **Java JDK** | 8+ (robot-service) / 21+ (resource-service) | Backend Java services | [Adoptium](https://adoptium.net/) |
| **Maven** | ≥ 3.6 | Java build tool | [maven.apache.org](https://maven.apache.org/) |
| **Docker** | latest | Infrastructure services | [docker.com](https://www.docker.com/) |
| **Git** | latest | Version control | [git-scm.com](https://git-scm.com/) |

### Choose by Development Scenario

> 💡 You don't need to install all tools — just pick those needed for the modules you're working on.

| Scenario | Required Tools |
|----------|---------------|
| Frontend only | Node.js, pnpm |
| Engine only | Python 3.13, uv |
| Backend Java services only | JDK, Maven, Docker (for DB) |
| Backend Python services only | Python 3.11+, uv, Docker (for DB) |
| Engine + Frontend integration | Node.js, pnpm, Python 3.13, uv |
| Full-stack development | All tools |

---

## 📂 Project Structure

```
astron-rpa/
├── frontend/                   # Frontend (pnpm monorepo)
│   ├── packages/
│   │   ├── web-app/            # Web application
│   │   ├── electron-app/       # Electron desktop application
│   │   └── ...
│   └── locales/                # i18n resources
│
├── engine/                     # RPA Engine
│   ├── components/             # Atomic capability components (20+)
│   ├── shared/                 # Shared base libraries
│   ├── servers/                # Internal engine services
│   ├── scripts/                # Build scripts
│   └── main.py                 # Debug entry point
│
├── backend/                    # Backend services
│   ├── robot-service/          # Robot core service (Java/Spring Boot)
│   ├── resource-service/       # Resource management service (Java/Spring Boot)
│   ├── ai-service/             # AI service (Python/FastAPI)
│   ├── openapi-service/        # OpenAPI service (Python/FastAPI)
│   └── rpa-auth/               # Authentication service
│
├── docker/                     # Docker deployment configuration
├── resources/                  # Runtime resources & configuration
├── docs/                       # Project documentation
├── scripts/                    # Global scripts
├── Makefile                    # Engineering automation commands
└── build.bat                   # One-click build script
```

---

## 🖥️ Frontend Development

> **Tech Stack**: Vue 3 + TypeScript + Vite + Electron + Ant Design Vue  
> **Docs**: [frontend/README.md](frontend/README.md)

### Quick Start

```bash
cd frontend

# 📦 Install dependencies
pnpm install

# ⚙️ Set environment variables
pnpm set-env

# 🌐 Start Web dev server
pnpm dev:web

# 🖥️ Or start Electron desktop dev (requires backend services)
pnpm dev:desktop
```

### Common Commands

| Command | Description |
|---------|-------------|
| `pnpm dev:web` | Start Web dev server |
| `pnpm dev:desktop` | Start Electron desktop app (dev mode) |
| `pnpm build:web` | Build Web production version |
| `pnpm build:desktop` | Build desktop installer |
| `pnpm test` | Run Vitest unit tests |
| `pnpm lint:fix` | ESLint auto-fix |
| `pnpm i18n` | Update i18n resources |

### Frontend Project Structure

The frontend uses pnpm workspaces to manage a monorepo. Core packages are located under `packages/`. See [frontend/README.md](frontend/README.md) for details.

---

## ⚙️ Engine Development

> **Tech Stack**: Python 3.13 + uv package management + component architecture  
> **Docs**: [engine/README.md](engine/README.md)

### Quick Start

```bash
cd engine

# 📦 Sync all dependencies (including 20+ component packages)
uv sync

# 🚀 Start engine debug (includes meta build)
uv run main.py

# Check the route_port in output, e.g.:
# scheduler startup_event: route_port=13159
```

### Component Development

Each `engine/components/astronverse-*` subdirectory is an independent Python package (atomic capability component).

```bash
# Generate meta config for a single component
cd engine/components/astronverse-browser
uv run meta.py

# Generate meta for all components and merge into global config
cd engine/scripts
uv run meta_build.py

# Run component tests
cd engine/components/astronverse-browser
uv run -m pytest tests/
```

See [engine/components/README.md](engine/components/README.md) for details.

---

## 🗄️ Backend Service Development

The backend consists of 4 independent microservices: 2 Java + 2 Python.

### Infrastructure Dependencies

All backend services depend on MySQL and Redis. Start them with Docker:

```bash
cd docker
docker compose up -d mysql redis
```

---

### robot-service (Java / Spring Boot)

> **Port**: 8040 · **JDK**: 8+ · **Framework**: Spring Boot 2.3.11  
> **Docs**: [backend/robot-service/README.md](backend/robot-service/README.md)

Core robot service for robot management, workflow orchestration, scheduled tasks, and audit monitoring.

```bash
cd backend/robot-service

# Build
mvn clean package -DskipTests

# Run (with local profile)
java -jar target/robot-*.jar --spring.profiles.active=local

# Run tests
mvn test
```

---

### resource-service (Java / Spring Boot)

> **Port**: 8030 · **JDK**: 21+ · **Framework**: Spring Boot 3.2.4  
> **Docs**: [backend/resource-service/README.md](backend/resource-service/README.md)

Resource management service for file upload/download, S3 object storage, and video processing.

```bash
cd backend/resource-service

# Build
mvn clean package -DskipTests

# Run
java -jar target/resource-*.jar

# Run tests
mvn test
```

---

### ai-service (Python / FastAPI)

> **Port**: 8010 · **Python**: ≥ 3.13 · **Framework**: FastAPI  
> **Docs**: [backend/ai-service/README.md](backend/ai-service/README.md)

AI service providing AI chat, OCR recognition, CAPTCHA recognition, and credit management.

```bash
cd backend/ai-service

# Sync dependencies
uv sync

# Start in development mode
uv run python run.py dev
```

---

### openapi-service (Python / FastAPI)

> **Port**: 8020 · **Python**: ≥ 3.11 · **Framework**: FastAPI  
> **Docs**: [backend/openapi-service/README.md](backend/openapi-service/README.md)

OpenAPI service for workflow management, WebSocket communication, and MCP protocol support.

```bash
cd backend/openapi-service

# Sync dependencies
uv sync

# Start in development mode
uv run python run.py dev

# Or start directly with uvicorn
uvicorn app.main:app --port 8020 --reload
```

---

## 🔗 Frontend-Backend Integration

### Engine + Frontend Integration

The most common development scenario — the engine runs locally and the Electron frontend connects to it directly.

**Terminal 1 — Start the engine:**
```bash
cd engine
uv sync
uv run main.py
# 📝 Note the route_port from the output (e.g., 13159)
```

**Terminal 2 — Start the frontend:**
```bash
cd frontend
pnpm install
set PORT=13159 && pnpm dev:desktop
```

> The frontend will automatically skip the built-in engine startup and connect directly to the local engine at the specified `route_port`.

### Full-Stack Integration

When all services are needed, use Docker for infrastructure and backend:

```bash
# Terminal 1: Start infrastructure + backend
cd docker
cp .env.example .env
# Edit CASDOOR_EXTERNAL_ENDPOINT in .env with your actual IP
docker compose up -d

# Terminal 2: Start engine
cd engine
uv run main.py

# Terminal 3: Start frontend
cd frontend
set PORT=13159 && pnpm dev:desktop
```

---

## 📜 Makefile Commands

The root `Makefile` provides unified engineering automation commands:

```bash
# View all available commands
make help

# Code formatting
make fmt              # Format all languages
make fmt-ts           # Format TypeScript
make fmt-java         # Format Java
make fmt-python       # Format Python

# Code checks
make check            # Quick check
make check-all        # Full check

# Project status
make project-status   # Project status overview
make dev-setup        # Development environment setup
```

---

## 📏 Code Standards

### Frontend (TypeScript)

| Tool | Purpose | Config File |
|------|---------|-------------|
| ESLint | Code linting | `frontend/eslint.config.mjs` |
| Prettier | Code formatting | Built into ESLint config |
| Vitest | Unit testing | `frontend/vitest.config.ts` |

```bash
cd frontend
pnpm lint:fix    # Auto-fix
pnpm test        # Run tests
```

### Engine (Python)

| Tool | Purpose | Config File |
|------|---------|-------------|
| Ruff | Code formatting | `engine/.ruff.toml` |
| pylint | Code linting | - |
| pytest | Unit testing | - |

```bash
cd engine
uv run ruff check .     # Lint
uv run ruff format .    # Auto-format
uv run pytest           # Run tests
```

### Backend Java Services

| Tool | Purpose | Config File |
|------|---------|-------------|
| Checkstyle | Style checking | `backend/*/checkstyle.xml` |
| PMD | Static analysis | `backend/*/pmd-ruleset.xml` |
| SpotBugs | Bug detection | `backend/*/spotbugs-exclude.xml` |

```bash
cd backend/robot-service
mvn checkstyle:check    # Style check
mvn pmd:check           # Static analysis
mvn test                # Run tests
```

---

## 🐳 Docker for Local Development

### Start Infrastructure Only

When developing backend services, you typically only need databases and caches:

```bash
cd docker
docker compose up -d mysql redis
```

### Start All Server-Side Services

```bash
cd docker
cp .env.example .env
# Edit .env configuration
docker compose up -d
```

### Service Port Reference

| Service | Port | Description |
|---------|------|-------------|
| Nginx Gateway | 32742 | Backend API unified entry |
| Casdoor | 8000 | SSO authentication service |
| robot-service | 8040 | Robot core service |
| resource-service | 8030 | Resource management service |
| ai-service | 8010 | AI service |
| openapi-service | 8020 | OpenAPI service |
| MySQL | 3306 | Database |
| Redis | 6379 | Cache |

---

## ❓ FAQ

<details>
<summary><b>Q: uv sync fails or dependency conflict?</b></summary>

```bash
# Clean uv cache
uv cache clean

# Delete venv and rebuild
rm -rf .venv
uv sync
```

</details>

<details>
<summary><b>Q: pnpm install fails?</b></summary>

```bash
# Clean pnpm cache
pnpm store prune

# Delete node_modules and reinstall
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

</details>

<details>
<summary><b>Q: Frontend cannot connect to the engine?</b></summary>

- Confirm the engine is running and has output a `route_port`
- Confirm the `PORT` environment variable was set before starting the frontend
- Check if the port is in use: `netstat -ano | findstr :13159`

</details>

<details>
<summary><b>Q: Java service compilation fails?</b></summary>

- Check JDK version: robot-service requires JDK 8+, resource-service requires JDK 21+
- Check Maven version: requires 3.6+
- Ensure Maven repository is accessible (consider configuring a mirror)

</details>

<details>
<summary><b>Q: Docker services fail to start?</b></summary>

```bash
# Check port usage
netstat -ano | findstr :3306
netstat -ano | findstr :6379

# View service logs
docker compose logs -f

# Restart services
docker compose down
docker compose up -d
```

</details>

---

## 📚 Additional Documentation

| Document | Description |
|----------|-------------|
| [BUILD_GUIDE.md](BUILD_GUIDE.md) | Deployment and packaging guide |
| [engine/README.md](engine/README.md) | Engine development details |
| [engine/components/README.md](engine/components/README.md) | Atomic capability component development guide |
| [frontend/README.md](frontend/README.md) | Frontend engineering details |
| [docker/QUICK_START.md](docker/QUICK_START.md) | Docker deployment guide |
| [FAQ.md](FAQ.md) | Frequently asked questions |

---

<div align="center">

**If you have any questions, please contact the project maintainers or submit feedback via [GitHub Issues](https://github.com/iflytek/astron-rpa/issues).**

</div>
