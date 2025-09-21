# Robot Backend Service (Spring Boot)

> A comprehensive backend service for RPA robot design, execution, terminal management, auditing and monitoring.

---

## 1. Project Introduction

This project is a backend service based on Spring Boot, providing RPA robot design, version management, execution
orchestration, scheduled tasks, terminal access/grouping, runtime monitoring, auditing and notification capabilities.
The project has integrated single sign-on (casdoor), data access (MyBatis-Plus + Druid), caching (Redis), scheduled
tasks (Spring Scheduling), remote calls (OpenFeign, provided with starter), logging (Logback) and other infrastructure.

- Application Name: `robot`
- Running Port: Default `8040`
- Context Path: `/api/robot`
- Java Version: `8`
- Spring Boot: `2.3.11.RELEASE`
- Spring Cloud: `2023.0.1`

---

## 2. Technology Stack and Middleware

- Core Framework
    - Spring Boot (Web / Validation / AOP / Scheduling / Session)
    - MyBatis-Plus (DAO layer simplification, pagination)
    - Druid (data source and monitoring)
    - Spring Data Redis (distributed caching, rate limiting/anti-shake)
    - iflytek-rpa-starter (unified user-casdoor integration, common utilities, response encapsulation, etc.)
    - OpenFeign (provided with starter, `@EnableFeignClients` enabled)
    - Spring Session (Redis Session management)
- Tools and Libraries
    - Lombok, Apache Commons, Jsoup, EasyPOI (report export)
- Logging
    - Logback (console + rolling files, path `/opt/log/rpa/${spring.application.name}/`)
- Storage
    - MySQL (driver `com.mysql.cj.jdbc.Driver`)
    - Redis (String/Key operations, pipeline and transaction support)
    - Object Storage (S3 compatible endpoint configured in `amazonaws.s3.*`)
- Containerization/Observability
    - Base Image: `openjdk8-with-skywalking8.6.3`
    - Can integrate SkyWalking probe (Dockerfile already includes agent copy action)

---

## 3. Directory Structure

```
src/main/java/com/iflytek/rpa/
├─ RobotApplication.java        // Application startup class (@SpringBootApplication, @EnableFeignClients, @EnableScheduling, @EnableRedisHttpSession, @EnableAsync)
├─ conf/                        // Global configuration and base controllers
│  ├─ ApiContext.java           // Simple request context (tenantId/userId, etc.)
│  ├─ LoginController.java      // Login status, logout, user info (based on casdoor)
│  ├─ FeignConfiguration.java   // Feign related configuration (timeout/logging, etc., if any)
│  ├─ MybatisPlusConfig.java    // Pagination plugin, etc.
│  └─ RedisConfig.java          // Enable Redis transaction support
├─ base/                        // Base metadata module (atoms, processes, parameters, modules, groups, global variables, etc.)
├─ robot/                       // Robot core: design, version, execution, shared variables/files, resource management
├─ task/                        // Scheduled tasks: task definition, execution records, log pulling, etc.
├─ triggerTask/                 // Trigger tasks: trigger rules/task mailboxes, etc.
├─ terminal/                    // Terminal access and management: registration, heartbeat, grouping, login records
├─ monitor/                     // Monitoring and statistics: historical terminals/robots, statistical reports
├─ notify/                      // Notification sending
├─ auditRecord/                 // Audit records (alarm rules, audit logs)
├─ market/                      // Market/application management extensions
├─ component/                   // Component management module
├─ dispatch/                    // Task dispatch module
└─ utils/                       // Common utilities (pagination, time, ID, HTTP, anti-shake, monitoring assistance, etc.)

src/main/resources/
├─ bootstrap.yml                // Application name/port/context, default profile
├─ application-local.yml        // Local development configuration
├─ application-dev.yml          // Development environment configuration
├─ application-uat.yml          // UAT configuration
├─ application-prod.yml         // Production configuration
└─ logback-delayed.xml          // Logging configuration
```

---

## 4. Configuration

> Default active profile: `local` (see `bootstrap.yml`). Please override sensitive information (DB/Redis/casdoor/S3) in
> different environments. Account passwords in example configuration files are only placeholders/examples and must be
> replaced with secure sources (environment variables, K8s Secrets, etc.).

- Web Service
    - `server.port`: Default `8040`
    - `server.servlet.context-path`: `/api/robot`
- Data Source (MySQL + Druid)
    - `spring.datasource.*`: Driver, connection pool (`stat,wall,slf4j` filters), slow SQL logging
- ORM (MyBatis-Plus)
    - `mybatis-plus.mapper-locations: classpath:/mapper/*/*.xml`
    - Logical deletion: `logic-delete-value: 1` / `logic-not-delete-value: 0`
    - Pagination plugin: `PaginationInterceptor` (see `MybatisPlusConfig`)
- Cache (Redis)
    - `spring.redis.*`: Database, address, connection pool, timeout
    - Transactions: Enable `StringRedisTemplate` transaction support in `RedisConfig`
    - Project custom: `redis.open` switch, anti-shake configuration `deBounce.prefix/window`
- Authentication (casdoor SSO)
    - `casdoor.cas-server-context` / `rest-server-url`: casdoor service address
    - `casdoor.cas-client-context`: Current application backend context address (note: backend, not frontend)
    - `casdoor.session-filter-exclude` / `casdoor.access-auth-exclude`: Login/authentication whitelist
    - `cas.client.context` / `cas.client.index`: Post-login redirect/homepage
    - `allowed.origins`: Cross-origin domain whitelist
- Reports/Export (EasyPOI)
    - `report.export.strategy: excel`, buffer/Sheet names, file naming templates
- Object Storage (S3 Compatible)
    - `amazonaws.s3.url/accessKey/secretKey/bucket/prefix/maxConnections`
    - Note: Please do not keep real keys in code repository, recommend using environment variable injection
- Logging
    - Console + rolling files (hourly split, single file 20MB, total 10GB, max retention 4320 hours)

---

## 5. Modules and Interface Overview

The following only lists module-level basic route prefixes. Detailed interfaces can be viewed through source
code `@GetMapping/@PostMapping`:

- Authentication and Users
    - `GET /login-status`: Query login status
    - `POST /logout`: Logout and clean terminal real-time data, sync offline status
    - `GET /user/info`: Get current logged-in user info
- Terminals (`/terminal*`)
    - `/terminal`: Registration, heartbeat, pagination
    - `/terminal-group`: Group management, member management
    - `/terminal-manage`, `/terminal-monitor`: Terminal info, monitoring data, trends
- Robots (`/robot-*`)
    - `/robot-design`: Create, rename, list, details, copy, delete, share
    - `/robot-version`: Same name validation, publish, enable/restore, list
    - `/robot-execute`: Execution list, delete, update, details, pre-execution check
    - `/robot-record`: Execution record list, logs, details, result save, batch delete
    - `/robot-shared-var`, `/robot-shared-file`: Shared variable/file management
    - `/robot-manage`: Resource/deployment/transfer/version/execution statistics, etc.
- Scheduled Tasks and Triggers (`/task*`, `/triggerTask`)
    - `/task`: Task list, save, start/stop, delete, name validation, next time
    - `/task-execute`: Execution status, list, batch delete
    - `/triggerTask`: Trigger name validation, insert/query/delete/update, pagination, etc.
    - `/taskMail`: Task mailbox connection, save, delete
- Base Metadata (`/atom`, `/param`, `/module`, `/process`, `/group`, `/global`, `/require`, `/element`, etc.)
- Market and Applications (`/market-*`, `/application`)
- Monitoring (`/his-*`) and Auditing (`/record`)
- Notifications (`/notify`)

> Tip: Controllers are located in `controller` packages of each module; DAOs inherit `BaseMapper<T>`, located
> in `dao/mapper` packages; entities and constants in `entity/constants` packages; `annotation` contains module custom
> annotations (if any).

---

## 6. Core Processes

- Authentication and Session (casdoor)

- Terminal Access and Status
    - Terminal registration `/terminal/register`, heartbeat `/terminal/beat`; real-time status stored in Redis (Key
      prefix see business constants)
    - Logout cleans `TERMINAL_KEY_REAL_TIME + terminalId` and syncs terminal status to MySQL
- Robot Design/Version/Execution
    - Design/version/execution composed of Controller + Service + Dao under `robot` module
    - Execution records support paginated retrieval, log/details viewing, result saving and batch cleanup
- Scheduled Tasks and Triggers
    - Enable `@EnableScheduling`; typical tasks:
        - `TerminalServiceImpl`: Terminal status inspection and data cleanup (`fixedRate=35s/10m`)
        - `SharedVarServiceImpl`: Shared variable daily maintenance (`cron: 1 0 0 * * *`)
        - `StatisticsServiceImpl`: Statistical report tasks (`cron: 0 0 1 * * ?`)
- Cache and Anti-shake
    - `DeBounceUtils` uses Redis to build Key-based anti-shake window (millisecond level), window and prefix adjustable
      in config `deBounce.*`
    - Batch read/write/pipeline: Use `RedisTemplate.executePipelined` in terminal and monitoring services
- Report Export
    - Based on EasyPOI; export parameters (Sheet name, buffer, naming template, max rows) configurable in `report.*`
- Context and Multi-tenancy
    - `ApiContext` exposes tenantId/userId set and get methods; recommend combining with interceptors or ThreadLocal for
      isolation optimization

---

## 7. Build and Run

- Prerequisites
    - JDK 8, Maven 3.6+
    - Available MySQL and Redis instances
    - casdoor service reachable (local environment can disable authentication or use whitelist as needed)

- Local Run

```bash
# 1) Replace database/Redis/casdoor/S3 sensitive configurations in application-local.yml
# 2) Compile and package (default configured <skipTests>true</skipTests>)
mvn clean package -DskipTests

# 3) Run
java -jar target/robot-0.0.1-SNAPSHOT.jar --spring.profiles.active=local

# Optional: adjust port/context
# --server.port=8040 --server.servlet.context-path=/api/robot
```

- Docker Image (Example)

```bash
# Build image (ensure target/*.jar exists)
docker build -t robot:local .

# Run (please override sensitive configurations with environment variables)
docker run -d --name robot \
  -p 8040:8040 \
  -e JAVA_TOOL_OPTIONS="-javaagent:/skywalking-agent/agent/skywalking-agent.jar" \
  -e SW_AGENT_NAME=robot \
  -e SPRING_PROFILES_ACTIVE=prod \
  robot:local
```

> Note: `Dockerfile` based on JDK8 image with SkyWalking, default places `target/*.jar` to root directory and
> copies `skywalking-agent`. Startup command can be specified via `CMD` or `args` in orchestration (K8s/Compose).

---

## 8. Development Conventions

- Layering Standards
    - `controller` only does input validation and orchestration, `service` carries business logic, `dao` only does data
      access, `entity` is data model
    - Pagination uniformly uses MyBatis-Plus pagination plugin; returns uniformly use `AppResponse`
- Naming and Style
    - Variable/method names semantic, avoid abbreviations; complex conditions use intermediate variables to express
      meaning
    - See `utils` utility classes in repository, prioritize reuse
- Error and Boundaries
    - Prioritize early return (guard clauses), limit nesting depth
    - External interfaces validate `@Valid`/`@Validated`; validate public methods for null values
- Logging
    - Key processes DEBUG/INFO, exceptions WARN/ERROR; avoid outputting sensitive information

---

## 9. Common Issues (FAQ)

- 401/403 after startup?
    - Check casdoor service address, `session-filter-exclude` and `access-auth-exclude` whitelist
- Mapper XML not loaded?
    - Confirm `mybatis-plus.mapper-locations` and `pom.xml` resource packaging configuration
      for `src/main/java/**/*.xml`
- Redis transactions not working?
    - Confirm `RedisConfig` enabled `StringRedisTemplate.setEnableTransactionSupport(true)` and correctly use
      transactions in needed logic
- Excel export OOM?
    - Please reduce `report.excel.buffer.size` and `robot.maxLines`, or paginated export
- Log files not generated?
    - Check if container/host has write permissions for `/opt/log/rpa/`; or customize Logback configuration

---

## 10. Security and Compliance

- Never commit real database, Redis, casdoor, S3 accounts and keys to code repository
- Recommend injecting sensitive information through environment variables, external configuration center or K8s Secrets
- Do not output user privacy and authentication tokens in logs

---

## 11. Change Records (Maintenance Recommendations)

- Record important interface changes, data structure changes, configuration adjustments and migration paths here for
  version management and team collaboration

---

## 12. References

- Spring Boot, MyBatis-Plus, Druid, Spring Data Redis, EasyPOI
- casdoor Unified Authentication 
