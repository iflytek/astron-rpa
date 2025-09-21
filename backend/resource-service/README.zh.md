# Resource Service - 资源管理服务

## 📖 项目介绍

Resource Service 是一个基于 Spring Boot 3.2.4 构建的资源管理服务，专门用于处理文件上传、下载、存储和管理。该服务集成了 S3 兼容的对象存储（MinIO）、MySQL 数据库、Redis 缓存等基础设施，提供完整的文件生命周期管理功能。

### ✨ 主要特性

- 📁 **文件上传管理** - 支持多种文件格式上传，包括普通文件和视频文件
- 🔗 **文件下载服务** - 基于文件ID的安全文件下载
- 🎥 **视频文件支持** - 专门优化的视频文件上传和格式验证
- 📤 **共享文件上传** - 支持共享文件上传并返回文件元数据
- 🗄️ **S3 对象存储** - 集成 MinIO 等 S3 兼容存储服务
- 📊 **文件元数据管理** - 完整的文件信息记录和查询
- 🔧 **异步高性能** - 基于 Spring Boot 3 异步框架，支持高并发文件处理
- 🐳 **容器化部署** - 提供完整的 Docker 部署方案

## 🚀 核心功能

### 1. 文件上传 (`/file/upload`)
- 支持最大 50MB 文件上传
- 自动文件类型检测和验证
- 返回唯一文件ID用于后续操作

### 2. 视频文件上传 (`/file/upload-video`)
- 支持最大 50MB 视频文件上传
- 支持格式：mp4, webm, ogg, avi, mov, mpeg
- 专门的视频格式验证

### 3. 共享文件上传 (`/file/share-file-upload`)
- 支持最大 100MB 文件上传
- 返回文件ID、类型和文件名信息
- 适用于共享场景的大文件处理

### 4. 文件下载 (`/file/download`)
- 基于文件ID的安全下载
- 支持各种文件格式下载
- 完整的下载权限控制

## 🛠 技术栈

| 组件 | 技术选型 | 版本要求 |
|------|----------|----------|
| **后端框架** | Spring Boot | 3.2.4 |
| **Java** | Java | 21 |
| **数据库** | MySQL + MyBatis-Plus | 8.0.28 / 3.5.5 |
| **对象存储** | AWS S3 SDK | 2.17.102 |
| **连接池** | Druid | 1.2.16 |
| **缓存** | Redis | - |
| **构建工具** | Maven | 3.6+ |
| **容器化** | Docker | - |
| **日志框架** | Logback | - |

## 📁 项目结构

```
resource-service/
├── src/main/java/com/iflytek/rpa/resource/
│   ├── ResourceApplication.java           # Spring Boot 应用启动类
│   ├── common/                           # 公共组件
│   │   ├── exp/                          # 异常处理
│   │   │   ├── GlobalExceptionHandler.java
│   │   │   └── ServiceException.java
│   │   └── response/                     # 响应封装
│   │       ├── AppResponse.java
│   │       └── ErrorCodeEnum.java
│   └── file/                            # 文件管理模块
│       ├── config/                      # 配置类
│       │   └── S3Config.java           # S3 存储配置
│       ├── controller/                  # 控制器
│       │   └── FileController.java     # 文件操作控制器
│       ├── dao/                        # 数据访问层
│       │   ├── FileMapper.java
│       │   └── FileMapper.xml
│       ├── entity/                     # 实体类
│       │   ├── enums/                  # 枚举类
│       │   │   └── FileType.java
│       │   ├── vo/                     # 视图对象
│       │   │   └── ShareFileUploadVo.java
│       │   └── File.java              # 文件实体
│       ├── service/                    # 服务层
│       │   ├── impl/                   # 服务实现
│       │   │   └── FileServiceImpl.java
│       │   └── FileService.java        # 文件服务接口
│       └── utils/                      # 工具类
│           └── IdWorker.java           # ID 生成器
├── src/main/resources/
│   ├── application.yml                 # 主配置文件
│   ├── application-local.yml           # 本地环境配置
│   └── logback-delayed.xml            # 日志配置
├── Dockerfile                          # Docker 镜像构建
├── pom.xml                            # Maven 项目配置
└── README.md                          # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Java 21+
- MySQL 8.0+
- Redis 7.0+
- MinIO 或 S3 兼容存储
- Maven 3.6+
- Docker & Docker Compose (可选)

### 1. 克隆项目

```bash
git clone <repository-url>
cd resource-service
```

### 2. 配置环境变量

创建 `.env` 文件，配置必要的环境变量：

```bash
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=resource_service
DATABASE_USERNAME=your_db_username
DATABASE_PASSWORD=your_db_password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# MinIO/S3 配置
MINIO_URL=http://localhost:9000
MINIO_BUCKET=resource-bucket
MINIO_AK=your_access_key
MINIO_SK=your_secret_key
```

### 3. 构建项目

```bash
mvn clean package -DskipTests
```

### 4. 启动服务

```bash
java -jar target/resource-0.0.1-SNAPSHOT.jar --spring.profiles.active=local
```

### 5. 验证服务

访问 [http://localhost:8030/api/resource](http://localhost:8030/api/resource) 验证服务是否正常启动。

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t resource-service:latest .
```

### 运行容器

```bash
docker run -d --name resource-service \
  -p 8030:8030 \
  -e DATABASE_HOST=your_db_host \
  -e DATABASE_USERNAME=your_db_username \
  -e DATABASE_PASSWORD=your_db_password \
  -e REDIS_HOST=your_redis_host \
  -e MINIO_URL=your_minio_url \
  -e MINIO_AK=your_access_key \
  -e MINIO_SK=your_secret_key \
  resource-service:latest
```

## 📚 API 文档

### 核心接口

#### 1. 文件上传

**POST** `/api/resource/file/upload`

```bash
curl -X POST "http://localhost:8030/api/resource/file/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.jpg"
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": "file-uuid-12345"
}
```

#### 2. 视频文件上传

**POST** `/api/resource/file/upload-video`

```bash
curl -X POST "http://localhost:8030/api/resource/file/upload-video" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/video.mp4"
```

#### 3. 共享文件上传

**POST** `/api/resource/file/share-file-upload`

```bash
curl -X POST "http://localhost:8030/api/resource/file/share-file-upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/large-file.zip"
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "fileId": "file-uuid-12345",
    "type": 1,
    "filename": "large-file.zip"
  }
}
```

#### 4. 文件下载

**GET** `/api/resource/file/download?fileId=file-uuid-12345`

```bash
curl -X GET "http://localhost:8030/api/resource/file/download?fileId=file-uuid-12345" \
  -o downloaded-file.jpg
```

## ⚙️ 配置说明

### 文件大小限制

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `spring.servlet.multipart.max-file-size` | 50MB | 普通文件最大上传大小 |
| `spring.servlet.multipart.max-request-size` | 110MB | 请求最大大小 |
| `spring.servlet.multipart.file-size-threshold` | 100MB | 文件大小阈值 |

### 数据库配置

| 配置项 | 说明 |
|--------|------|
| `spring.datasource.url` | MySQL 连接 URL |
| `spring.datasource.username` | 数据库用户名 |
| `spring.datasource.password` | 数据库密码 |
| `spring.datasource.druid.*` | Druid 连接池配置 |

### S3/MinIO 配置

| 配置项 | 说明 |
|--------|------|
| `amazonaws.s3.url` | S3 服务地址 |
| `amazonaws.s3.bucket` | 存储桶名称 |
| `amazonaws.s3.accessKey` | 访问密钥 |
| `amazonaws.s3.secretKey` | 秘密密钥 |
| `amazonaws.s3.maxConnections` | 最大连接数 |

## 🧪 开发指南

### 运行测试

```bash
# 运行所有测试
mvn test

# 运行特定测试类
mvn test -Dtest=FileServiceTest
```

### 代码质量检查

```bash
# 编译检查
mvn compile

# 代码格式化
mvn spotless:apply
```

### 查看日志

```bash
# 实时查看应用日志
tail -f logs/application.log
```

## 📝 日志说明

### 日志配置

- **日志级别**：通过 `logging.level.*` 配置
- **日志文件**：自动轮转，单文件最大 20MB
- **日志格式**：包含时间戳、日志级别、线程名、类名和消息内容

### 关键日志

```
2024-01-01 10:30:15.123 INFO  [http-nio-8030-exec-1] c.i.r.r.f.s.i.FileServiceImpl : 文件上传成功，文件ID: file-uuid-12345
2024-01-01 10:30:16.456 INFO  [http-nio-8030-exec-2] c.i.r.r.f.s.i.FileServiceImpl : 文件下载成功，文件ID: file-uuid-12345
```

## ❓ 常见问题

### Q: 文件上传失败怎么办？

A: 检查以下几点：
1. 文件大小是否超过限制（普通文件50MB，共享文件100MB）
2. 文件格式是否支持
3. S3/MinIO 服务是否正常运行
4. 数据库连接是否正常

### Q: 如何修改文件大小限制？

A: 在 `application.yml` 中修改以下配置：

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 100MB
      max-request-size: 150MB
```

### Q: 如何监控服务健康状况？

A: 可以通过以下方式监控：
1. 检查应用日志文件
2. 监控数据库连接状态
3. 检查 Redis 连接状态
4. 验证 S3/MinIO 存储服务

### Q: 如何备份文件数据？

A: 
1. **数据库备份**：定期备份文件元数据
2. **存储备份**：配置 S3/MinIO 的备份策略
3. **应用备份**：使用容器镜像备份应用配置

### Q: 支持哪些文件格式？

A: 
- **普通文件**：支持所有格式
- **视频文件**：mp4, webm, ogg, avi, mov, mpeg
- **共享文件**：支持所有格式，但大小限制为100MB

## 🔄 版本更新

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基础文件上传下载功能
- 集成 S3 对象存储
- 支持视频文件专门处理

