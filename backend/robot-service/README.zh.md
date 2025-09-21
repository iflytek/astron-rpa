# Robot 后端服务（Spring Boot）

> 面向 RPA 机器人设计、执行、终端管理、审计与监控的一体化后端服务。

---

## 1. 项目简介

本项目是基于 Spring Boot 的后端服务，提供 RPA
机器人的设计、版本管理、执行编排、计划任务、终端接入/分组、运行监控、审计与通知等能力。项目已集成单点登录（casdoor）、数据访问（MyBatis-Plus +
Druid）、缓存（Redis）、定时任务（Spring Scheduling）、远程调用（OpenFeign，随 starter 提供）、日志（Logback）等基础设施。

- 应用名：`robot`
- 运行端口：默认 `8040`
- 上下文路径：`/api/robot`
- Java 版本：`8`
- Spring Boot：`2.3.11.RELEASE`
- Spring Cloud：`2023.0.1`

---

## 2. 技术栈与中间件

- 核心框架
    - Spring Boot（Web / Validation / AOP / Scheduling / Session）
    - MyBatis-Plus（DAO 层简化、分页）
    - Druid（数据源与监控）
    - Spring Data Redis（分布式缓存、限流/防抖、Session 存储）
    - iflytek-rpa-starter（统一用户-casdoor 接入、通用工具、响应封装等）
    - OpenFeign（随 starter 提供，`@EnableFeignClients` 已开启）
    - Spring Session（Redis Session 管理）
- 工具与库
    - Lombok、Apache Commons、Jsoup、EasyPOI（报表导出）
- 日志
    - Logback（控制台 + 滚动文件，路径 `/opt/log/rpa/${spring.application.name}/`）
- 存储
    - MySQL（驱动 `com.mysql.cj.jdbc.Driver`）
    - Redis（String/Key 操作、管道与事务支持）
    - 对象存储（S3 兼容端点配置在 `amazonaws.s3.*`）
- 容器化/可观测
    - 基础镜像：`openjdk8-with-skywalking8.6.3`
    - 可集成 SkyWalking 探针（Dockerfile 已包含 agent 拷贝动作）

---

## 3. 目录结构

```
src/main/java/com/iflytek/rpa/
├─ RobotApplication.java        // 应用启动类（@SpringBootApplication, @EnableFeignClients, @EnableScheduling, @EnableRedisHttpSession, @EnableAsync）
├─ conf/                        // 全局配置与基础控制器
│  ├─ ApiContext.java           // 简单的请求上下文（tenantId/userId 等）
│  ├─ LoginController.java      // 登录状态、登出、用户信息（基于 casdoor）
│  ├─ FeignConfiguration.java   // Feign 相关配置（如超时/日志等，如果有）
│  ├─ MybatisPlusConfig.java    // 分页插件等
│  └─ RedisConfig.java          // 启用 Redis 事务支持
├─ base/                        // 基础元数据模块（原子、流程、参数、模块、分组、全局变量等）
├─ robot/                       // 机器人核心：设计、版本、执行、共享变量/文件、资源管理
├─ task/                        // 计划任务：任务定义、执行记录、拉取日志等
├─ triggerTask/                 // 触发任务：触发规则/任务邮箱等
├─ terminal/                    // 终端接入与管理：注册、心跳、分组、登录记录
├─ monitor/                     // 监控与统计：历史终端/机器人、统计报表
├─ notify/                      // 通知发送
├─ auditRecord/                 // 审计记录（告警规则、审计日志）
├─ market/                      // 市场/应用管理扩展
├─ component/                   // 组件管理模块
├─ dispatch/                    // 任务调度模块
└─ utils/                       // 通用工具（分页、时间、ID、HTTP、防抖、监控辅助等）

src/main/resources/
├─ bootstrap.yml                // 应用名/端口/上下文、默认 profile
├─ application-local.yml        // 本地开发配置
├─ application-dev.yml          // 开发环境配置
├─ application-uat.yml          // UAT 配置
├─ application-prod.yml         // 生产配置
└─ logback-delayed.xml          // 日志配置
```

---

## 4. 配置说明

> 默认激活 profile：`local`（见 `bootstrap.yml`）。请在不同环境下覆盖敏感信息（DB/Redis/casdoor/S3）。示例配置文件中的账号密码仅为占位/示例，务必替换为安全来源（环境变量、K8s
> Secret 等）。

- Web 服务
    - `server.port`: 默认 `8004`
    - `server.servlet.context-path`: `/api/robot`
- 数据源（MySQL + Druid）
    - `spring.datasource.*`：驱动、连接池（`stat,wall,slf4j` 过滤器）、慢 SQL 日志
- ORM（MyBatis-Plus）
    - `mybatis-plus.mapper-locations: classpath:/mapper/*/*.xml`
    - 逻辑删除：`logic-delete-value: 1` / `logic-not-delete-value: 0`
    - 分页插件：`PaginationInterceptor`（见 `MybatisPlusConfig`）
- 缓存（Redis）
    - `spring.redis.*`：库、地址、连接池、超时
    - 事务：在 `RedisConfig` 里启用 `StringRedisTemplate` 事务支持
    - 项目自定义：`redis.open` 开关、防抖配置 `deBounce.prefix/window`
- 鉴权（casdoor SSO）
    - `casdoor.cas-server-context` / `rest-server-url`：casdoor 服务地址
    - `casdoor.cas-client-context`：当前应用后端上下文地址（注意是后端，不是前端）
    - `casdoor.session-filter-exclude` / `casdoor.access-auth-exclude`：登录/鉴权白名单
    - `cas.client.context` / `cas.client.index`：登录后跳转/首页
    - `allowed.origins`：跨域域名白名单
- 报表/导出（EasyPOI）
    - `report.export.strategy: excel`、缓冲/Sheet 名称、文件命名模板
- 对象存储（S3 兼容）
    - `amazonaws.s3.url/accessKey/secretKey/bucket/prefix/maxConnections`
    - 注意：请不要在代码库中保留真实密钥，建议使用环境变量注入
- 日志
    - 控制台 + 滚动文件（小时切分，单文件 20MB，总量 10GB，最长保留 4320 小时）

---

## 5. 模块与接口概览

以下仅列出模块级别的基础路由前缀，详细接口可通过源码 `@GetMapping/@PostMapping` 查看：

- 认证与用户
    - `GET /login-status`：查询登录态
    - `POST /logout`：登出并清理终端实时数据、同步离线状态
    - `GET /user/info`：获取当前登录用户信息
- 终端（`/terminal*`）
    - `/terminal`：注册、心跳、分页
    - `/terminal-group`：分组管理、成员管理
    - `/terminal-manage`、`/terminal-monitor`：终端信息、监控数据、趋势
- 机器人（`/robot-*`）
    - `/robot-design`：创建、重命名、列表、详情、复制、删除、分享
    - `/robot-version`：同名校验、发布、启用/恢复、列表
    - `/robot-execute`：执行列表、删除、更新、详情、执行前检查
    - `/robot-record`：执行记录列表、日志、详情、结果保存、批量删除
    - `/robot-shared-var`、`/robot-shared-file`：共享变量/文件管理
    - `/robot-manage`：资源/部署/转移/版本/执行统计等
- 计划任务与触发器（`/task*`、`/triggerTask`）
    - `/task`：任务列表、保存、启停、删除、名称校验、下次时间
    - `/task-execute`：执行状态、列表、批量删除
    - `/triggerTask`：触发器名称校验、插入/查询/删除/更新、分页等
    - `/taskMail`：任务邮箱连接、保存、删除
- 基础元数据（`/atom`、`/param`、`/module`、`/process`、`/group`、`/global`、`/require`、`/element` 等）
- 市场与应用（`/market-*`、`/application`）
- 监控（`/his-*`）与审计（`/record`）
- 通知（`/notify`）

> 提示：控制器位于各模块的 `controller` 包下；DAO 继承 `BaseMapper<T>`，位于 `dao/mapper`
> 包；实体与常量在 `entity/constants` 包；`annotation` 包含模块自定义注解（若有）。

---

## 6. 核心流程

- 鉴权与会话（casdoor）
- 终端接入与状态
    - 终端注册 `/terminal/register`、心跳 `/terminal/beat`；实时状态存储于 Redis（Key 前缀见业务常量）
    - 登出时清理 `TERMINAL_KEY_REAL_TIME + terminalId` 并将终端状态同步 MySQL
- 机器人设计/版本/执行
    - 设计/版本/执行分别由 `robot` 模块下的 Controller + Service + Dao 组成
    - 执行记录支持分页检索、日志/详情查看、结果保存与批量清理
- 计划任务与触发
    - 开启 `@EnableScheduling`；典型任务：
        - `TerminalServiceImpl`：终端状态巡检与数据清理（`fixedRate=35s/10m`）
        - `SharedVarServiceImpl`：共享变量每日维护（`cron: 1 0 0 * * *`）
        - `StatisticsServiceImpl`：统计报表任务（`cron: 0 0 1 * * ?`）
- 缓存与防抖
    - `DeBounceUtils` 使用 Redis 构建基于 Key 的防抖窗口（毫秒级），窗口与前缀可在配置项 `deBounce.*` 调整
    - 批量读写/管道：在终端与监控服务中使用 `RedisTemplate.executePipelined`
- 报表导出
    - 基于 EasyPOI；导出参数（Sheet 名、缓冲区、命名模板、最大行数）可在 `report.*` 下配置
- 上下文与多租户
    - `ApiContext` 暴露 tenantId/userId 设置与获取方法；建议后续结合拦截器或 ThreadLocal 优化隔离

---

## 7. 构建与运行

- 先决条件
    - JDK 8、Maven 3.6+
    - 可用的 MySQL 与 Redis 实例
    - casdoor 服务可达（local 环境可按需关闭鉴权或使用白名单）

- 本地运行

```bash
# 1) 替换 application-local.yml 中的数据库/Redis/casdoor/S3 等敏感配置
# 2) 编译打包（缺省已配置 <skipTests>true</skipTests>）
mvn clean package -DskipTests

# 3) 运行
java -jar target/robot-0.0.1-SNAPSHOT.jar --spring.profiles.active=local

# 可选：调整端口/上下文
# --server.port=8040 --server.servlet.context-path=/api/robot
```

- Docker 镜像（示例）

```bash
# 构建镜像（确保 target/*.jar 已存在）
docker build -t robot:local .

# 运行（请用环境变量覆盖敏感配置）
docker run -d --name robot \
  -p 8040:8040 \
  -e JAVA_TOOL_OPTIONS="-javaagent:/skywalking-agent/agent/skywalking-agent.jar" \
  -e SW_AGENT_NAME=robot \
  -e SPRING_PROFILES_ACTIVE=prod \
  robot:local
```

> 注：`Dockerfile` 基于带 SkyWalking 的 JDK8 镜像，默认会将 `target/*.jar` 放置到根目录，并拷贝 `skywalking-agent`
> 。启动命令可在编排中（K8s/Compose）通过 `CMD` 或 `args` 指定。

---

## 8. 开发约定

- 分层规范
    - `controller` 只做入参校验与编排，`service` 承载业务，`dao` 仅做数据访问，`entity` 为数据模型
    - 分页统一走 MyBatis-Plus 分页插件；返回统一使用 `AppResponse`
- 命名与风格
    - 变量/方法名语义化，避免缩写；复杂条件使用中间变量表达含义
    - 见仓库中的 `utils` 工具类，优先复用
- 错误与边界
    - 优先使用早返回（guard clauses），限制嵌套深度
    - 对外接口校验 `@Valid`/`@Validated`；对公共方法做空值校验
- 日志
    - 关键流程 DEBUG/INFO，异常 WARN/ERROR；避免输出敏感信息

---

## 9. 常见问题（FAQ）

- 启动后 401/403？
    - 检查 casdoor 服务地址、`session-filter-exclude` 与 `access-auth-exclude` 白名单
- Mapper XML 未被加载？
    - 确认 `mybatis-plus.mapper-locations` 与 `pom.xml` 中对 `src/main/java/**/*.xml` 的资源打包配置
- Redis 事务不生效？
    - 确认 `RedisConfig` 已启用 `StringRedisTemplate.setEnableTransactionSupport(true)`，并在需要的逻辑中正确使用事务
- 导出 Excel OOM？
    - 请调小 `report.excel.buffer.size` 与 `robot.maxLines`，或分页导出
- 日志文件未生成？
    - 检查容器/主机是否有 `/opt/log/rpa/` 写入权限；或自定义 Logback 配置

---

## 10. 安全与合规

- 切勿在代码仓库中提交真实的数据库、Redis、casdoor、S3 账号与密钥
- 建议通过环境变量、外部配置中心或 K8s Secret 注入敏感信息
- 日志中不要输出用户隐私与鉴权令牌

---

## 11. 变更记录（维护建议）

- 在此记录重要的接口变更、数据结构变更、配置项调整与迁移路径，便于版本管理与团队协作

---

## 12. 参考

- Spring Boot、MyBatis-Plus、Druid、Spring Data Redis、EasyPOI
- casdoor 统一认证