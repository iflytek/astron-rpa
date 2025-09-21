# 使用官方Python镜像作为基础镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip

# 复制项目依赖文件
COPY backend/ai-service/pyproject.toml backend/ai-service/uv.lock ./

# 安装项目依赖
RUN pip install --no-cache-dir -e .

# 复制项目代码
COPY backend/ai-service/app/ ./app/

# 复制配置文件（如果存在）
COPY docker/.env ./.env

# 暴露端口
EXPOSE 8010


# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010", "--proxy-headers", "--workers", "4"]