# 多阶段构建 Dockerfile for Java 8 Spring Boot Application

# 第一阶段：构建JAR包
FROM maven:3.8.6-jdk-8 AS build

# 设置工作目录
WORKDIR /app

# 复制Maven配置文件
COPY backend/rpa-auth/pom.xml .

# 复制 lib 目录（opensource profile 需要）
COPY backend/rpa-auth/lib ./lib

# 安装 rpa-auth-stubs 的 JAR
RUN if [ -f "./lib/rpa-auth-stubs-1.0.0.jar" ]; then \
    mvn install:install-file \
        -Dfile=./lib/rpa-auth-stubs-1.0.0.jar \
        -DgroupId=com.iflytek.rpa \
        -DartifactId=rpa-auth-stubs \
        -Dversion=1.0.0 \
        -Dpackaging=jar; \
    else \
        echo "错误: 找不到 lib/rpa-auth-stubs-1.0.0.jar"; \
        exit 1; \
    fi

# 下载依赖（利用Docker缓存层）
RUN mvn dependency:go-offline -B -P opensource

# 复制源代码
COPY backend/rpa-auth/src ./src

# 构建应用（启用 opensource profile）
RUN mvn clean package -DskipTests -P opensource

# 第二阶段：构建可执行镜像
FROM eclipse-temurin:8-jre AS runtime

# 设置工作目录
WORKDIR /app

# 安装必要的工具
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制JAR文件
COPY --from=build /app/target/*.jar app.jar

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 10251

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置JVM参数
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -Djava.security.egd=file:/dev/./urandom"

# 启动应用
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
