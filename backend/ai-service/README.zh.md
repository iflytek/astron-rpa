# AI Service - 智能服务平台

新增可选的 **语义选择** 流程节点与 `/v1/decision/choice` 接口：使用 Jev 在给定候选中分类，
支持明确拒答；服务端配置 `JEV_API_KEY` 后启用，部署升级与流程示例见
[Jev 语义选择指南](../../docs/JEV_SEMANTIC_CHOICE.md)。

## 📖 项目介绍

AI Service 是一个基于 FastAPI 构建的综合性智能服务平台，集成了多种 AI 能力和完整的积分管理系统。平台提供了聊天对话、OCR 文字识别、验证码识别等核心功能，并通过积分机制实现服务使用的精细化管理。

### ✨ 主要特性

- 🤖 **AI 聊天服务** - 对接 DeepSeek 等大语言模型，支持流式和非流式对话
- 📝 **OCR 文字识别** - 集成讯飞通用文字识别 API，支持中英文混合识别
- 🔐 **验证码识别** - 集成云码验证码识别服务，支持多种验证码类型
- 💰 **积分管理系统** - 完整的用户积分分配、消费、过期和优先级管理
- 📊 **请求链路追踪** - 完整的日志记录和请求 ID 追踪机制
- 🔧 **异步高性能** - 基于 FastAPI 异步框架，支持高并发请求
- 🐳 **容器化部署** - 提供完整的 Docker 和 Docker Compose 部署方案

## 🚀 核心功能

### 1. AI 聊天服务 (`/v1/chat/completions`)
- 支持流式和非流式对话模式
- 兼容 OpenAI ChatGPT API 格式
- 自动积分扣除和余额检查
- 完整的错误处理和重试机制

### 2. AI 模型管理 (`/v1/models`)
- 列出所有支持的 AI 模型
- 返回模型名称、ID 和其他元数据
- 用于动态发现和选择模型 

### 3. OCR 文字识别 (`/ocr/general`)
- 基于讯飞通用文字识别 API
- 支持中英文混合文本识别
- 支持手写和印刷体文字
- 支持倾斜文本和生僻字优化
- 自动积分扣除机制

### 4. 验证码识别 (`/jfbym/customApi`)
- 集成云码验证码识别服务
- 支持多种验证码类型
- 高准确率识别
- 按成功扣费机制（仅成功时扣除积分）
- 中文错误信息返回

### 5. 积分管理系统
- **分配策略**：月度自动发放、手动添加、优先级管理
- **消费策略**：按优先级和过期时间消费
- **过期管理**：支持多种过期策略（30天、月末、永不过期等）
- **缓存优化**：Redis 缓存用户积分，提升查询性能

### 6. 管理员接口 (`/admin`)
- 用户积分查询和管理
- 手动添加/扣除积分
- 积分使用统计和监控

## 🛠 技术栈

| 组件 | 技术选型 | 版本要求 |
|------|----------|----------|
| **后端框架** | FastAPI | >=0.115.12 |
| **Python** | Python | >=3.13 |
| **数据库** | MySQL + SQLAlchemy | >=2.0.41 |
| **缓存** | Redis | >=6.1.0 |
| **异步支持** | asyncio + aiomysql | >=0.2.0 |
| **配置管理** | Pydantic Settings | >=2.9.1 |
| **容器化** | Docker + Docker Compose | - |
| **测试框架** | pytest + pytest-asyncio | >=8.3.5 |
| **代码质量** | Ruff | >=0.11.11 |
| **加密支持** | bcrypt + cryptography | >=4.3.0 |

## 📁 项目结构

```
ai-service/
├── app/                          # 应用主目录
│   ├── main.py                   # FastAPI 应用入口
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接和会话管理
│   ├── redis_op.py               # Redis 连接池管理
│   ├── logger.py                 # 日志配置
│   ├── dependencies/             # 依赖注入模块
│   │   ├── __init__.py          # 通用依赖
│   │   └── points.py            # 积分相关依赖
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   └── point.py             # 积分相关模型
│   ├── schemas/                  # Pydantic 数据模式
│   │   ├── chat.py              # 聊天接口模式
│   │   ├── ocr.py               # OCR 接口模式
│   │   └── jfbym.py             # 验证码接口模式
│   ├── routers/                  # API 路由
│   │   ├── ocr.py               # OCR 路由
│   │   ├── jfbym.py             # 验证码路由
│   │   └── v1/
│   │       ├── chat.py          # 聊天路由
│   │       └── models.py        # 模型管理路由
│   ├── services/                 # 业务逻辑服务
│   │   └── point.py             # 积分管理服务
│   ├── utils/                    # 工具函数
│   │   ├── ocr.py               # OCR 工具
│   │   └── jfbym.py             # 验证码工具
│   ├── middlewares/              # 中间件
│   │   └── tracing.py           # 请求追踪中间件
│   └── internal/                 # 内部管理接口
│       └── admin.py             # 管理员接口
├── tests/                        # 测试代码
│   ├── conftest.py              # 测试配置
│   ├── test_main.py             # 主应用测试
│   └── routers/                 # 路由测试
├── logs/                         # 日志目录（如 app.log）
├── docker-compose.yml            # 生产环境 Docker Compose
├── docker-compose.test.yaml      # 测试环境 Docker Compose
├── Dockerfile                    # Docker 镜像构建
├── pyproject.toml                # 项目依赖配置
├── uv.lock                       # uv 依赖锁定文件
└── README.md                     # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.13+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (可选)

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-service
```

### 2. 安装依赖

```bash
# 使用 pip 安装
pip install -e .

# 或使用 uv (推荐)
uv sync
```

> 推荐使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理，`uv.lock` 文件已锁定依赖版本，确保环境一致性。

### 3. 配置环境变量

编辑 `.env` 文件，配置必要的环境变量：

```bash
# 数据库配置
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/ai_service
DATABASE_USERNAME=your_db_username
DATABASE_PASSWORD=your_db_password

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# AI 聊天服务配置
AICHAT_BASE_URL=https://api.deepseek.com/v1/
AICHAT_API_KEY=your_deepseek_api_key

# 讯飞 OCR 配置
XFYUN_APP_ID=your_xfyun_app_id
XFYUN_API_SECRET=your_xfyun_api_secret
XFYUN_API_KEY=your_xfyun_api_key

# 云码验证码配置
JFBYM_API_TOKEN=your_jfbym_token

# 积分策略配置，这个也可以不配置，使用默认的 .env.default
MONTHLY_GRANT_AMOUNT=100000
AICHAT_POINTS_COST=100
OCR_GENERAL_POINTS_COST=50
JFBYM_POINTS_COST=10
```

### 4. 启动服务

```bash
uv run python run.py dev
```

### 5. 验证服务

访问 [http://localhost:8010/docs](http://localhost:8010/docs) 查看 API 文档。

## 🐳 Docker 部署

### 生产环境部署

1. **配置环境变量**

   创建 `.env` 文件并配置相关环境变量。

2. **启动服务**

   ```bash
   docker-compose up -d
   ```

3. **查看服务状态**

   ```bash
   docker-compose ps
   docker-compose logs -f app
   ```

### 单元测试环境部署

1. **启动测试依赖服务**

   ```bash
   docker-compose -f docker-compose.test.yaml up -d
   ```

2. **运行测试**

   ```bash
   pytest
   ```

## 📚 API 文档

### 认证说明

所有 API 请求需要在请求头中包含用户 ID：

```bash
X-User-Id: 123
# 或
user_id: 123
```

### 核心接口

#### 1. AI 聊天接口

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

#### 2. OCR 文字识别

**POST** `/ocr/general`

```json
{
  "image": "base64_encoded_image_string",
  "encoding": "jpg",
  "status": 3
}
```

#### 3. 验证码识别

**POST** `/jfbym/customApi`

```json
{
  "type": "验证码类型",
  "image": "base64_encoded_image_string"
}
```

**响应格式：**
```json
{
  "code": 10000,
  "message": "success",
  "data": {
    "code": 0,
    "data": "识别结果"
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "云码验证码处理失败: 具体错误信息",
  "data": null
}
```

#### 4. 用户积分查询

**GET** `/admin/user/points?user_id=123`

#### 5. 手动添加积分

**POST** `/admin/user/points?user_id=123&amount=1000`

## ⚙️ 配置说明

### 积分策略配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MONTHLY_GRANT_AMOUNT` | 100000 | 月度自动发放积分数量 |
| `AICHAT_POINTS_COST` | 100 | AI 聊天每次请求消耗积分 |
| `OCR_GENERAL_POINTS_COST` | 50 | OCR 识别每次消耗积分 |
| `JFBYM_POINTS_COST` | 10 | 验证码识别每次消耗积分 |

### 积分过期策略

- **月度发放积分**：当月月末过期
- **手动添加积分**：永不过期
- **其他类型积分**：30 天后过期

### 日志配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LOG_LEVEL` | INFO | 日志级别（DEBUG, INFO, WARNING, ERROR） |
| `LOG_DIR` | /var/log/ai_service | 日志文件存储目录 |

## 🧪 开发指南

### 运行测试

```bash
# 启动测试数据库
docker-compose -f docker-compose.test.yaml up -d

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/routers/test_chat.py

# 运行测试并显示覆盖率
pytest --cov=app
```

### 代码质量检查

```bash
# 格式化代码
ruff format

# 检查代码质量
ruff check

# 修复可自动修复的问题
ruff check --fix
```

### 查看日志

```bash
# 实时查看应用日志
tail -f logs/app.log
```

### 新增服务模块

1. 在 `app/routers/` 下创建新的路由文件
2. 在 `app/schemas/` 下定义数据模式
3. 在 `app/utils/` 下实现具体逻辑
4. 在 `app/main.py` 中注册路由
5. 编写对应的测试用例

### 添加新的积分消费类型

1. 在 `app/models/point.py` 中的 `PointTransactionType` 枚举添加新类型
2. 在配置文件中添加对应的积分消费配置
3. 使用 `PointChecker` 依赖注入进行积分检查和扣除

> 注意：添加新的积分类型后，需要手动升级数据库，生产环境不建议这么做。

## 📝 日志说明

### 日志配置

- **日志级别**：通过 `LOG_LEVEL` 环境变量配置（默认：INFO）
- **日志目录**：通过 `LOG_DIR` 环境变量配置（默认：/var/log/ai_service）
- **日志格式**：包含时间戳、模块名、请求 ID、日志级别和消息内容
- **日志轮转**：单个日志文件最大 10MB，保留 10 个历史文件

### 请求追踪

每个请求都会分配唯一的 Request ID，便于问题排查：

```
2025-06-03 10:30:15 - app.main - [abc-123-def] - INFO - Root endpoint accessed!
```

### 日志输出

- **控制台输出**：包含请求 ID 的格式化日志
- **文件输出**：包含请求 ID 的格式化日志，支持日志轮转
- **错误处理**：所有异常都会记录详细日志，便于问题排查

## ❓ 常见问题

### Q: 如何重置用户积分？

A: 可以通过管理员接口手动扣除用户当前所有积分，然后重新添加：

```bash
# 1. 查询用户当前积分
curl -X GET "http://localhost:8010/admin/user/points?user_id=123"

# 2. 扣除所有积分
curl -X POST "http://localhost:8010/admin/user/points/deduct?user_id=123&amount=当前积分数"

# 3. 添加新的积分
curl -X POST "http://localhost:8010/admin/user/points?user_id=123&amount=新积分数"
```

### Q: 积分不足时如何处理？

A: 系统会自动检查用户积分，如果不足会返回 403 状态码。用户需要联系管理员添加积分或等待月度自动发放。

### Q: 如何监控服务健康状况？

A: 可以通过以下方式监控：

1. 访问根路径 `/` 检查服务是否正常响应
2. 查看日志文件了解详细运行情况
3. 监控 Redis 和 MySQL 连接状态
4. 检查容器运行状态（如果使用 Docker）

### Q: 如何备份和恢复数据？

A: 

**备份：**
```bash
# 备份 MySQL 数据
docker exec mysql_container mysqldump -u root -p ai_service > backup.sql

# 备份 Redis 数据
docker exec redis_container redis-cli BGSAVE
```

**恢复：**
```bash
# 恢复 MySQL 数据
docker exec -i mysql_container mysql -u root -p ai_service < backup.sql
```

### Q: 验证码识别失败怎么办？

A: 验证码识别失败时，系统会返回详细的错误信息：

- **业务逻辑错误**：返回 400 状态码和具体错误信息
- **网络错误**：返回 503 状态码，提示服务暂时不可用
- **未知错误**：返回 500 状态码，提示发生未知错误

所有错误信息都是中文，便于用户理解。

### Q: 日志中看不到 request_id 怎么办？

A: 确保：

1. 应用正确配置了 `RequestTracingMiddleware` 中间件
2. 日志配置中包含了 `RequestIdFilter`
3. 检查日志格式是否包含 `%(request_id)s`

如果仍有问题，可以检查日志配置和中间件是否正确加载。
