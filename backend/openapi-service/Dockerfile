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
COPY backend/openapi-service/pyproject.toml backend/openapi-service/uv.lock ./

# 复制rpawebsocket wheel文件
COPY backend/openapi-service/app/utils/rpawebsocket-1.0.5-py3-none-any.whl ./

# 安装项目依赖
RUN pip install --no-cache-dir -e .

# 安装本地rpawebsocket wheel文件
RUN pip install --no-cache-dir rpawebsocket-1.0.5-py3-none-any.whl

# 复制项目代码
COPY backend/openapi-service/app/ ./app/

# 复制配置文件（如果存在）
COPY docker/.env ./.env

# 暴露端口
EXPOSE 8020

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020", "--proxy-headers", "--workers", "4"]