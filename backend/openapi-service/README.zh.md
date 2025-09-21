# RPA OpenAPI Service - RPA 工作流管理服务

## 📖 项目介绍

RPA OpenAPI Service 是一个基于 FastAPI 构建的 RPA 工作流管理服务，提供工作流创建、执行、监控和 API 密钥管理等功能。该服务集成了 WebSocket 实时通信、MCP (Model Context Protocol) 支持、Redis 缓存、请求链路追踪等现代化技术栈，为 RPA 平台提供完整的 API 服务能力。

### ✨ 主要特性

- 🔄 **工作流管理** - 支持工作流的创建、更新、查询和删除
- ⚡ **实时执行** - 基于 WebSocket 的工作流实时执行和状态监控
- 🔑 **API 密钥管理** - 完整的 API 密钥生成、验证和管理功能
- 🌐 **MCP 协议支持** - 集成 Model Context Protocol，支持 AI 模型交互
- 📊 **请求链路追踪** - 完整的请求 ID 生成与传递机制，简化日志追踪
- 📝 **结构化日志** - 统一的日志格式和日志文件轮转管理
- ♻️ **依赖注入** - 清晰的依赖注入模式，便于测试和维护
- 🔄 **Redis 集成** - 异步 Redis 连接池，用于缓存和分布式状态管理
- 🧪 **测试框架** - 集成 pytest-asyncio 用于异步测试
- 🐳 **容器化部署** - 提供 Docker 和 Docker Compose 配置

## 🏗️ 项目架构

该服务采用了清晰的分层架构设计，专门为 RPA 工作流管理而设计：

### 1. API 层 (`app/routers/`)
- **工作流管理** (`workflows.py`) - 工作流的 CRUD 操作
- **执行管理** (`executions.py`) - 工作流执行和状态监控
- **API 密钥管理** (`api_keys.py`) - API 密钥的生成和验证
- **WebSocket 通信** (`websocket.py`) - 实时通信和状态推送
- **MCP 协议** (`streamable_mcp.py`) - Model Context Protocol 支持

### 2. 服务层 (`app/services/`)
- **工作流服务** (`workflow.py`) - 工作流业务逻辑处理
- **执行服务** (`execution.py`) - 工作流执行逻辑
- **WebSocket 服务** (`websocket.py`) - 实时通信管理
- **API 密钥服务** (`api_key.py`) - 密钥生成和验证逻辑

### 3. 数据模型 (`app/schemas/`)
- **工作流模式** (`workflow.py`) - 工作流数据结构定义
- **执行模式** (`execution.py`) - 执行状态和结果定义
- **API 密钥模式** (`api_key.py`) - 密钥相关数据结构

### 4. 公共组件
- **依赖注入** (`app/dependencies/`) - 用户认证、服务依赖管理
- **中间件** (`app/middlewares/`) - 请求追踪中间件
- **内部接口** (`app/internal/`) - 管理和维护接口

### 5. 配置与连接管理
- **配置管理** (`app/config.py`) - 环境变量和配置项管理
- **Redis 连接** (`app/redis.py`) - 异步 Redis 连接池
- **日志管理** (`app/logger.py`) - 统一的日志配置

## 🛠 技术栈

| 组件 | 技术选型 | 版本要求 |
|------|----------|----------|
| **后端框架** | FastAPI | >=0.115.12 |
| **Python** | Python | >=3.11 |
| **数据库** | MySQL + SQLAlchemy | >=2.0.41 |
| **缓存** | Redis | >=6.1.0 |
| **异步支持** | asyncio + aiomysql | >=0.2.10 |
| **配置管理** | Pydantic Settings | >=2.9.1 |
| **容器化** | Docker + Docker Compose | - |
| **测试框架** | pytest + pytest-asyncio | >=8.3.5 |
| **代码质量** | Ruff | >=0.11.11 |
| **依赖管理** | uv | - |

## 📁 项目结构

```
rpa-openapi-service/
├── app/                          # 应用主目录
│   ├── main.py                   # FastAPI 应用入口
│   ├── config.py                 # 配置管理
│   ├── redis.py                  # Redis 连接池管理
│   ├── logger.py                 # 日志配置
│   ├── dependencies/             # 依赖注入模块
│   │   └── __init__.py          # 通用依赖注入
│   ├── schemas/                  # Pydantic 数据模式
│   │   ├── workflow.py          # 工作流数据结构
│   │   ├── execution.py         # 执行状态和结果
│   │   └── api_key.py           # API 密钥数据结构
│   ├── routers/                  # API 路由
│   │   ├── workflows.py         # 工作流管理路由
│   │   ├── executions.py        # 执行管理路由
│   │   ├── api_keys.py          # API 密钥管理路由
│   │   ├── websocket.py         # WebSocket 通信路由
│   │   └── streamable_mcp.py    # MCP 协议支持
│   ├── services/                 # 业务逻辑服务
│   │   ├── workflow.py          # 工作流服务
│   │   ├── execution.py         # 执行服务
│   │   ├── api_key.py           # API 密钥服务
│   │   └── websocket.py         # WebSocket 服务
│   ├── middlewares/              # 中间件
│   │   └── tracing.py           # 请求追踪中间件
│   └── internal/                 # 内部管理接口
│       └── admin.py             # 管理员接口
├── tests/                        # 测试代码
│   ├── conftest.py              # 测试配置
│   ├── test_main.py             # 主应用测试
│   └── routers/                 # 路由测试
├── logs/                         # 日志目录
├── Dockerfile                    # Docker 镜像构建
├── pyproject.toml                # 项目依赖配置
├── uv.lock                       # uv 依赖锁定文件
└── README.md                     # 项目说明文档
```

## 🚀 核心功能

### 1. 工作流管理 (`/workflows`)
- **创建/更新工作流** (`/workflows/upsert`) - 支持工作流的创建和更新
- **查询工作流** (`/workflows/{project_id}`) - 根据项目ID查询工作流详情
- **工作流列表** (`/workflows`) - 分页查询工作流列表
- **删除工作流** (`/workflows/{project_id}`) - 删除指定工作流

### 2. 工作流执行 (`/executions`)
- **创建执行** (`/executions`) - 创建工作流执行任务
- **查询执行状态** (`/executions/{execution_id}`) - 获取执行状态和结果
- **执行列表** (`/executions`) - 分页查询执行记录
- **取消执行** (`/executions/{execution_id}/cancel`) - 取消正在执行的流程

### 3. API 密钥管理 (`/api-keys`)
- **生成密钥** (`/api-keys`) - 创建新的 API 密钥
- **密钥列表** (`/api-keys`) - 查询用户的 API 密钥列表
- **删除密钥** (`/api-keys/{key_id}`) - 删除指定的 API 密钥

### 4. WebSocket 实时通信 (`/ws`)
- **实时状态推送** - 工作流执行状态的实时更新
- **执行日志流** - 实时推送执行过程中的日志信息
- **连接管理** - 支持多客户端连接和消息广播

### 5. MCP 协议支持 (`/mcp`)
- **Model Context Protocol** - 支持 AI 模型与工作流的交互
- **流式 HTTP 处理** - 支持流式数据传输和处理

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose (可选)

### 1. 基于模板创建新项目

```bash
# 克隆模板项目
git clone https://git.example.com/fastapi-boilerplate.git my-new-project
cd my-new-project

# 重置 Git 历史
rm -rf .git
git init
git add .
git commit -m "Initial commit from boilerplate"

# 修改项目名称和描述
sed -i '' 's/fastapi-boilerplate-service/my-service-name/g' pyproject.toml
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

配置文件有三个，按优先级从低到高排序：`.env.default` < `.env` < `.env.local`，其中 `.env.local` 仅用于本地调试，切勿在生产环境使用。

创建 `.env` 文件，配置必要的环境变量：

```bash
# 数据库配置
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/my_service

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 应用名称
APP_NAME="My New Service"
```

### 4. 启动服务

```bash
# 使用 uvicorn 直接启动（开发环境）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8020

# 或使用 uv 启动
uv run fastapi dev
```

### 5. 验证服务

访问 [http://localhost:8020/docs](http://localhost:8020/docs) 查看 API 文档。

## 🚀 基于模板开发新项目

按照以下步骤，您可以快速基于此模板开发自己的 API 服务：

### 1. 定义新的数据模型

在 `app/models/` 目录下创建新的数据模型：

```python
# app/models/user.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)
```

### 2. 创建数据验证模式

在 `app/schemas/` 目录下定义请求和响应模式：

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### 3. 实现业务逻辑服务

在 `app/services/` 目录下实现业务逻辑：

```python
# app/services/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
import bcrypt

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        # 加密密码
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
```

在 `app/dependencies/__init__.py` 文件中添加服务依赖：

```python
# app/dependencies/__init__.py
from app.database import get_db
from app.services.user import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 其他现有代码...

async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """提供 UserService 实例的依赖项"""
    return UserService(db)
```

### 4. 创建API路由

在 `app/routers/` 目录下创建新的路由文件：

```python
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.services.user import UserService
from app.dependencies import get_user_id_from_header, get_user_service
from typing import Annotated

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_user_id_from_header)]
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)]
):
    try:
        user = await user_service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )
```

### 5. 注册路由到主应用

在 `app/main.py` 中导入并注册新路由：

```python
# app/main.py
from app.routers import users

# 在其他路由后添加
app.include_router(users.router)
```

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

## 📚 API 文档和认证

### 认证说明

模板项目默认实现了基于请求头的简单用户识别，所有 API 请求需要在请求头中包含用户 ID：

```bash
X-User-Id: 123
# 或
user_id: 123
```

### 自动生成的 API 文档

FastAPI 自动为您的 API 生成交互式文档：

- **Swagger UI**: `/docs` - 适合开发和调试
- **ReDoc**: `/redoc` - 更适合阅读和共享

## 🧪 开发指南

### 运行测试

```bash
# 启动测试数据库
docker-compose -f docker-compose.test.yaml up -d

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/routers/test_items.py

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

### 配置调整

模板项目使用分层配置文件，可根据需要创建和修改：

1. `.env.default` - 默认配置，提交到版本控制
2. `.env` - 环境特定配置，根据部署环境定制
3. `.env.local` - 本地开发配置，不提交到版本控制

配置项加载顺序：`.env.default` < `.env` < `.env.local`

## 📝 扩展功能指南

### 1. 添加身份认证和授权

要添加 JWT 身份认证系统：

1. 添加必要的依赖：
   ```bash
   pip install python-jose[cryptography] passlib
   ```

2. 创建认证服务和依赖：
   ```python
   # app/services/auth.py
   from jose import JWTError, jwt
   from datetime import datetime, timedelta
   
   SECRET_KEY = "your-secret-key"  # 生产环境使用环境变量
   ALGORITHM = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   
   def create_access_token(data: dict):
       to_encode = data.copy()
       expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
       to_encode.update({"exp": expire})
       encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
       return encoded_jwt
   ```

3. 创建依赖项：
   ```python
   # app/dependencies/auth.py
   from fastapi import Depends, HTTPException, status
   from fastapi.security import OAuth2PasswordBearer
   
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
   
   async def get_current_user(token: str = Depends(oauth2_scheme)):
       # JWT 验证逻辑
   ```

### 2. 实现数据库迁移

使用 Alembic 进行数据库迁移：

1. 安装 Alembic：
   ```bash
   pip install alembic
   ```

2. 初始化 Alembic：
   ```bash
   alembic init migrations
   ```

3. 配置 `alembic.ini` 和 `migrations/env.py`

4. 创建迁移脚本：
   ```bash
   alembic revision --autogenerate -m "Create initial tables"
   ```

5. 运行迁移：
   ```bash
   alembic upgrade head
   ```

### 3. 添加缓存机制

利用已集成的 Redis 实现缓存：

```python
# app/services/cache.py
from redis.asyncio import Redis
from typing import Any, Optional
import json

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
        
    async def set(self, key: str, value: Any, expire: int = 3600):
        await self.redis.set(key, json.dumps(value), ex=expire)
```

## 📝 日志说明

### 日志配置

- **日志级别**：通过 `LOG_LEVEL` 环境变量配置（默认：INFO）
- **日志目录**：通过 `LOG_DIR` 环境变量配置
- **日志格式**：包含时间戳、模块名、请求 ID、日志级别和消息内容

### 请求追踪

每个请求都会分配唯一的 Request ID，便于问题排查：

```
2025-06-06 10:30:15 - app.main - [abc-123-def] - INFO - Root endpoint accessed!
```

请求 ID 会自动：
1. 保存在上下文变量中，便于整个请求生命周期内访问
2. 添加到响应头 `X-Request-ID` 
3. 注入到每条日志记录中

## ❓ 常见问题

### Q: 如何修改默认端口号？

A: 可以通过环境变量或直接在启动命令中指定：

```bash
# 在命令中指定
uvicorn app.main:app --host 0.0.0.0 --port 8020

# 或在 docker-compose.yml 中修改映射
ports:
  - "8080:8000"
```

### Q: 如何处理大量并发请求？

A: 考虑以下方案：
1. 增加 uvicorn workers 数量：`--workers 4`
2. 使用 Gunicorn 作为进程管理器
3. 对耗时操作使用异步处理
4. 添加适当的缓存机制

### Q: 如何监控服务健康状况？

A: 可以通过以下方式监控：
1. 实现健康检查端点 `/health`
2. 查看日志文件了解详细运行情况
3. 监控 Redis 和 MySQL 连接状态
4. 添加 Prometheus 和 Grafana 监控（高级）

### Q: 如何部署到生产环境？

A: 推荐的生产部署方案：
1. 使用 Docker Compose 或 Kubernetes 管理容器
2. 配置反向代理（如 Nginx）处理 SSL 和请求分发
3. 使用环境变量注入敏感配置
4. 设置适当的日志级别和监控

## 🔄 持续更新与贡献

本模板项目会持续更新以保持与 FastAPI 生态系统和最佳实践的同步。如果您有任何改进建议或问题，欢迎通过以下方式参与贡献：

1. 提交 Issue 报告问题或建议新功能
2. 提交 Pull Request 贡献代码改进
3. 完善文档和示例代码

## 📜 许可证

本项目采用 MIT 许可证。您可以自由地使用、修改和分发此代码，无论是用于个人项目还是商业项目。
