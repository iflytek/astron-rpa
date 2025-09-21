# 多阶段构建 Dockerfile for Java 21 Spring Boot Application

# 第一阶段：构建JAR包
FROM maven:3.9-eclipse-temurin-21 AS build

# 设置工作目录
WORKDIR /app

# 复制Maven配置文件
COPY backend/resource-service/pom.xml .

# 下载依赖（利用Docker缓存层）
RUN mvn dependency:go-offline -B

# 复制源代码
COPY backend/resource-service/src ./src

# 构建应用
RUN mvn clean package -DskipTests

# 第二阶段：构建可执行镜像
FROM openjdk:21-slim AS runtime

# 设置工作目录
WORKDIR /app

# 从构建阶段复制JAR文件
COPY --from=build /app/target/*.jar app.jar

# 复制配置文件（如果存在）
COPY docker/.env ./.env

# 暴露端口
EXPOSE 8030

# 设置JVM参数
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:+UseContainerSupport"

# 启动应用
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
