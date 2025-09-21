# AI Service - Intelligent Service Platform

## 📖 Project Introduction

AI Service is a comprehensive intelligent service platform built on FastAPI, integrating multiple AI capabilities and a complete points management system. The platform provides core functions including chat conversations, OCR text recognition, captcha recognition, and implements fine-grained service usage management through a points mechanism.

### ✨ Key Features

- 🤖 **AI Chat Service** - Integration with DeepSeek and other large language models, supporting both streaming and non-streaming conversations
- 📝 **OCR Text Recognition** - Integration with Xunfei general text recognition API, supporting Chinese-English mixed recognition
- 🔐 **Captcha Recognition** - Integration with Yunma captcha recognition service, supporting multiple captcha types
- 💰 **Points Management System** - Complete user points allocation, consumption, expiration and priority management
- 📊 **Request Tracing** - Complete logging and request ID tracking mechanism
- 🔧 **Asynchronous High Performance** - Based on FastAPI async framework, supporting high concurrency requests
- 🐳 **Containerized Deployment** - Complete Docker and Docker Compose deployment solution

## 🚀 Core Functions

### 1. AI Chat Service (`/v1/chat/completions`)
- Support for both streaming and non-streaming conversation modes
- Compatible with OpenAI ChatGPT API format
- Automatic points deduction and balance checking
- Complete error handling and retry mechanism

### 2. AI Model Management (`/v1/models`)
- List all supported AI models
- Return model names, IDs and other metadata
- Used for dynamic discovery and model selection

### 3. OCR Text Recognition (`/ocr/general`)
- Based on Xunfei general text recognition API
- Support for Chinese-English mixed text recognition
- Support for handwritten and printed text
- Support for tilted text and rare character optimization
- Automatic points deduction mechanism

### 4. Captcha Recognition (`/jfbym/customApi`)
- Integration with Yunma captcha recognition service
- Support for multiple captcha types
- High accuracy recognition
- Pay-per-success mechanism (points deducted only on success)
- Chinese error message return

### 5. Points Management System
- **Allocation Strategy**: Monthly automatic distribution, manual addition, priority management
- **Consumption Strategy**: Consumption by priority and expiration time
- **Expiration Management**: Support for multiple expiration strategies (30 days, end of month, never expire, etc.)
- **Cache Optimization**: Redis cache for user points, improving query performance

### 6. Admin Interface (`/admin`)
- User points query and management
- Manual points addition/deduction
- Points usage statistics and monitoring

## 🛠 Technology Stack

| Component | Technology | Version Requirement |
|-----------|------------|-------------------|
| **Backend Framework** | FastAPI | >=0.115.12 |
| **Python** | Python | >=3.13 |
| **Database** | MySQL + SQLAlchemy | >=2.0.41 |
| **Cache** | Redis | >=6.1.0 |
| **Async Support** | asyncio + aiomysql | >=0.2.0 |
| **Config Management** | Pydantic Settings | >=2.9.1 |
| **Containerization** | Docker + Docker Compose | - |
| **Testing Framework** | pytest + pytest-asyncio | >=8.3.5 |
| **Code Quality** | Ruff | >=0.11.11 |
| **Encryption Support** | bcrypt + cryptography | >=4.3.0 |

## 📁 Project Structure

```
ai-service/
├── app/                          # Main application directory
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── database.py               # Database connection and session management
│   ├── redis_op.py               # Redis connection pool management
│   ├── logger.py                 # Logging configuration
│   ├── dependencies/             # Dependency injection modules
│   │   ├── __init__.py          # Common dependencies
│   │   └── points.py            # Points-related dependencies
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── point.py             # Points-related models
│   ├── schemas/                  # Pydantic data schemas
│   │   ├── chat.py              # Chat interface schemas
│   │   ├── ocr.py               # OCR interface schemas
│   │   └── jfbym.py             # Captcha interface schemas
│   ├── routers/                  # API routes
│   │   ├── ocr.py               # OCR routes
│   │   ├── jfbym.py             # Captcha routes
│   │   └── v1/
│   │       ├── chat.py          # Chat routes
│   │       └── models.py        # Model management routes
│   ├── services/                 # Business logic services
│   │   └── point.py             # Points management service
│   ├── utils/                    # Utility functions
│   │   ├── ocr.py               # OCR utilities
│   │   └── jfbym.py             # Captcha utilities
│   ├── middlewares/              # Middlewares
│   │   └── tracing.py           # Request tracing middleware
│   └── internal/                 # Internal management interfaces
│       └── admin.py             # Admin interface
├── tests/                        # Test code
│   ├── conftest.py              # Test configuration
│   ├── test_main.py             # Main application tests
│   └── routers/                 # Route tests
├── logs/                         # Log directory (e.g., app.log)
├── Dockerfile                    # Docker image build
├── pyproject.toml                # Project dependency configuration
├── uv.lock                       # uv dependency lock file
└── README.md                     # Project documentation
```

## 🚀 Quick Start

### Environment Requirements

- Python 3.13+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (optional)

### 1. Clone Project

```bash
git clone <repository-url>
cd ai-service
```

### 2. Install Dependencies

```bash
# Install using pip
pip install -e .

# Or use uv (recommended)
uv sync
```

> It is recommended to use [uv](https://github.com/astral-sh/uv) for dependency management. The `uv.lock` file has locked dependency versions to ensure environment consistency.

### 3. Configure Environment Variables

There are three configuration files, sorted by priority from low to high: `.env.default` < `.env` < `.env.local`, where `.env.local` is only used for local debugging and should never be used in production.

Edit the `.env` file and configure necessary environment variables:

```bash
# Database configuration
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/ai_service
DATABASE_USERNAME=your_db_username
DATABASE_PASSWORD=your_db_password

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# AI chat service configuration
AICHAT_BASE_URL=https://api.deepseek.com/v1/
AICHAT_API_KEY=your_deepseek_api_key

# Xunfei OCR configuration
XFYUN_APP_ID=your_xfyun_app_id
XFYUN_API_SECRET=your_xfyun_api_secret
XFYUN_API_KEY=your_xfyun_api_key

# Yunma captcha configuration
JFBYM_API_TOKEN=your_jfbym_token

# Points strategy configuration (can also use default .env.default)
MONTHLY_GRANT_AMOUNT=100000
AICHAT_POINTS_COST=100
OCR_GENERAL_POINTS_COST=50
JFBYM_POINTS_COST=10
```

### 4. Start Service

```bash
uv run fastapi dev
```

### 5. Verify Service

Visit [http://localhost:8010/docs](http://localhost:8010/docs) to view API documentation.

## 🐳 Docker Deployment

### Production Environment Deployment

1. **Configure Environment Variables**

   Create `.env` file and configure relevant environment variables.

2. **Start Service**

   ```bash
   docker-compose up -d
   ```

3. **Check Service Status**

   ```bash
   docker-compose ps
   docker-compose logs -f app
   ```

### Unit Test Environment Deployment

1. **Start Test Dependency Services**

   ```bash
   docker-compose -f docker-compose.test.yaml up -d
   ```

2. **Run Tests**

   ```bash
   pytest
   ```

## 📚 API Documentation

### Authentication

All API requests need to include user ID in request headers:

```bash
X-User-Id: 123
# or
user_id: 123
```

### Core Interfaces

#### 1. AI Chat Interface

**POST** `/v1/chat/completions`

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 4096
}
```

#### 2. OCR Text Recognition

**POST** `/ocr/general`

```json
{
  "image": "base64_encoded_image_string",
  "encoding": "jpg",
  "status": 3
}
```

#### 3. Captcha Recognition

**POST** `/jfbym/customApi`

```json
{
  "type": "captcha_type",
  "image": "base64_encoded_image_string"
}
```

**Response Format:**
```json
{
  "code": 10000,
  "message": "success",
  "data": {
    "code": 0,
    "data": "recognition_result"
  }
}
```

**Error Response:**
```json
{
  "code": 400,
  "message": "Yunma captcha processing failed: specific error message",
  "data": null
}
```

#### 4. User Points Query

**GET** `/admin/user/points?user_id=123`

#### 5. Manual Points Addition

**POST** `/admin/user/points?user_id=123&amount=1000`

## ⚙️ Configuration

### Points Strategy Configuration

| Configuration | Default Value | Description |
|---------------|---------------|-------------|
| `MONTHLY_GRANT_AMOUNT` | 100000 | Monthly automatic points distribution amount |
| `AICHAT_POINTS_COST` | 100 | Points consumed per AI chat request |
| `OCR_GENERAL_POINTS_COST` | 50 | Points consumed per OCR recognition |
| `JFBYM_POINTS_COST` | 10 | Points consumed per captcha recognition |

### Points Expiration Strategy

- **Monthly distributed points**: Expire at end of month
- **Manually added points**: Never expire
- **Other type points**: Expire after 30 days

### Logging Configuration

| Configuration | Default Value | Description |
|---------------|---------------|-------------|
| `LOG_LEVEL` | INFO | Log level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_DIR` | /var/log/ai_service | Log file storage directory |

## 🧪 Development Guide

### Running Tests

```bash
# Start test database
docker-compose -f docker-compose.test.yaml up -d

# Run all tests
pytest

# Run specific test file
pytest tests/routers/test_chat.py

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

### Adding New Service Modules

1. Create new route file in `app/routers/`
2. Define data schemas in `app/schemas/`
3. Implement specific logic in `app/utils/`
4. Register routes in `app/main.py`
5. Write corresponding test cases

### Adding New Points Consumption Types

1. Add new type to `PointTransactionType` enum in `app/models/point.py`
2. Add corresponding points consumption configuration in config file
3. Use `PointChecker` dependency injection for points checking and deduction

> Note: After adding new points types, database needs to be manually upgraded. This is not recommended in production.

## 📝 Logging

### Log Configuration

- **Log Level**: Configured via `LOG_LEVEL` environment variable (default: INFO)
- **Log Directory**: Configured via `LOG_DIR` environment variable (default: /var/log/ai_service)
- **Log Format**: Contains timestamp, module name, request ID, log level and message content
- **Log Rotation**: Single log file max 10MB, keep 10 historical files

### Request Tracing

Each request is assigned a unique Request ID for easy troubleshooting:

```
2025-06-03 10:30:15 - app.main - [abc-123-def] - INFO - Root endpoint accessed!
```

### Log Output

- **Console Output**: Formatted logs with request ID
- **File Output**: Formatted logs with request ID, supporting log rotation
- **Error Handling**: All exceptions are logged in detail for troubleshooting

## ❓ FAQ

### Q: How to reset user points?

A: You can manually deduct all current user points through admin interface, then re-add:

```bash
# 1. Query current user points
curl -X GET "http://localhost:8010/admin/user/points?user_id=123"

# 2. Deduct all points
curl -X POST "http://localhost:8010/admin/user/points/deduct?user_id=123&amount=current_points"

# 3. Add new points
curl -X POST "http://localhost:8010/admin/user/points?user_id=123&amount=new_points"
```

### Q: How to handle insufficient points?

A: The system automatically checks user points. If insufficient, returns 403 status code. Users need to contact admin to add points or wait for monthly automatic distribution.

### Q: How to monitor service health?

A: You can monitor through:

1. Access root path `/` to check if service responds normally
2. View log files to understand detailed running status
3. Monitor Redis and MySQL connection status
4. Check container running status (if using Docker)

### Q: How to backup and restore data?

A: 

**Backup:**
```bash
# Backup MySQL data
docker exec mysql_container mysqldump -u root -p ai_service > backup.sql

# Backup Redis data
docker exec redis_container redis-cli BGSAVE
```

**Restore:**
```bash
# Restore MySQL data
docker exec -i mysql_container mysql -u root -p ai_service < backup.sql
```

### Q: What to do when captcha recognition fails?

A: When captcha recognition fails, the system returns detailed error information:

- **Business logic errors**: Returns 400 status code with specific error message
- **Network errors**: Returns 503 status code, indicating service temporarily unavailable
- **Unknown errors**: Returns 500 status code, indicating unknown error occurred

All error messages are in Chinese for easy user understanding.

### Q: What to do if request_id is not visible in logs?

A: Ensure:

1. Application correctly configured `RequestTracingMiddleware` middleware
2. Log configuration includes `RequestIdFilter`
3. Check if log format includes `%(request_id)s`

If problems persist, check if log configuration and middleware are correctly loaded.