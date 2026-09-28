# n8n MCP 公共框架验收记录

本文保留公共框架的历史验收记录；浏览器读取与服务连接的本轮结果见文末独立记录（2026-09-20），对应机器可读证据的 `browserServiceValidation` 字段。

本次新增独立的 AstronRPA Community Node，通过 HTTPS MCP 完成工作流读取、执行、查询和取消，并在 OpenAPI 服务中实现工作流声明与准入校验。已完成相关自动化测试，以及真实 n8n、OpenAPI 服务和 Windows 客户端联调；全仓质量检查和运行中设计器发布的组合验证存在未完成项，详见文末。

使用方法见[节点说明](n8n-nodes-astron-rpa/README.md)和[工作流示例](n8n-nodes-astron-rpa/examples/README.md)。执行标识、恢复前后期限、产物校验值及发布时序见[验证证据](validation-evidence.json)。

## 本次实现

- 新增[Community Node](n8n-nodes-astron-rpa/nodes/AstronRpa/AstronRpa.node.ts)及凭据类型，提供工作流列表、详情、Async／Wait／Sync 执行、执行查询和精准取消，业务操作统一通过 MCP。
- 实现[持久等待编排](n8n-nodes-astron-rpa/execution/workflow.ts)与[执行状态观察](n8n-nodes-astron-rpa/execution/runner.ts)：使用 n8n 公开接口创建子执行、保存等待检查点；派发前保存固定请求和幂等键，响应丢失时有界恢复，取得执行 ID 后查询原执行。
- 实现批量顺序等待、输入项关联和错误路由；前项状态未确认时阻止后项派发。区分网络请求超时、调用方等待预算与 RPA 执行期限。
- 新增服务端[声明与准入策略](../../backend/openapi-service/app/services/integration_policy.py)，由管理员维护声明并绑定工作流版本、输入 Schema 和完整声明摘要。在纳入管理的范围内，固定 MCP、动态 MCP 与 REST 共用准入校验，拒绝未知、失效或不完整的声明。
- 修复[已受理执行的管理契约](../../backend/openapi-service/app/services/workflow_control.py)：普通重新发布后仍可查询、同键恢复和取消原执行，同时保留所有权、工作流开放状态及鉴权检查。
- 增加秘密输入对应的 `resultVisibility`，明确结果被抑制的原因；通过 JSON 错误封装保留 n8n 错误路由中的执行 ID，并为查询和取消增加 UUID 校验。
- 增加 json-data 能力类别，统一声明、准入、输入限制、输出 Schema 和 MCP 执行契约；文件传输、GUI 要求和运行时对象不属于本次数据能力。

## 验证环境

验证使用自托管单实例 n8n、单个持有客户端连接的 OpenAPI 实例，以及与仓库源码核对一致的 Windows 客户端。客户端支持范围为本次验证的配套版本，要求托管协议 1；能力不足时明确拒绝，不静默降级。工作流声明的 `supportScope` 为 `controlled-validation`。

| 组件 | 实测版本 |
| --- | --- |
| Community Node | `n8n-nodes-astron-rpa@0.1.0-dev.1`，tarball 安装 |
| n8n / n8n-workflow | `2.36.9` / `2.36.4` |
| Node.js / MCP TypeScript SDK | `24.18.0` / `1.30.0` |
| MCP 协议 | `2025-11-25` |
| OpenAPI 应用 | `1.0.0+public-framework.1` |
| OpenAPI 契约 / 声明 Schema / 客户端协议 | `1 / 1 / 1` |
| Server Python / FastAPI / Python MCP | `3.13.12` / `0.135.1` / `1.26.0` |
| Windows 桌面 | `1.1.8.0` |
| Client Python / Scheduler / Executor | `3.13.14` / `1.0.1` / `1.0.2` |

## 自动化检查

| 检查 | 结果 |
| --- | --- |
| OpenAPI 相关回归 | 203 项通过；4 个 SQLite datetime adapter 弃用警告 |
| 节点测试 | 21 项通过 |
| JSON 数据输入专项回归 | 已纳入节点测试；覆盖大小、深度、Unicode、对象键、循环引用、能力限制和 MCP 传输 |
| 节点构建、类型检查、ESLint、Prettier、npm pack | 通过 |
| 源码包与安装目录 npm audit | 均为 0 个漏洞 |
| 修改的 Python 文件格式检查 | 通过 |
| 修改涉及文件的 Ruff 检查 | 仍有 3 项既有问题，未新增 |
| 全仓 `make check` | 未通过，原因见文末 |

OpenAPI 回归覆盖声明与准入、执行管理、工作流 Schema、MCP 鉴权、外部接口安全、用户隔离及敏感信息日志。节点测试覆盖幂等恢复、等待预算、批量关联、错误中的执行身份、唤醒回调及 MCP 传输约束；[传输测试](n8n-nodes-astron-rpa/tests/transport.test.cjs)验证了跨源重定向拒绝、请求超时，以及未支持协议和空 Key 的前置拒绝。

Ruff 的 3 项问题为 `schemas/workflow.py` 的 `UP042`，以及 `services/execution.py` 中 `pageNo`、`pageSize` 的两项 `N803`；使用相同环境对照确认这些问题已存在。

## 实际联调结果

| 场景 | 结果 |
| --- | --- |
| 安装与发现 | 在全新 n8n 数据目录中从 tarball 安装，无源码链接；两次独立 CLI 执行均加载节点和凭据，并通过 MCP 读取授权工作流 |
| 鉴权与传输 | 有效 Key 成功，无效或吊销 Key 被拒绝；空工作流列表连接成功且未创建执行；未知 CA、错误主机名均被拒绝 |
| 客户端状态 | 离线时凭据测试仍能识别连接状态，执行返回 `CLIENT_OFFLINE`；忙碌时已受理回执最终为 `failed/CLIENT_BUSY`，未启动第二个运行进程 |
| 跨入口准入 | 未声明的受控工作流在固定 MCP、动态 MCP 和 REST 均被拒绝，未派发执行 |
| Async / Wait / Sync | Async 返回受理 ID；Wait／Sync 取得真实终态；成功结果中的数值 0 保持不变 |
| 幂等与响应丢失 | 顺序及并发同键请求返回同一执行；参数变化返回 `IDEMPOTENCY_CONFLICT`；受理响应丢失后恢复同一执行，客户端仅一条回执、一个 runId |
| n8n 重启恢复 | 取得执行 ID 前后均验证等待检查点恢复，执行身份和期限保持不变，无重复派发；批量重启保留已完成项和运行中项，再启动下一项，保留 `pairedItem` |
| 等待预算与执行期限 | 等待预算耗尽后保留运行中的执行 ID，未自动停止 RPA；显式取消后确认停止；RPA 执行期限到达后取得真实停止证据及 `timeout` 状态 |
| 批量失败与错误路由 | 成功／失败／成功批量保留输入项关联，错误 JSON 保留执行 ID；前项状态未确认时，后项返回 `PREVIOUS_EXECUTION_UNRESOLVED`，服务端无后项执行记录 |
| 取消竞态 | 重复取消、完成后取消均已验证；对旧执行再次取消不会停止正在运行的新执行 |
| 版本变化与设计器发布 | 运行中修改公开版本元数据后，原执行仍可查询、同键恢复和取消，新键启动旧版本被拒绝；设计器完整发布及 Java 到 OpenAPI 的同步已验证，新版本未经声明时返回 `PROFILE_UNKNOWN`，更新声明后执行成功。运行中完整 UI 发布的组合验证未完成 |
| OpenAPI 重启 | 短暂传输错误和 `unknown` 后恢复为同一成功执行，客户端仅一条回执、一个 runId |
| 客户端完整重启 | 运行中重启桌面进程树后，原执行保留 ID／runId，状态为 `unknown / CLIENT_RESTARTED`，不可取消且未自动重跑；新受控任务执行成功 |
| 秘密输入 | 合成秘密未出现在持久化参数、结果或错误中；结果为 null，`resultVisibility=suppressed-for-secret-inputs` |
| 重复与迟到唤醒 | 伪造回调结果未被接纳，最终结果仍由 MCP 查询，未产生第二次 RPA 执行；并发唤醒的宿主响应为 500／200，迟到唤醒为 409 |
| 失败恢复与原生重试 | 持久子执行返回业务失败后，n8n 原生 Retry On Fail 未重新执行业务；跨 n8n 执行使用同业务键返回原失败回执，显式新键才产生新执行 |
| JSON 数据型工作流 | 本地契约回归已通过；服务端与节点执行相同 JSON 限制，成功回执按冻结输出 Schema 校验 |
| 真实环境 MCP 与 JSON 执行 | 服务器 MySQL、Redis、OpenAPI、OpenResty 均健康；最新节点已安装到本机 n8n，MCP 鉴权与工具发现成功。客户端状态为 ready。普通 JSON 执行和 json-data 声明执行均完成 accepted → running → succeeded，结果保留 count=0、ratio=0，同一业务键重放返回同一执行记录；数据库保存冻结的 outputSchema、limits 和 profile revision。临时声明已回滚。 |

工作流停用、删除、跨用户及 Key 权限边界由授权与隔离自动化覆盖。真实联调使用受控工作流。

## 源码与安装产物核验

| 核验对象 | 结果 |
| --- | --- |
| 部署的 OpenAPI app | 44 个 Python 文件归一化换行后与仓库 SHA-256 一致 |
| 已安装 Scheduler / Executor | 64 / 31 个 Python 文件与仓库一致 |
| robot-service / rpa-auth 部署源码 | 918 个 Java 源文件一致；核验范围为源码 |
| 节点编译产物 | 14 个 `dist` 文件与 n8n 安装目录逐字节一致 |
| 节点分发包 | 17 个文件与 n8n 安装目录一致 |

验证包为 `n8n-nodes-astron-rpa-0.1.0-dev.1.tgz`，SHA-256：

```text
A25B5AAF6124C2D925022A58F22C25584563F3DC43168160EE8AF9B5061580E1
```

联调结束后，临时 n8n 工作流、明文凭据和临时服务端声明已删除或回滚；n8n 健康检查通过，客户端保持登录并处于 ready 状态，无遗留运行中或等待中的测试执行。

## 已确认的运行限制

- 自动幂等键按 n8n 执行隔离。跨执行恢复需显式提供稳定业务键，并保持原版本、输入、期限和声明 revision 一致；重新执行业务需使用新键。
- 本次重启验证覆盖持久等待检查点。任意活跃指令处崩溃及跨版本等待迁移不在已验证范围内。
- 唤醒定时器丢失后依靠 n8n 持久 `waitTill` 恢复，可能增加约 60 秒等待；回调内容不作为业务结果。
- 支持范围限于上述配套客户端、协议和单实例部署方式。

## 未完成的验证

| 项目 | 状态与原因 |
| --- | --- |
| 全仓 `make check` 通过 | 已使用 GNU Make 4.4.1 在相同依赖的对照快照和本次代码快照中运行，均以 exit 2 停在 `makefiles/typescript.mk:62 check-typescript`：`frontend/` 根目录缺少 `tsconfig.json`，`npx tsc --noEmit` 输出 TypeScript 5.9.3 帮助并失败。另有 `backend-go` 路径探测警告；停止点之后的聚合检查未执行 |
| 同一次任务运行中完成设计器 UI 发布 | 受控任务在实际发布前已结束，尝试延长任务时遇到窗口定位异常，未完成组合验证。运行中版本元数据变更、完整设计器发布及发布后原执行管理已分别验证，尚无同一次运行中的组合证据 |

## 浏览器读取与服务连接验收（2026-09-20）

本轮在已安装的 `n8n-nodes-astron-rpa@0.1.0-dev.2`、HTTPS OpenAPI 服务及 Windows 客户端之间完成真实联调，再完成本地定向回归。能力模块与 JSON 数据能力平级，复用公共执行框架；MCP 为主通道，REST 由调用方显式选择。本轮不改写上面的历史测试结果。

### 操作覆盖

按当前全部 25 个组件的操作行为核对分类，本类准入清单为 5 个组件、29 个操作，均有真实执行覆盖。完整操作名见 [分类清单](n8n-nodes-astron-rpa/capabilities/shared/catalog.ts)及机器可读证据。

| 组件 | 操作数 | 本轮验证 |
| --- | --- | --- |
| browser | 18 | 当前上下文、URL/title/tab、加载等待、元素生成与等待、存在性、文本、属性读取、选择项、选中态、相似元素及遍历、关联元素、表格、单页抓取、Cookie |
| database | 3 | SQLite 只读连接、固定 SQL 查询、断开；连接对象留在工作流内部 |
| network | 6 | HTTP GET/HEAD；FTP 建连、目录列表、当前目录、切换会话目录、关闭；无文件传输 |
| email | 1 | 邮件查询；不保存附件、不标记已读 |
| enterprise | 1 | 共享变量读取 |

HTTP、数据库、FTP、邮件、共享变量均通过 MCP 和显式 REST 执行；浏览器通过 MCP 执行。HTTP 使用同一业务键跨通道重放时保留同一 executionId/runId。成功执行的 MCP 与 REST 查询快照逐项一致。

### 修复与契约检查

- 服务端校验管理员维护、绑定发布版本及声明 revision 的私有 `readOnlyReview`，再次检查受约束的直接输入绑定；公开 `readContractVersion=1`，不公开固定 SQL 或私有审核参数。动态 SQL、多语句、写入开关、附件落盘、多页抓取及导出不在本类准入范围。
- REST 使用服务端权威能力声明、受理回执、查询及精准取消快照；保留安全业务错误码，未知执行结果不通过换通道重发解决。服务读取沿用严格 JSON、冻结输出 Schema 与结果限制。
- 原组件修复包括数据库查询调用、返回连接与游标释放、可选驱动延迟加载、数据库打包及元数据注册，HTTP HEAD 的 JSON 结果、FTP 超时及失败清理，邮件只读提取与连接释放，共享变量明文读取及浏览器读取时的窗口副作用。

### 测试结果与部署一致性

| 检查 | 本轮结果 |
| --- | --- |
| OpenAPI 定向回归 | 247 项通过；4 个既有 SQLite datetime adapter 弃用警告 |
| Community Node | 33 项通过；构建、类型检查、ESLint、Prettier、npm pack 通过 |
| Engine 定向回归 | 18 项通过；邮件 6 项使用独立进程运行 |
| 修改涉及的 Python 文件 | 26 个文件格式检查通过；与 HEAD 同环境比较，无新增 Ruff 诊断 |
| Engine 锁文件 | `uv lock --check --offline --project engine` 通过 |
| 网关 | Lua 六个路由/身份清除检查、部署环境 Nginx 配置检查通过 |
| 精准取消与期限 | REST 取消取得真实 `cancelled`；执行期限取得 `timeout`；重复取消旧执行未停止新执行 |
| 读取副作用与释放 | IMAP 使用 EXAMINE、BODY.PEEK、LOGOUT，未产生 STORE/Seen；FTP、IMAP 连接均归零 |
| 部署源码与产物 | 8 个 OpenAPI 修改文件、9 个客户端组件源码与本地一致；26 个节点 dist 文件逐字节一致 |
| 执行退出 | 本轮 29 条 RPA 执行回执均为终态，客户端残留测试执行进程为 0 |

浏览器独立读取执行 `78038fcb-7acc-4ba4-8fcc-f29b70f965b2` 与补充读取执行 `025432a4-750b-4f58-bd61-c58b0d2e75c8` 均通过；最终安装包 REST 烟测执行 `a62da5d7-4319-4926-800b-2bc3d905ad70` 成功。其他成功记录及取消证据见 [validation-evidence.json](validation-evidence.json)。早期浏览器测试曾读取到另一活动页，未作为成功证据；保持受控测试页活动后重新验证通过。

### 清理与支持边界

11 个临时机器人已通过服务接口删除，临时共享变量和 OpenAPI 工作流数据已清理，原服务端声明已恢复；服务端部署文件写入及清理均限于授权的 source 目录。n8n 临时工作流及其 57 条执行记录、11 个测试虚拟环境缓存、导出的临时凭据与测试 TLS 私钥已删除。本轮启动的 n8n、HTTP/FTP/IMAP 模拟服务已停止，原有 n8n 凭据保留；停止前健康检查通过，客户端保持登录且 MCP 报告 ready。服务端和客户端终态回执保留用于审计。

- 只读审核适用于管理员核对过的可信已发布工作流，不能替代 Python 沙箱或通用 SQL 安全解析；远程数据库仍须使用实际只读账号，并对查询结果及资源使用设限。
- 浏览器实测依赖 Windows、已连接的浏览器插件、所需登录态和指定活动页；测试时独占终端。未实现后台固定 tabId 路由，不保证切换窗口或活动页后的目标保持不变。
- 数据库真实执行覆盖 SQLite；MySQL 驱动随默认组件安装，但未据此宣称所有数据库真实验证通过。PostgreSQL、SQL Server、Oracle、Access 等可选驱动及 Linux 未实测，DB2 明确未实现；本轮未重建完整客户端 EXE。
- 本轮未重跑全仓 `make check`，其历史阻塞见上文。本机无 Docker CLI，完整 Docker 网关 shell 测试未运行；上述 Lua 与部署环境检查已完成。历史“同次运行中设计器 UI 发布”组合验证仍单独保留，不计入本类完成结果。
