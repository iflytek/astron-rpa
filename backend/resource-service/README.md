# Resource Service - Resource Management Service

## 📖 Project Introduction

Resource Service is a resource management service built on Spring Boot 3.2.4, specifically designed for handling file upload, download, storage and management. The service integrates S3-compatible object storage (MinIO), MySQL database, Redis caching and other infrastructure, providing complete file lifecycle management functionality.

### ✨ Key Features

- 📁 **File Upload Management** - Support for multiple file format uploads, including regular files and video files
- 🔗 **File Download Service** - Secure file download based on file ID
- 🎥 **Video File Support** - Specially optimized video file upload and format validation
- 📤 **Shared File Upload** - Support for shared file upload and return file metadata
- 🗄️ **S3 Object Storage** - Integration with MinIO and other S3-compatible storage services
- 📊 **File Metadata Management** - Complete file information recording and querying
- 🔧 **Asynchronous High Performance** - Based on Spring Boot 3 async framework, supporting high concurrency file processing
- 🐳 **Containerized Deployment** - Complete Docker deployment solution

## 🚀 Core Functions

### 1. File Upload (`/file/upload`)
- Support for maximum 50MB file upload
- Automatic file type detection and validation
- Return unique file ID for subsequent operations

### 2. Video File Upload (`/file/upload-video`)
- Support for maximum 50MB video file upload
- Supported formats: mp4, webm, ogg, avi, mov, mpeg
- Specialized video format validation

### 3. Shared File Upload (`/file/share-file-upload`)
- Support for maximum 100MB file upload
- Return file ID, type and filename information
- Suitable for large file processing in sharing scenarios

### 4. File Download (`/file/download`)
- Secure download based on file ID
- Support for various file format downloads
- Complete download permission control

## 🛠 Technology Stack

| Component | Technology | Version Requirement |
|-----------|------------|-------------------|
| **Backend Framework** | Spring Boot | 3.2.4 |
| **Java** | Java | 21 |
| **Database** | MySQL + MyBatis-Plus | 8.0.28 / 3.5.5 |
| **Object Storage** | AWS S3 SDK | 2.17.102 |
| **Connection Pool** | Druid | 1.2.16 |
| **Cache** | Redis | - |
| **Build Tool** | Maven | 3.6+ |
| **Containerization** | Docker | - |
| **Logging Framework** | Logback | - |

## 📁 Project Structure

```
resource-service/
├── src/main/java/com/iflytek/rpa/resource/
│   ├── ResourceApplication.java           # Spring Boot application startup class
│   ├── common/                           # Common components
│   │   ├── exp/                          # Exception handling
│   │   │   ├── GlobalExceptionHandler.java
│   │   │   └── ServiceException.java
│   │   └── response/                     # Response encapsulation
│   │       ├── AppResponse.java
│   │       └── ErrorCodeEnum.java
│   └── file/                            # File management module
│       ├── config/                      # Configuration classes
│       │   └── S3Config.java           # S3 storage configuration
│       ├── controller/                  # Controllers
│       │   └── FileController.java     # File operation controller
│       ├── dao/                        # Data access layer
│       │   ├── FileMapper.java
│       │   └── FileMapper.xml
│       ├── entity/                     # Entity classes
│       │   ├── enums/                  # Enum classes
│       │   │   └── FileType.java
│       │   ├── vo/                     # View objects
│       │   │   └── ShareFileUploadVo.java
│       │   └── File.java              # File entity
│       ├── service/                    # Service layer
│       │   ├── impl/                   # Service implementations
│       │   │   └── FileServiceImpl.java
│       │   └── FileService.java        # File service interface
│       └── utils/                      # Utility classes
│           └── IdWorker.java           # ID generator
├── src/main/resources/
│   ├── application.yml                 # Main configuration file
│   ├── application-local.yml           # Local environment configuration
│   └── logback-delayed.xml            # Logging configuration
├── Dockerfile                          # Docker image build
├── pom.xml                            # Maven project configuration
└── README.md                          # Project documentation
```

## 🚀 Quick Start

### Environment Requirements

- Java 21+
- MySQL 8.0+
- Redis 7.0+
- MinIO or S3-compatible storage
- Maven 3.6+
- Docker & Docker Compose (optional)

### 1. Clone Project

```bash
git clone <repository-url>
cd resource-service
```

### 2. Configure Environment Variables

Create `.env` file and configure necessary environment variables:

```bash
# Database configuration
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=resource_service
DATABASE_USERNAME=your_db_username
DATABASE_PASSWORD=your_db_password

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# MinIO/S3 configuration
MINIO_URL=http://localhost:9000
MINIO_BUCKET=resource-bucket
MINIO_AK=your_access_key
MINIO_SK=your_secret_key
```

### 3. Build Project

```bash
mvn clean package -DskipTests
```

### 4. Start Service

```bash
java -jar target/resource-0.0.1-SNAPSHOT.jar --spring.profiles.active=local
```

### 5. Verify Service

Visit [http://localhost:8030/api/resource](http://localhost:8030/api/resource) to verify service startup.

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t resource-service:latest .
```

### Run Container

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

## 📚 API Documentation

### Core Interfaces

#### 1. File Upload

**POST** `/api/resource/file/upload`

```bash
curl -X POST "http://localhost:8030/api/resource/file/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.jpg"
```

**Response Format:**
```json
{
  "code": 200,
  "message": "success",
  "data": "file-uuid-12345"
}
```

#### 2. Video File Upload

**POST** `/api/resource/file/upload-video`

```bash
curl -X POST "http://localhost:8030/api/resource/file/upload-video" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/video.mp4"
```

#### 3. Shared File Upload

**POST** `/api/resource/file/share-file-upload`

```bash
curl -X POST "http://localhost:8030/api/resource/file/share-file-upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/large-file.zip"
```

**Response Format:**
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

#### 4. File Download

**GET** `/api/resource/file/download?fileId=file-uuid-12345`

```bash
curl -X GET "http://localhost:8030/api/resource/file/download?fileId=file-uuid-12345" \
  -o downloaded-file.jpg
```

## ⚙️ Configuration

### File Size Limits

| Configuration | Default Value | Description |
|---------------|---------------|-------------|
| `spring.servlet.multipart.max-file-size` | 50MB | Maximum upload size for regular files |
| `spring.servlet.multipart.max-request-size` | 110MB | Maximum request size |
| `spring.servlet.multipart.file-size-threshold` | 100MB | File size threshold |

### Database Configuration

| Configuration | Description |
|---------------|-------------|
| `spring.datasource.url` | MySQL connection URL |
| `spring.datasource.username` | Database username |
| `spring.datasource.password` | Database password |
| `spring.datasource.druid.*` | Druid connection pool configuration |

### S3/MinIO Configuration

| Configuration | Description |
|---------------|-------------|
| `amazonaws.s3.url` | S3 service address |
| `amazonaws.s3.bucket` | Bucket name |
| `amazonaws.s3.accessKey` | Access key |
| `amazonaws.s3.secretKey` | Secret key |
| `amazonaws.s3.maxConnections` | Maximum connections |

## 🧪 Development Guide

### Running Tests

```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=FileServiceTest
```

### Code Quality Check

```bash
# Compile check
mvn compile

# Code formatting
mvn spotless:apply
```

### View Logs

```bash
# Real-time view of application logs
tail -f logs/application.log
```

## 📝 Logging

### Log Configuration

- **Log Level**: Configured via `logging.level.*`
- **Log Files**: Auto-rotation, single file max 20MB
- **Log Format**: Contains timestamp, log level, thread name, class name and message content

### Key Logs

```
2024-01-01 10:30:15.123 INFO  [http-nio-8030-exec-1] c.i.r.r.f.s.i.FileServiceImpl : File upload successful, file ID: file-uuid-12345
2024-01-01 10:30:16.456 INFO  [http-nio-8030-exec-2] c.i.r.r.f.s.i.FileServiceImpl : File download successful, file ID: file-uuid-12345
```

## ❓ FAQ

### Q: What to do when file upload fails?

A: Check the following points:
1. Whether file size exceeds limit (regular files 50MB, shared files 100MB)
2. Whether file format is supported
3. Whether S3/MinIO service is running normally
4. Whether database connection is normal

### Q: How to modify file size limits?

A: Modify the following configuration in `application.yml`:

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 100MB
      max-request-size: 150MB
```

### Q: How to monitor service health?

A: You can monitor through:
1. Check application log files
2. Monitor database connection status
3. Check Redis connection status
4. Verify S3/MinIO storage service

### Q: How to backup file data?

A: 
1. **Database Backup**: Regularly backup file metadata
2. **Storage Backup**: Configure S3/MinIO backup strategy
3. **Application Backup**: Use container images to backup application configuration

### Q: What file formats are supported?

A: 
- **Regular Files**: Support all formats
- **Video Files**: mp4, webm, ogg, avi, mov, mpeg
- **Shared Files**: Support all formats, but size limit is 100MB

## 🔄 Version Updates

### v1.0.0 (2024-01-01)
- Initial version release
- Support for basic file upload/download functionality
- Integration with S3 object storage
- Support for specialized video file processing

## 📜 License

This project is licensed under the MIT License. You are free to use, modify and distribute this code for both personal and commercial projects.