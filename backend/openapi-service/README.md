# RPA OpenAPI Service - RPA Workflow Management Service

## 📖 Project Introduction

RPA OpenAPI Service is an RPA workflow management service built on FastAPI, providing workflow creation, execution, monitoring, and API key management functions. The service integrates WebSocket real-time communication, MCP (Model Context Protocol) support, Redis caching, request tracing and other modern technology stacks, providing complete API service capabilities for the RPA platform.

### ✨ Key Features

- 🔄 **Workflow Management** - Support for workflow creation, update, query and deletion
- ⚡ **Real-time Execution** - WebSocket-based real-time workflow execution and status monitoring
- 🔑 **API Key Management** - Complete API key generation, validation and management functionality
- 🌐 **MCP Protocol Support** - Integration with Model Context Protocol, supporting AI model interaction
- 📊 **Request Tracing** - Complete request ID generation and passing mechanism, simplifying log tracing
- 📝 **Structured Logging** - Unified log format and log file rotation management
- ♻️ **Dependency Injection** - Clear dependency injection pattern, easy to test and maintain
- 🔄 **Redis Integration** - Async Redis connection pool for caching and distributed state management
- 🧪 **Testing Framework** - Integrated pytest-asyncio for async testing
- 🐳 **Containerized Deployment** - Docker and Docker Compose configuration

## 🏗️ Project Architecture

The service adopts a clear layered architecture design, specifically designed for RPA workflow management:

### 1. API Layer (`app/routers/`)
- **Workflow Management** (`workflows.py`) - Workflow CRUD operations
- **Execution Management** (`executions.py`) - Workflow execution and status monitoring
- **API Key Management** (`api_keys.py`) - API key generation and validation
- **WebSocket Communication** (`websocket.py`) - Real-time communication and status push
- **MCP Protocol** (`streamable_mcp.py`) - Model Context Protocol support

### 2. Service Layer (`app/services/`)
- **Workflow Service** (`workflow.py`) - Workflow business logic processing
- **Execution Service** (`execution.py`) - Workflow execution logic
- **WebSocket Service** (`websocket.py`) - Real-time communication management
- **API Key Service** (`api_key.py`) - Key generation and validation logic

### 3. Data Models (`app/schemas/`)
- **Workflow Schema** (`workflow.py`) - Workflow data structure definitions
- **Execution Schema** (`execution.py`) - Execution status and result definitions
- **API Key Schema** (`api_key.py`) - Key-related data structures

### 4. Common Components
- **Dependency Injection** (`app/dependencies/`) - User authentication, service dependency management
- **Middlewares** (`app/middlewares/`) - Request tracing middleware
- **Internal Interfaces** (`app/internal/`) - Management and maintenance interfaces

### 5. Configuration and Connection Management
- **Configuration Management** (`app/config.py`) - Environment variables and configuration management
- **Redis Connection** (`app/redis.py`) - Async Redis connection pool
- **Logging Management** (`app/logger.py`) - Unified logging configuration

## 🛠 Technology Stack

| Component | Technology | Version Requirement |
|-----------|------------|-------------------|
| **Backend Framework** | FastAPI | >=0.115.12 |
| **Python** | Python | >=3.11 |
| **Database** | MySQL + SQLAlchemy | >=2.0.41 |
| **Cache** | Redis | >=6.1.0 |
| **Async Support** | asyncio + aiomysql | >=0.2.10 |
| **Config Management** | Pydantic Settings | >=2.9.1 |
| **Containerization** | Docker + Docker Compose | - |
| **Testing Framework** | pytest + pytest-asyncio | >=8.3.5 |
| **Code Quality** | Ruff | >=0.11.11 |
| **Dependency Management** | uv | - |

## 📁 Project Structure

```
rpa-openapi-service/
├── app/                          # Main application directory
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── redis.py                  # Redis connection pool management
│   ├── logger.py                 # Logging configuration
│   ├── dependencies/             # Dependency injection modules
│   │   └── __init__.py          # Common dependency injection
│   ├── schemas/                  # Pydantic data schemas
│   │   ├── workflow.py          # Workflow data structures
│   │   ├── execution.py         # Execution status and results
│   │   └── api_key.py           # API key data structures
│   ├── routers/                  # API routes
│   │   ├── workflows.py         # Workflow management routes
│   │   ├── executions.py        # Execution management routes
│   │   ├── api_keys.py          # API key management routes
│   │   ├── websocket.py         # WebSocket communication routes
│   │   └── streamable_mcp.py    # MCP protocol support
│   ├── services/                 # Business logic services
│   │   ├── workflow.py          # Workflow service
│   │   ├── execution.py         # Execution service
│   │   ├── api_key.py           # API key service
│   │   └── websocket.py         # WebSocket service
│   ├── middlewares/              # Middlewares
│   │   └── tracing.py           # Request tracing middleware
│   └── internal/                 # Internal management interfaces
│       └── admin.py             # Admin interface
├── tests/                        # Test code
│   ├── conftest.py              # Test configuration
│   ├── test_main.py             # Main application tests
│   └── routers/                 # Route tests
├── logs/                         # Log directory
├── Dockerfile                    # Docker image build
├── pyproject.toml                # Project dependency configuration
├── uv.lock                       # uv dependency lock file
└── README.md                     # Project documentation
```

## 🚀 Core Functions

### 1. Workflow Management (`/workflows`)
- **Create/Update Workflow** (`/workflows/upsert`) - Support for workflow creation and update
- **Query Workflow** (`/workflows/{project_id}`) - Query workflow details by project ID
- **Workflow List** (`/workflows`) - Paginated workflow list query
- **Delete Workflow** (`/workflows/{project_id}`) - Delete specified workflow

### 2. Workflow Execution (`/executions`)
- **Create Execution** (`/executions`) - Create workflow execution task
- **Query Execution Status** (`/executions/{execution_id}`) - Get execution status and results
- **Execution List** (`/executions`) - Paginated execution record query
- **Cancel Execution** (`/executions/{execution_id}/cancel`) - Cancel running workflow

### 3. API Key Management (`/api-keys`)
- **Generate Key** (`/api-keys`) - Create new API key
- **Key List** (`/api-keys`) - Query user's API key list
- **Delete Key** (`/api-keys/{key_id}`) - Delete specified API key

### 4. WebSocket Real-time Communication (`/ws`)
- **Real-time Status Push** - Real-time updates of workflow execution status
- **Execution Log Stream** - Real-time push of log information during execution
- **Connection Management** - Support for multi-client connections and message broadcasting

### 5. MCP Protocol Support (`/mcp`)
- **Model Context Protocol** - Support for AI model interaction with workflows
- **Streaming HTTP Processing** - Support for streaming data transmission and processing
- **API Key Authentication** - Supports Bearer and `X-API-Key` request headers

#### MCP Authentication

Bearer authentication is recommended for production:

```http
Authorization: Bearer <API_KEY>
```

The dedicated header is also supported:

```http
X-API-Key: <API_KEY>
```

URL query credentials (`?key=`) are rejected by default so credentials do not enter browser history or proxy logs.
Set `MCP_ALLOW_QUERY_API_KEY=true` only while migrating legacy clients. A request must use exactly one credential
source. Missing, malformed, invalid, or revoked credentials return HTTP 401.

## 🚀 Quick Start

### Environment Requirements

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (optional)

### 1. Install Dependencies

```bash
# Install using pip
pip install -e .

# Or use uv (recommended)
uv sync
```

> It is recommended to use [uv](https://github.com/astral-sh/uv) for dependency management. The `uv.lock` file has locked dependency versions to ensure environment consistency.

### 2. Configure Environment Variables

There are three configuration files, sorted by priority from low to high: `.env.default` < `.env` < `.env.local`, where `.env.local` is only used for local debugging and should never be used in production.

Create `.env` file and configure necessary environment variables:

```bash
# Database configuration
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/rpa_openapi

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# Application name
APP_NAME="RPA OpenAPI Service"

# Enable temporarily only while migrating legacy MCP clients
MCP_ALLOW_QUERY_API_KEY=false
```

### 3. Start Service

```bash
# Use uvicorn directly (development environment)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8020

# Or use uv
uv run python run.py dev
```

### 4. Verify Service

Visit [http://localhost:8020/docs](http://localhost:8020/docs) to view API documentation.

## 📚 API Documentation

FastAPI automatically generates interactive documentation for your API:

- **Swagger UI**: `/docs` - Suitable for development and debugging
- **ReDoc**: `/redoc` - More suitable for reading and sharing

## 🧪 Development Guide

### Running Tests

```bash
# Start test database
docker-compose -f docker-compose.test.yaml up -d

# Run all tests
pytest

# Run specific test file
pytest tests/routers/test_workflows.py

# Run tests with coverage
pytest --cov=app
```

### Code Quality Check

```bash
# Format code
ruff format

# Check code quality
ruff check

# Fix auto-fixable issues
ruff check --fix
```

### View Logs

```bash
# Real-time view of application logs
tail -f logs/app.log
```

### Configuration Adjustment

The service uses layered configuration files that can be created and modified as needed:

1. `.env.default` - Default configuration, committed to version control
2. `.env` - Environment-specific configuration, customized according to deployment environment
3. `.env.local` - Local development configuration, not committed to version control

Configuration loading order: `.env.default` < `.env` < `.env.local`

## 📝 Logging

### Log Configuration

- **Log Level**: Configured via `LOG_LEVEL` environment variable (default: INFO)
- **Log Directory**: Configured via `LOG_DIR` environment variable
- **Log Format**: Contains timestamp, module name, request ID, log level and message content

### Request Tracing

Each request is assigned a unique Request ID for easy troubleshooting:

```
2025-06-06 10:30:15 - app.main - [abc-123-def] - INFO - Root endpoint accessed!
```

Request ID automatically:
1. Saved in context variables for easy access throughout request lifecycle
2. Added to response header `X-Request-ID`
3. Injected into each log record

## ❓ FAQ

### Q: How to modify default port number?

A: You can specify through environment variables or directly in startup command:

```bash
# Specify in command
uvicorn app.main:app --host 0.0.0.0 --port 8020

# Or modify mapping in docker-compose.yml
ports:
  - "8020:8020"
```

### Q: How to handle large concurrent requests?

A: Consider the following solutions:
1. Increase uvicorn workers: `--workers 4`
2. Use Gunicorn as process manager
3. Use async processing for time-consuming operations
4. Add appropriate caching mechanisms

### Q: How to monitor service health?

A: You can monitor through:
1. Implement health check endpoint `/health`
2. View log files to understand detailed running status
3. Monitor Redis and MySQL connection status
4. Add Prometheus and Grafana monitoring (advanced)

### Q: How to deploy to production?

A: Recommended production deployment solutions:
1. Use Docker Compose or Kubernetes to manage containers
2. Configure reverse proxy (like Nginx) to handle SSL and request distribution
3. Use environment variables to inject sensitive configurations
4. Set appropriate log levels and monitoring

## 🔄 Contributions

If you have any improvement suggestions or questions, welcome to contribute through:

1. Submit Issues to report problems or suggest new features
2. Submit Pull Requests to contribute code improvements

## 📜 License

This project is licensed under the MIT License. You are free to use, modify and distribute this code for both personal and commercial projects.
