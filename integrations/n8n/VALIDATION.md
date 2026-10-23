# n8n MCP 公共框架验收记录

本文保留公共框架与各能力的历史验收记录。最新 LLM 兼容性回归与三端定向复验见下节（2026-10-23）；2026-10-22 的较广范围复验保留为历史记录。各轮结论仅适用于各自代码与覆盖范围，不能替代其他操作的现场验证。

## LLM 普通调用失败契约回归与三端定向复验（2026-10-23）

核对 main 与本分支后确认：`request_json` 将网络异常转换为 `RuntimeError`，而 `chat_normal`、`chat_prompt` 仍捕获 `RequestException`，导致普通流程原本返回 `None` 的请求失败变为向外抛错。此次修复引入继承 `RuntimeError` 的专用 `AIRequestError`，保持 `AI_REQUEST_FAILED` 脱敏文本；两个调用方在普通流程中返回 `None`，启用托管风险契约时继续抛出错误。其他 `RuntimeError` 不会被吞掉。HTTP 超时、响应大小限制、禁止重定向及连接释放保持原有约束。

新增 `test_llm.py` 通过真实 `llm` → `request_json` 调用链，仅替换底层网络响应，覆盖连接失败、连接/读取超时、HTTP 错误、非法 JSON、响应超限、两种聊天响应格式、prompt 返回值、请求参数和无关异常传播。新增用例修复前有 12 项普通调用失败，修复后全部通过；错误文本和日志不包含合成敏感内容。

| 检查 | 本轮本地结果 |
| --- | --- |
| Engine AI 组 | 42 项通过，包含 34 项新增调用方回归及 8 项既有 HTTP/Agent 回归 |
| Engine 风险组 | 10 项通过 |
| n8n | 联调后 52 项测试通过；构建、打包及安装文件一致性检查通过 |
| 静态检查 | 5 个 Python 文件 AST、格式检查通过；相对 HEAD 无新增 Ruff 诊断，`llm.py` 的 8 条既有诊断未作为全量 lint 通过 |
| CI 接入 | 新测试加入现有 AI 组，按 Engine 锁文件补充 `sseclient-py` 测试依赖；上述两组均通过 CI 脚本在本机隔离环境执行，未运行 GitHub 托管 CI |

### 实际执行与结果

同步客户端 `http.py`、`llm.py` 后启动现有客户端，核验 304 个客户端源码文件与本地一致。服务端 55 个源码文件和本机 n8n `2.40.7` 的 45 个安装文件已与当前分支一致，其中 38 个编译文件与本轮构建一致，无需变更服务端业务代码或替换节点包。MCP 使用既有 HTTPS 地址且保持 TLS 校验开启；服务器配置写入仅位于授权的 source 目录内。

使用两个临时已发布流程及仅监听本机回环地址的受控 HTTP 服务。普通路径经客户端 `/executor/run_sync` 执行，托管路径经真实 n8n 节点、MCP、服务端和客户端执行；托管批准绑定发布代码、具体输入和幂等键。工作流直接调用实际 `chat_normal` / `chat_prompt`，未替换 HTTP 请求函数，也未更改 HTTP helper 的超时配置。

| 场景 | 普通执行 | n8n/MCP 托管执行 |
| --- | --- | --- |
| 聊天原格式、聊天包装格式、prompt 成功响应 | 3 项返回预期内容 | 3 项为 `succeeded`，返回预期内容 |
| 两个调用方连接拒绝、HTTP 503、真实 35 秒读取超时 | 6 项返回 `None`，测试流程正常结束 | 6 项为 `failed`，节点映射 `EXECUTION_FAILED`，结果为 null |

共 18 个有效场景通过。服务端 9 条托管执行为 3 COMPLETED、6 FAILED，客户端、服务端和 n8n 的 executionId/runId 与终态一致；失败执行未持久化业务结果。14 次实际 HTTP 请求、18 条风险审计与场景对应；回执、审计和对外错误未包含合成服务错误文本，最终无残留执行器进程或 HTTP 连接。n8n 测试入口使用 `continueRegularOutput` 收集预期错误，不将该入口本身的成功状态视为 RPA 业务成功。

准备阶段的 8 次试运行不计入上述通过数量：1 次使用了错误的普通执行参数格式，另 7 次运行时夹具 HTTP 服务未持续运行。调整测试参数列表和服务启动方式后完整重跑，并校验响应内容、请求记录与终态；本轮联调未发现需要继续修改产品源码的问题。联调后 AI、风险组及 n8n 本地回归均再次通过。

临时机器人、服务端声明、两个 n8n 测试工作流和 18 条 n8n 测试执行记录已清理，服务端策略恢复与原配置等价，原有凭据及执行审计保留。客户端两个临时运行目录的自动删除被审批策略拒绝，已请求用户手动清理；其状态将在最终复核中确认。HTTP 夹具已停止，n8n 健康、客户端空闲、MCP 正常。

本轮验证了上述调用方的真实执行及跨服务错误传播；模型响应由受控 HTTP 服务提供，不代表真实模型推理验收。Windows 桌面/Office 操作、完整客户端发布包、远程数据库和其他未复验模块仍保留原有边界。结构化记录见 `validation-evidence.json` 的 `llmCompatibilityValidation`。

## 变基后修复与三端复验（2026-10-22）

本轮在 `feat/office-file-workflows` 的 `e7e07c9f` 与未提交工作区上，处理前次复核的原组件失败项，并将最新代码同步到现有 Windows 客户端、自部署服务和本机 n8n `2.40.7` / Node.js `24.18.0`。未暂存、提交或推送。MCP 为主通道，REST 仅显式使用，TLS 校验保持开启。

### 修复和回归

- 多索引删除改用解析后的整数索引，归一负索引、去重并逆序删除；非法索引在修改列表前拒绝。
- 字符串右侧补齐使用转换后的整数长度；字典已有键的 `null` 值不再被误判为缺失。
- Base64 文本模式忽略残留文件路径，仅图片模式读取指定文件，保持公开组件的模式语义。
- 旧共享变量用例迁到当前 Enterprise 接口，覆盖明文、缺失、空组、加密和混合组；修正旧参数、异常期望及通配导入遮蔽内建类型的问题。加密测试使用独立临时文件和实际结果断言。
- CI 定向入口增加 dataprocess、encrypt 两组及其锁定依赖；连同已有风险/AI 组，Engine 矩阵共 17 组。目录仍按平级能力组织，未扩张禁止操作的准入范围。

前次与 main 同样失败的 14 项已通过行为修复或迁移到现有接口处理；相关三组当前为 dataprocess 217、encrypt 4、enterprise 6 项通过。此处保留较早失败记录作为修复前证据，不再将其作为当前未通过项。

| 检查 | 当前结果 |
| --- | --- |
| OpenAPI 定向回归 | 373 项通过，4 个既有 SQLite adapter 警告 |
| Engine 17 组 | 369 项通过、1 项 Windows 不适用的 POSIX 归档成员名用例跳过，无失败 |
| n8n | 52 项通过；类型检查、ESLint、Prettier（接受检出换行符）、构建和打包通过 |
| Python | 99 个相关文件 AST/格式通过；相对 HEAD 无新增 Ruff 诊断，877 条继承诊断不作为全量 lint 通过 |
| CI 与依赖 | 两个集成工作流 actionlint、Engine/OpenAPI 锁文件检查通过；未运行 GitHub 托管 CI |
| 联调后本地回归 | dataprocess、encrypt、enterprise 共 227 项再次通过；产品源码未在联调后改变 |

### 当前现场覆盖

| 范围 | 实际结果 |
| --- | --- |
| JSON/数据 | 真实发布流程经 n8n/MCP 验证多索引删除、补齐、null 和 Base64 四项修复；声明需要人工交互后，服务端准入为 `JSON_DATA_UNSUPPORTED`，节点返回 `ADMISSION_DENIED`，未派发 |
| 服务读取 | HTTP GET、SQLite 文件只读连接/查询/断开成功；MCP 成功回执经显式 REST 同键重放保持身份和结果 |
| Office/文件 | n8n Binary 上传、MCP 执行和下载核验通过；ZIP/7z 解压、文本、Excel/WPS、Word/WPS、PDF、CSV 输出均校验实际内容与 SHA-256，路径穿越归档拒绝 |
| 桌面/UI | 经用户确认，在专用合成窗口验证定位、置顶/尺寸、鼠标、键盘、元素文本和受控区域截图；输入内容正确，截图 Binary 一致，窗口已关闭 |
| 风险组合 | 审核 Smart 代码、SQLite 内存写入和回环合成 Agent 成功；`Compress.compress` 公开名称在风险审核中正确匹配原元数据别名，输出归档内容核验通过 |
| 拒绝与结果 | 代码/参数摘要、未声明操作、次数、缺失/过期/变更/撤销批准均按预期拒绝；敏感结果为 null，超限及不符合冻结 Schema 的结果不持久化业务数据 |
| 生命周期 | 五个测试请求 MCP/REST 同键重放保持 executionId/runId；取消为 `cancelled`，执行期限为 `timeout`；再次取消旧执行不影响新的 REST 执行；撤销后携带原 revision 重放仍返回原回执 |
| Office 退出清理 | 实际 WPS Excel/Word 私有实例在模拟执行器异常退出后被清理，工作目录删除 |

29 条 RPA 执行全部终态：18 COMPLETED、9 FAILED、1 TIMEOUT、1 CANCELLED。9 个失败包含 7 个预期拒绝及 2 个夹具问题：回环 HTTP 服务初次未持续运行、将 SQLite `:memory:` 当作只读文件；修正为持续运行的本轮夹具和实际只读数据库文件后均成功。另一次 JSON 拒绝测试遇到连接不确定，恢复连接后原测试请求完成拒绝验证。保留失败证据，不将初次失败或合成 Agent 表述为成功验收。

服务端和客户端 29 条执行身份均一致；结果被服务端契约拒绝时保留客户端执行成功、服务端 FAILED 的区别。39 条风险审计事件未含合成凭据或业务文本，无残留执行进程。55 个服务端 Python 文件、304 个客户端 Python 文件、45 个 n8n 安装文件与本地一致，其中 38 个编译文件与构建一致；包 SHA-256 为 `bfa5c555e639288f25163dd2fd4886db37c3cac9822157e5fa3fd5c53471a2c6`。

### 清理与验收边界

26 个临时机器人及服务端声明、17 个文件句柄、5 个 n8n 工作流及 105 条测试执行记录已清理，服务端策略恢复与原配置等价，原有 n8n 数据和凭据保留。客户端测试运行目录及 n8n 下载/上传缓存按精确测试 ID 清理，执行审计保留；回环服务和桌面夹具已停止。服务器源码备份和测试包已清理，所有服务器文件写入均位于授权的 source 范围。最终 n8n 健康、客户端空闲、MCP 正常。

用户要求的 `stash@{0}` 已在核验恢复完整后删除，stash 列表为空；工作区修改保留，仓库内没有新增临时测试目录。

**本轮已关闭可复现代码缺陷和上述定向验收，但不宣称全部操作均已现场验证。** 真实模型无可用配置，外部 Agent/商业服务、远程数据库、完整 EXE 重建、全部浏览器和 GUI 操作组合仍未验证；本轮 Office 宿主为 WPS，不替代 Microsoft Office 验收。浏览器/FTP/邮件/共享变量此次完成自动化回归，未重新进行全部真实服务操作。此前全仓 `make check` 超时，未作为通过；禁止的 CUA、验证码、解锁、动态表单等继续拒绝。结构化记录见 `validation-evidence.json` 的 `stage4ClosureValidation`。

## 合并后变基与全类别本地复核（2026-10-22）

PR #879 已合并。当前分支变基到 `origin/main` 的 `65e97b93`，两个后续提交重放为 `bcc7d06b`、`e7e07c9f`，`git range-diff` 确认补丁等价；无冲突。变基前 43 个未提交文件已用包含未跟踪文件的 stash 保存，恢复后逐字节核验一致。当时保留的快照已在后续修复轮次按用户要求删除，工作区修改保留。下述为变基复核时的历史结果，当前修复状态见上节；未新增业务提交或推送。

### 实现与覆盖结论

公共框架及五个平级能力模块均已落地，共用传输、准入、执行身份、等待恢复和结果映射。当前分类清单覆盖实际 26 个组件目录；服务读取 29 项、Office/文件 111 项、桌面/UI 73 项、风险分类 46 项与服务端清单一致，均能对应源码方法或既有元数据别名。风险分类的 46 项包含 11 项明确禁止的操作，不能作为 46 项开放支持或实测完成的数量。

**当前不能判定全部功能与覆盖已经完成。** 定向集成回归通过，但补充原组件回归仍有与最新 main 一致的失败；完整宿主、真实模型及逐项运行验收也有未关闭范围。

| 范围 | 本轮核对与回归 | 未关闭范围 |
| --- | --- | --- |
| 公共框架 | 凭据与 HTTPS、发现与 Schema、统一异步执行、幂等/恢复、等待/取消、错误和 item 映射均有现有实现及定向回归 | 本轮没有重启真实 n8n/客户端，也未重验设计器发布组合或完整 EXE |
| JSON/数据 | Schema、限额、冻结结果、数据映射回归通过；补齐低风险、无人交互和无声明副作用的准入校验 | 补充 dataprocess 218 项中 205 通过、13 失败；encrypt 3 项中 2 通过、1 失败，详见下文 |
| 浏览器/服务读取 | 29 项清单和只读审核、传输边界核对；OpenAPI service-read 34 项、Engine 五组共 46 项通过 | 自动化准入覆盖不等于 29 项当前现场复验；远程数据库及浏览器宿主组合仍需实际环境验证 |
| Office/文件 | 句柄授权、Binary 映射、限额/生命周期、私有 Office 与归档约束核对；OpenAPI 33 项，Engine files/scheduler、excel、word、system、datatable 共 63 项通过、1 项平台跳过 | 全部 111 项、Microsoft Office、商业文档服务、共享存储等未逐项实测；使用剪贴板或附着用户文档的 Excel 操作仍不开放 |
| 桌面/UI | 会话/分辨率/程序检查、独占、人工交互、取消/恢复核对；OpenAPI 25 项，Engine desktop、vision、dialog 共 17 项通过 | 73 项非全部实测；锁屏、会话切换、多屏、全部表单/手势仍有历史记录列出的边界；自定义表单和本地文件选择不开放 |
| AI/动态代码与风险 | 批准绑定、允许列表、参数/源码摘要、审计、秘密输出及组合契约核对；OpenAPI 27 项，Engine risk/ai 共 18 项通过 | 没有可用模型配置，真实模型成功推理未验证；外部 Agent、不可逆操作及全部组合未实测，禁止项继续拒绝 |

类别专项数量仅说明相关测试文件的范围；公共测试由多类复用，不能将各行与总数直接相加。

### 本轮修复

- JSON 数据声明此前仅阻止文件和 GUI，仍可能接受 `requiresHuman=true`、较高风险或声明副作用。服务端和节点现要求无文件、无 GUI、无人工交互、`risk=low` 及空副作用清单；补充拒绝用例，并在用户 README 中说明适用类别。
- 风险组合流程中，压缩、剪贴板、键鼠等方法的公开名称可能不同于元数据分组键。风险校验现在接受同一方法已批准的公开名称，同时保留 FTP/进程等既有元数据键；参数校验失败后不尝试另一个别名。普通非托管调用不受影响。新增别名接受、原键兼容和禁止绕过参数约束的回归。
- 补充节点与服务端风险操作清单一致性及禁止操作拒绝的自动化检查。两处行为缺陷均先由失败用例复现，再修复复测。

### 最终检查

| 检查 | 结果 |
| --- | --- |
| OpenAPI 定向回归 | 373 项通过，4 个既有 SQLite datetime adapter 警告 |
| Engine 15 组定向回归 | 144 项通过、1 项跳过，无失败；跳过项是 Windows 不适用的 POSIX 归档成员名用例 |
| n8n | 52 项通过；TypeScript、ESLint、Prettier、构建通过 |
| 打包 | npm pack 通过，45 个包内文件仅含发布范围；编译文件与本地构建一致，未安装到运行中的宿主 |
| Python 静态检查 | 公共框架和能力交付涉及的 88 个 Python 文件 AST、格式通过；相对变基后 HEAD 无新增 Ruff 诊断，保留 580 条既有诊断，不记为全量 lint 通过 |
| 配置与依赖 | 两个集成 CI 工作流 actionlint、Engine/OpenAPI 锁文件检查通过；未运行 GitHub 托管 CI |
| 全仓检查 | `mingw32-make check` 在 45 秒内未完成，已停止本轮检查进程树，不记为通过 |

额外运行原 dataprocess/encrypt 测试时，使用锁定的 numpy/pycryptodomex 等依赖，并对最新 `main` 的相同组件与公共依赖在隔离目录复跑。两边均为 **207 项通过、14 项失败**，失败用例名称一致，包括仍调用已迁移共享变量接口、旧参数/返回期望、列表/字符串/时间用例，以及缺少 `a.txt` 的加密夹具。它们不是本次变基新增的回归，但仍是完整覆盖的未通过项；本轮未顺带修改这些原组件和旧测试。

本轮限本地静态与自动化回归，没有同步或操作部署中的服务器、客户端及 n8n。新增修复尚未进行真实环境复验；较早联调的一致性校验不能替代当前工作区的部署验收。临时脚本、报告、基线源码及打包产物均放在仓库外；结构化结果见 `validation-evidence.json` 的 `stage4RebaseAudit`。

## AI、动态代码与高风险契约验证（2026-10-22）

本轮基于 `feat/office-file-workflows` 的 `fa084504` 与未提交修改，使用现有 Windows 客户端同步源码、本机 n8n `2.40.7` / Node.js `24.18.0` 及现有 HTTPS 服务。MCP 为主通道，REST 仅用于声明允许的显式执行和既有文件传输，TLS 校验保持开启。Office/文件及桌面/UI 已有实现和历史受控验收，本轮回归其公共边界，未重新操作全部 Office 或 GUI 场景。

### 实现与授权边界

- `ai-dynamic-risk.ts` 与其他类别平级，通过公共注册器分发；组合文件/桌面场景复用中性的共享契约，保留各原类别的准入限制。
- 管理员私有 `riskReview` 预批准具体请求，绑定用户、发布版本、输入 Schema、声明 revision、实际输入、幂等键和执行期限。公开画像不包含批准记录、审核参数或代码。
- 客户端声明 `riskProtocolVersion: 1`，检查操作允许列表、风险等级、参数摘要、调用次数及动态源码摘要；直接原子调用同样检查。源码通过校验后执行已核验字节，避免复用不同源码的模块/字节码缓存。普通非托管运行保留原行为。
- 动态输入输出沿用 JSON 限制和冻结输出 Schema。敏感输入的结果抑制为 `null`，输出 Schema 须允许该值；敏感输入与文件输出的组合仍拒绝。
- 私有审计只记录批准标识、操作、摘要、计数和接受/拒绝事件。风险诊断日志隐藏业务值，正常结果经私有终态回执返回。缺失有效回执时不把脱敏日志推断成成功。
- 此契约适用于可信、经管理员审核的发布代码，不是任意 Python 或操作系统沙箱。模型驱动 CUA、验证码、解锁、依赖设计器的多轮/知识对话等路径明确拒绝；不因归入该类别自动开放。

### 本地回归与静态检查

| 检查 | 结果 |
| --- | --- |
| OpenAPI | 369 项通过；4 个既有 SQLite datetime adapter 弃用警告 |
| Engine 15 组 | 141 项通过，1 项明确跳过：Windows 不适用的 POSIX 归档文件名用例；无失败 |
| 联调后 Engine 定向复测 | risk 7、ai 8、files/scheduler 39，共 54 项通过；其他 12 组本轮此前已通过，源码未再修改 |
| n8n | 50 项通过；TypeScript 类型检查、ESLint、构建、Prettier（接受检出换行符）、打包安装通过 |
| Python | 本次 29 个文件 AST/格式检查通过；与 HEAD 同环境比较，无新增 Ruff 诊断，既有诊断未作为全量通过 |
| CI 配置 | 定向入口增加风险和 AI 组及 OpenAPI 测试；两个相关工作流通过 actionlint，未运行 GitHub 托管 CI |

联调修复了两处执行链问题：风险日志脱敏后调度器仍取日志结果，现改用校验运行身份和进程退出证据后的私有回执；准备阶段失败、未绑定运行 ID 且准备线程已退出时，依据“绑定先于启动”的持久记录收敛为失败。已绑定但启动未确认的情况继续保留 `unknown`，不重新派发。两项均有定向回归及部署后复测。

### 真实环境结果

| 场景 | 结果 |
| --- | --- |
| 审核代码 | Smart 发布代码通过 MCP 返回预期 JSON；代码摘要、参数摘要不匹配分别返回 `RISK_CODE_DENIED`、`RISK_ARGUMENTS_DENIED` |
| 操作与次数 | 未声明的嵌套数据库调用及超过调用次数均返回 `RISK_OPERATION_DENIED` |
| 数据库写入 | 仅使用 SQLite 内存库，建表、插入、查询及关闭通过；MCP 与新请求的显式 REST 执行均成功 |
| Agent | 真实 `Agent.call_dify` 调用回环合成服务成功；该项验证调用链与资源释放，不代表外部 Dify 或真实模型推理成功 |
| 批准边界 | 未批准、过期、改变输入或期限、撤销后的新请求均在派发前拒绝；无对应 RPA 执行 |
| 幂等与撤销 | n8n 的同键跨通道重放保持相同 executionId/runId；撤销后通过已安装传输模块携带原 revision 重放，MCP/REST 均返回原成功回执 |
| JSON 与敏感输入 | 不符合冻结 Schema、超出 JSON 限制的结果被服务端拒绝且不持久化业务结果；可空 Schema 下敏感输入执行成功、结果为 null |
| 文件组合 | 审核代码仅写受管工作目录，n8n 下载为 Binary；25 字节内容与 SHA-256 一致，不公开客户端路径 |
| 生命周期 | 取消取得 `cancelled`，期限取得 `timeout`；重复取消旧执行不影响新的 REST 执行；准备超时的无进程记录已收敛为失败 |

共 19 条 RPA 记录全部终态：6 COMPLETED、11 FAILED、1 CANCELLED、1 TIMEOUT，无残留执行进程。失败数包含预期拒绝、初次回传缺陷、夹具 Schema/合成服务准备问题及真实模型配置缺失，不等同于 19 个独立成功场景。客户端与服务端运行 ID 均一致；客户端组件执行成功但结果被服务端契约拒绝的记录，保留两端各自状态及拒绝原因。42 条风险审计事件未包含合成凭据或业务文本。

55 个 OpenAPI 源码文件、228 个相关客户端 Python 源码与本地一致；安装包 45 个文件与最终 tarball 一致，其中 38 个编译文件与本地构建逐字节一致。tarball SHA-256 为 `b713aa9da10336a0c9a1c4d5e404e16f0f778159f5949a009f4deceb760759ed`。

### 清理与未完成边界

13 个临时机器人及其工作流/私有声明、1 个输出文件句柄、4 个 n8n 临时工作流及 74 条执行记录已清理，原服务端策略恢复一致。服务器测试包和备份已清理，所有服务器写入均限制在授权的 source 目录。n8n 保持健康运行，客户端空闲、MCP 连接正常；服务端/客户端审计及原有凭据保留。

本轮缓存删除曾被自动审批拒绝。用户手动清理后，只读核验确认 13 个客户端运行目录及 n8n 的 `storage/workflows/risk20261022downloadFile` 下载缓存目录均已删除，`.executions` 审计仍保留，本轮临时运行缓存清理完成。

现有服务端未设置可用的 `AICHAT_BASE_URL` / `AICHAT_API_KEY`，真实推理接口返回 HTTP 500；用户已确认没有可用模型配置，因此真实模型成功推理保留为未验证项。未测试真实不可逆动作、全部 AI/动态操作、远程数据库、外部 Agent 产品、完整客户端 EXE 重建或全部 GUI 组合；未将受控 SQLite 写入和合成 Agent 结果扩大为这些场景的验收。全仓 `make check` 仍受此前 frontend 枚举问题限制，不能记为通过。

结构化记录见 [validation-evidence.json](validation-evidence.json) 的 `aiDynamicRiskValidation`。本轮未暂存、提交或推送。

## 浏览器与服务读取变基核验（2026-10-20）

`browser-service` 从 `4e26f079` 变基到 main `59b576ed4fd22bf44bbe81ff1265cd2a75f9cb08`，保留本分支原有五个提交的工作范围。采用 main 的本地化元数据生成流程，未恢复已删除的 `engine/meta_json.py` 和已取消跟踪的浏览器 `meta.json`；`activate_window` 的中英文表单说明迁入 `locale`，默认激活兼容行为保持不变。Engine 锁文件保留 main 的依赖版本并合入数据库依赖，`uv lock --check --project engine` 通过。

main 新增 `astronverse-control` 后，当前组件目录为 **26 个**。分类清单已补齐控制流组件，其嵌套操作仍须按实际能力审核；本次读取准入仍为 **5 个组件、29 项操作**，未新增读取权限。浏览器元数据回归扩展为中英文两种生成结果，验证开关标题、提示及默认值。

| 检查 | 本轮本地结果 |
| --- | --- |
| OpenAPI 定向回归 | 284 项通过；4 个既有 SQLite datetime adapter 警告 |
| Engine 五组 | browser 6、database 12、email 22、network 4、enterprise 2，合计 46 项通过；相对历史 45 项增加 1 个本地化元数据用例 |
| n8n | 36 项通过；安装、类型检查、ESLint、Prettier（`--end-of-line auto`）及构建通过 |
| 静态检查 | 两个 CI 工作流通过 actionlint；回归入口和修改的浏览器测试通过 Ruff 检查及格式检查（Engine 配置）；`git diff --check` 通过 |

本轮使用仓库 CI 同一定向入口、Windows / Python 3.13.14 / Node.js 24.18.0，测试无失败或跳过，报告与临时环境放在仓库外。未同步或操作实际客户端、服务器和 n8n 宿主，未运行真实 GUI 或远程数据库。全仓 `mingw32-make check` 在递归枚举 frontend 文件阶段长时间未完成，已停止，不能记为通过。旧提交 `4e26f079` 的 GitHub CI 已真实通过 OpenAPI 284 项、Engine 45 项、n8n 36 项，见 2026-10-13 的 [PR 复审记录](https://github.com/iflytek/astron-rpa/pull/879#issuecomment-6143263871)；该结果不替代变基后提交的 CI。

### 历史现场证据与合并前责任

- **2026-09-20：**历史记录包含 29 项操作的执行覆盖，限当时的受控 Windows 环境和代码；不是当前分支全部 29 项的现场复验。
- **2026-10-10：**历史变基联调覆盖 19 个不同操作（Browser 8、Database 3、Network 6、Email 1、Enterprise 1），使用现有 Windows 客户端同步源码、n8n 2.40.7 / Node.js 24.18.0 和自部署 HTTPS 服务，未重建完整 EXE。MCP/显式 REST、幂等、取消、期限及资源释放的证据按该日期保留。
- **当前合并前检查责任人：PR 作者 `bbdu3`。状态：待完成。**由其在拟合并提交上核对当前 Windows 客户端/插件、服务端和 n8n 宿主的版本与安装文件一致性；验证浏览器默认激活与显式只读、受控活动页读取、HTTP/SQLite/FTP/邮件/共享变量读取，以及幂等、取消、超时和资源释放。执行后补录日期、提交号、实际覆盖操作和执行回执，再交由维护者复审；不将这份责任清单表述为已验收。

完整 EXE 打包、远程数据库、其他 Engine 组及全部 29 项操作的当前独立现场复验仍未完成；若合并验收范围不包含其中某项，由 `bbdu3` 在上述检查记录中明确保留边界并由维护者确认，不能用历史联调或定向测试替代。当前结论限于管理员审核并绑定版本的受控读取契约及已列出的自动化回归，不代表整个多模块 PR 获得无条件批准。

本轮结构化记录见 [validation-evidence.json](validation-evidence.json) 的 `browserServiceConflictReview`，此前记录保持原日期和适用范围。

## 桌面与 UI 能力验证（2026-10-14）

本轮基于 `feat/office-file-workflows` 的 `225914d15d328ec6193bbc790b52b4d00c2cc38e` 与未提交修改。使用现有 Windows 客户端、物理主屏 `1920×1200`、本机 n8n `2.40.7` / Node.js `24.18.0`、tarball 安装的 `n8n-nodes-astron-rpa@0.1.0-dev.2` 和现有 HTTPS OpenAPI 服务，TLS 校验保持开启。测试使用合成窗口和经管理员审核的已发布工作流。

### 实现范围与准入边界

`capabilities/desktop-ui.ts` 与 JSON 数据、浏览器/服务连接、Office/文件模块平级；文件契约校验移至 `shared/file-contract.ts`，不同类别互不继承。继续复用公共执行、幂等、等待、查询、取消和结果映射。MCP 为默认执行通道，REST 仅用于声明允许的显式辅助执行及既有文件传输，不因结果未知跨通道重发。

公开 `desktopContract` 声明分辨率、软件标识及人工交互模式；私有 `desktopReview` 保存审核过的操作、软件绝对路径、目标窗口及允许的弹窗标题，并绑定发布版本、输入 Schema 和声明 revision。受理时冻结契约，沿用已有 `data_contract`，无新增数据库迁移。涉及截图、上传或下载时仍须完整的文件契约与审核，不因具备桌面权限而放开文件权限。

准入清单为 browser 39、dialog 4、input 8、software 1、system 6、vision 5、window 4、winelement 6，合计 **8 个组件、73 项操作**。该数量表示代码允许审核接入的范围，**不是 73 项均已独立现场复验**。模型驱动 CUA、任意脚本/命令、验证码处理、终止进程、锁屏/解锁、打印、动态自定义表单和任意本地文件选择不开放。核对原组件后，`Software.close` 和 `BrowserSoftware.browser_close` 因会结束同名程序的全部进程而未纳入；保留经审核的定向窗口/标签页关闭。

客户端在启动前及执行期间检查 Windows 交互会话、输入桌面、物理主屏分辨率、审核软件和目标窗口的非预期所属弹窗；终端忙碌明确拒绝，无隐式排队。停止未确认时保留不确定状态。这里面向管理员审核过的确定性工作流，**不构成任意 Python/GUI 沙箱，也不承诺前台焦点拦截或后台固定标签页路由**；运行时仍需预留交互会话。

### 最终本地回归与静态检查

| 检查 | 结果与范围 |
| --- | --- |
| OpenAPI | 342 项通过，无失败或跳过；覆盖桌面契约/私有审核、版本绑定、混合文件权限及原执行框架；4 个既有 SQLite datetime adapter 警告 |
| Engine | files/scheduler 33、desktop 9、vision 2、dialog 6，合计 50 项通过，无失败或跳过；覆盖会话检查、弹窗判断、独占/恢复/清理、桌面中断后禁止上传文件、托管图像与原生表单分发；其他 Engine 组未在本轮重跑 |
| n8n | 48 项通过；构建、类型检查、ESLint、Prettier（`--end-of-line auto`）通过，节点已打包安装 |
| Python 静态检查 | 后端 8 个、Engine 11 个变更文件格式通过；与 HEAD 在同环境比较，无新增 Ruff 诊断，既有诊断分别从 6 降至 2、70 降至 48 |
| CI | 回归入口增加 OpenAPI 桌面测试及 Engine desktop、vision、dialog 组；主 CI 与定向工作流通过 actionlint；GitHub 托管 CI 尚未运行 |
| 收尾检查 | 验证证据 JSON 可解析且统计一致，历史记录未改写；`git diff --check` 通过，暂存区为空 |

Python 回归使用 [定向入口](../../.github/scripts/run-integration-regression.py) 的隔离环境，报告放在仓库外；Engine 本轮使用 `--component files|desktop|vision|dialog` 分组执行。上述结果来自最后一次源码修复后的本地回归，不把旧能力的历史测试数量累加到本轮。

### 真实环境验证

| 场景 | 实测结果 |
| --- | --- |
| 窗口、键鼠与元素 | 合成窗口置顶/调整大小、键鼠输入 `desktop-verified`、WinEle 读取 `Verified 1` 及定向关闭通过 |
| 截图与文件输出 | 仅截取合成窗口，经授权输出句柄下载为 n8n Binary；PNG 为 880×550、16,974 字节，SHA-256 一致并目视核对 |
| 固定图像匹配 | 合成窗口中的固定图像匹配返回 `true`；托管路径不再保存额外全屏调试图 |
| 原生人工表单 | 消息框返回 `confirm`，文本输入返回 `native-input-verified`，单选返回夹具选项字面值 `"beta"`（含引号），单日期返回 `2026-10-14`；未回答的选择框在期限到达后退出 |
| MCP / 显式 REST | 两条声明允许的执行路径均成功；同业务键跨通道重放返回相同 executionId/runId |
| 独占、取消与期限 | 忙碌返回 `CLIENT_BUSY` 且未启动第二个执行；精准取消及重复取消旧执行通过，未影响新执行；执行期限返回 timeout 并有停止证据 |
| 弹窗与启动检查 | 真实非预期所属弹窗触发 `DESKTOP_POPUP_BLOCKED`；分辨率不匹配、审核软件缺失均在启动前拒绝，`runId=null` |
| 客户端通道重连 | 运行中重启 OpenAPI，客户端实际重连；原执行以相同 executionId/runId 完成，没有重新派发 |
| n8n 重启恢复 | 在持久等待检查点重启 n8n；停机期间原 60 秒等待预算耗尽，恢复返回 `WAIT_BUDGET_EXPIRED` 并保留原执行身份及最后快照；随后显式查询原 ID 得到 succeeded。未将父等待流程记为成功完成 |
| 可导入示例 | `examples/desktop-ui.json` 导入真实 n8n 后成功执行 |
| 最后源码同步检查 | 最后一次客户端重启后，旧成功执行可原样重放，新 Window.exist 执行成功（测试窗口不存在，预期返回 false），分辨率及软件缺失拒绝再次通过 |

联调修复了 DPI 虚拟分辨率误判、弹窗 API 调用不兼容、托管弹窗依赖设计器 WebSocket 而无法交互、桌面执行等待日志浮层连接及额外全屏调试图问题；对应场景修复后已复测。恢复和清理期间保持终端独占，避免并发恢复覆盖回执。最后一项恢复修订确保已记录桌面中断时不因迟到的成功回执上传文件；该竞态经自动化回归验证，随后完成源码同步、客户端重启及上述最终检查，未再次重放全部 GUI 手势。

### 一致性、清理与未测边界

7 个 OpenAPI 源码文件、7 个已安装客户端源码文件、41 个已安装节点包文件与本地逐项一致；节点 tarball SHA-256 为 `c1c6904c5cf673a1e4ae7db14b9d7bedbb2983da7a52cac78d463fe32e5125e1`。服务器写入和清理均限制在指定源码部署目录。

服务端与客户端 **35 条执行回执一致且全部终态**：19 COMPLETED、11 FAILED、3 CANCELLED、2 TIMEOUT，无剩余测试执行进程。该统计包含预期拒绝、早期夹具错误及未执行到目标动作的空分支，不能将 19 条 COMPLETED 全部视为独立 GUI 验收；功能证据以上表实际效果为准。

23 个临时机器人及对应工作流/声明、1 个输出文件句柄、7 个 n8n 临时工作流、100 条 n8n 执行记录、服务器测试包与临时目录均已清理，原声明策略恢复。14 个客户端临时运行目录经用户手动清理并只读核验不存在。合成窗口、表单及回环测试服务已退出；服务端/客户端审计、非测试数据与原凭据保留，先前按用户要求保留的 Office 临时凭据副本未改动。客户端空闲、n8n 健康且保持运行。

本轮未实际锁屏或切换 Windows 会话，相关异常路径仅有模拟回归；未独立实测密码、多选、日期范围表单、全部浏览器桌面手势、软件启动及多屏适配，也未逐项现场复验全部 73 个操作。未重建完整客户端 EXE、未重跑全仓 `make check`、未运行 GitHub 托管 CI。当前结论限于上述受控环境与场景。脱敏执行标识、结果摘要和清理证据见 [validation-evidence.json](validation-evidence.json) 的 `desktopUiValidation`。本轮代码未暂存、提交或推送。

## Office 与文件能力验证（2026-10-13）

本轮基于 `feat/office-file-workflows` 的 `4e26f079` 与未提交修改。使用本机 n8n `2.40.7`、Node.js `24.18.0`、tarball 安装的 `n8n-nodes-astron-rpa@0.1.0-dev.2`、现有 HTTPS OpenAPI 服务和同步源码后的 Windows 客户端。TLS 验证通过，证书有效期至 2026-12-13。Office 实测使用 WPS Office 2023 专业版的 `Ket.Application`、`Kwps.Application`。

`capabilities/office-file.ts` 与 JSON 数据、浏览器/服务连接模块平级，复用既有执行、幂等、等待恢复和取消逻辑。MCP 负责工作流控制；REST 负责二进制传输及声明允许的显式辅助执行，不在 MCP 结果未知时切换通道重发。

文件使用授权句柄和执行绑定的临时传输授权，在客户端私有工作目录中处理；限制为单文件 10 MiB、输入输出合计 8 个、保留 24 小时，每个所有者最多 100 MiB / 64 条文件记录。节点使用 n8n Binary Data，不向调用方暴露客户端路径。公共契约沿用已有 `data_contract` 列，无新增数据库迁移。

准入清单覆盖 10 个组件的 111 项操作：Excel 32、Word 19、PDF 8、system 23、datatable 2、browser 12、network 6、enterprise 2、openapi 6、email 1。操作已与 Engine 源码和节点清单核对；**111 是准入清单数量，不是独立实测通过数**。工作流仍须经过管理员审核并绑定发布版本；文件目录约束和操作声明不构成任意 Python 代码沙箱。

### 本地回归与静态检查

| 检查 | 结果与范围 |
| --- | --- |
| OpenAPI | 317 项通过，无失败或跳过；覆盖文件授权、配额与生命周期、画像/文件契约、结果校验及原执行框架回归；4 个既有 SQLite datetime adapter 警告 |
| Engine | files 27、excel 6、word 4、system 12、datatable 2、email 22，合计 73 项通过，无失败或跳过；自动化 Office 测试使用模拟 COM，真实 WPS 验证另列如下 |
| n8n | 44 项通过；构建、类型检查、ESLint、Prettier（`--end-of-line auto`）通过；覆盖文件操作、Binary 映射、操作清单一致性和既有执行/传输契约 |
| Python 静态检查 | 变更的后端 11 个、Engine 15 个文件格式通过；相对 HEAD 无新增 Ruff 问题，既有诊断分别从 7 降至 3、398 降至 383；回归入口 Ruff 和格式检查通过 |
| CI | 两个工作流通过 actionlint；定向入口增加文件执行、Excel、Word、system、datatable 组，主 CI 增加 scheduler/executor 路径触发；GitHub 托管运行尚未执行 |

使用 `.github/scripts/run-integration-regression.py` 的临时环境和仓库外报告执行 Python 回归。Engine 新增组可用 `--component files|excel|word|system|datatable` 分别运行；原有组保留，本轮另重跑了 email，其他组的历史结果不计入本轮 73 项。

合并前 review follow-up 仅进行本地静态与定向回归：普通（非托管）压缩解压保留 POSIX 文件名和大小写区分，托管 ZIP 增加实际写入量限制；恢复路径的文件上传和 Office 清理移出状态锁，并增加并发读取回归。相关 system 压缩测试为 12 项通过、1 项因 Windows 符号链接权限跳过，scheduler 文件/恢复测试为 28 项通过；OpenAPI 文件测试 33 项、n8n 测试 44 项通过。此 follow-up 未进行服务器、客户端或 n8n 真实联调。

### 真实环境验证

| 场景 | 实测结果 |
| --- | --- |
| 文件主链路 | n8n 上传 → MCP 执行 → 现有 Windows 客户端 → 输出上传 → n8n Binary 下载通过；覆盖中文文本，以及包含 `0,false,null` 的文本内容 |
| Excel / Word | WPS Excel 读取 B1=42，修改并下载后 B1=43；WPS Word 读取正文、保存和关闭通过；输出内容已核对 |
| PDF / DataTable | PDF 页数和文本提取通过；CSV 导入导出通过，实际下载内容为 CSV 文本，值保持一致 |
| 浏览器文件输出 | 在连接 AstronRPA 插件的 Edge 中先核对合成测试页 URL，再截图并下载；图像已目视核对 |
| 压缩包 / 网络文件 | ZIP、7z 解压后的文件字节与输入样本一致；HTTP 下载本机回环小文件通过；穿越 ZIP 被拒绝 |
| 大小与输出边界 | 空文件往返、精确 10 MiB 上传通过；10 MiB + 1 字节输入被节点拒绝；超限输出和缺失输出返回 `FILE_OUTPUT_INVALID`；删除后的句柄被拒绝 |
| 授权与幂等 | 活跃输入删除返回 `FILE_IN_USE`；MCP/REST 同键重放保持 executionId/runId；同键修改输入被拒绝；成功输出作为新输入经显式 REST 执行通过 |
| 超时 / 取消 | 2 秒执行期限触发 timeout，确认执行进程退出；精准取消和重复取消通过 |
| n8n 重启恢复 | 真实等待期间重启 n8n，恢复同一 executionId/runId；取得预期的缺失输出失败终态，没有重新派发 |
| Office 异常退出 | 两个 WPS provider 分别模拟执行器突然退出，按私有实例 PID 与创建时间清理，工作目录移除通过 |
| 可导入示例 | 包内 `examples/office-file.json` 实际导入 n8n，完整执行后 Binary 内容及摘要一致 |

联调发现并修复了客户端文件传输 TLS 兼容、执行器回显文件参数路径导致结果被拒绝、DataTable 将 XLSX 字节写入 CSV 文件的问题，修复后相关场景均已重测。浏览器夹具参数错误也已纠正后复测。早期失败以及修复前虽为成功终态但 CSV 格式错误的执行均保留为审计记录，不计作功能通过证据。

### 部署一致性、清理与边界

部署的 11 个服务端文件、9 个客户端源码文件和 n8n 安装包的 36 个文件与本地校验一致；服务器 Nginx 配置检查通过。节点 tarball SHA-256 为 `d558ab0cc05b5c060bbb5f685d9b44af9aaac2870305612b4a6b22cd0895f38b`。服务器写入限于指定源码部署目录，保留文件存储及传输配置。

服务端本轮 29 条执行均已终态，临时传输授权全部撤销；这些记录包含预期失败和修复前失败，不能以成功终态数量代替场景验收。14 个临时机器人及工作流声明、42 个文件句柄、7 个 n8n 工作流、115 条 n8n 父子执行记录和 14 个客户端测试运行目录均已清理；原声明策略恢复，非测试数据保留。临时回环服务、服务器测试包及备份已清理，服务端和客户端执行审计保留。**临时凭据导出副本按用户要求保留，未记为已删除；n8n 原凭据保持不变。** 客户端空闲，无残留执行进程或私有文件工作目录，n8n 保持运行且健康。

本轮未重建完整客户端 EXE，未实测 Microsoft Office、全部 111 项操作、商业 OCR/文档服务、企业共享存储及其他远程文件服务，也未重跑全仓 `make check`。当前结论限于上述自动化与受控真实场景，不作为全平台或生产容量验收。脱敏执行标识、产物摘要、回归结果与清理状态见 [validation-evidence.json](validation-evidence.json) 的 `officeFileValidation`。

## CI 定向回归核验（2026-10-12）

本轮基于 `a200c867` 与未提交的 CI 修改，在本地 Windows、Python 3.13、Node.js 24.18.0 环境执行。检查限于 OpenAPI、五组 Engine 组件及 n8n 节点的定向回归，没有操作部署环境。

[主 CI](../../.github/workflows/main-ci.yml) 在 OpenAPI、n8n 集成、Engine 组件/共享代码/依赖或本回归入口变化时调用 [Integration Regression](../../.github/workflows/integration-regression.yml)。所有组件目录变化都会触发，是因为节点测试核对完整组件目录清单；实际 Engine 测试仍只运行下表五组。新增检查结果纳入主 CI 汇总，应运行却失败、取消或跳过时汇总失败。工作流也支持手动触发，各任务保存 JUnit 报告。

| 检查 | 本地结果与范围 |
| --- | --- |
| OpenAPI | 284 项通过，无跳过；覆盖准入与只读约束、执行隔离与生命周期、MCP/REST、JSON 契约、迁移就绪与敏感日志；保留 4 个既有 SQLite datetime adapter 弃用警告 |
| Engine browser | 5 项通过：默认窗口激活、只读参数关闭激活、异常兼容及组件元数据；窗口操作使用 mock |
| Engine database | 12 项通过：SQLite 查询与只读连接、游标释放、元数据、可选驱动缺失提示；不连接远程数据库 |
| Engine email | 22 项通过：只读/标记已读语义、连接释放、附件路径限制、IMAP 指令与文件夹编码；使用测试桩和模拟邮件连接 |
| Engine network | 4 项通过：本机回环 HTTP GET/HEAD、FTP 超时与失败清理 |
| Engine enterprise | 2 项通过：明文共享变量读取不请求密钥、变量不存在时返回空值；服务调用使用 mock |
| n8n | 36 项通过，无跳过；`npm ci`、构建、类型检查、ESLint 和 Prettier 通过；传输测试使用本机回环或 mock，未启动真实 n8n 服务 |
| CI 静态及门禁核验 | 两个工作流通过 actionlint；运行脚本通过 Ruff 与格式检查；汇总的成功、失败、取消、意外跳过及无相关变更场景已验证 |

[Python 回归入口](../../.github/scripts/run-integration-regression.py) 使用临时环境并固定测试文件。OpenAPI 按项目锁文件安装；Engine 按五组分别启动进程，以 Engine 锁文件中的直接依赖版本构建最小测试环境，不安装完整 GUI/EXE 依赖图，不生成组件锁文件。邮件测试的替身模块不会污染其他组，测试包同名通过独立收集和 `importlib` 模式处理。Engine 本轮共 45 项通过，无跳过；这不等于完整组件打包验证。

从仓库根目录复现（需要 uv 0.12.1；Engine 需 Windows；报告目录请放在仓库外）：

```text
python .github/scripts/run-integration-regression.py openapi --report-dir <报告目录>
python .github/scripts/run-integration-regression.py engine --component <browser|database|email|network|enterprise> --report-dir <报告目录>
```

n8n 在 `integrations/n8n/n8n-nodes-astron-rpa` 执行 `npm ci`、`npm run typecheck`、`npm run lint`、`npm run format:check -- --end-of-line auto` 和 `npm test`。CI 使用同样的构建与测试命令，另输出 JUnit。换行参数兼容 Windows checkout 的 CRLF。此次 `npm ci` 输出 12 项 high 依赖审计告警，未改动依赖锁文件或将安装成功表述为安全审计通过。

**覆盖边界：**本轮未实测 Windows GUI/浏览器插件、完整客户端 EXE、远程数据库或真实 n8n/服务器/客户端联调，未覆盖其他 Engine 组，也未重跑全仓 `make check`。准入清单中的 **29 个操作是能力清单数量，不是本次独立复验通过数**。历史联调记录仅保留为历史证据。2026-10-12 形成本地记录时 GitHub 托管 CI 尚未运行（当时按要求不提交、不推送）；后续 `4e26f079` 的实际 CI 结果见上文，不能将旧提交的结果用于确认当前提交。

## 公共框架历史验收

本次新增独立的 AstronRPA Community Node，通过 HTTPS MCP 完成工作流读取、执行、查询和取消，并在 OpenAPI 服务中实现工作流声明与准入校验。已完成相关自动化测试，以及真实 n8n、OpenAPI 服务和 Windows 客户端联调；全仓质量检查和运行中设计器发布的组合验证存在未完成项，详见文末。

使用方法见[节点说明](n8n-nodes-astron-rpa/README.md)和[工作流示例](n8n-nodes-astron-rpa/examples/README.md)。执行标识、恢复前后期限、产物校验值及发布时序见[验证证据](validation-evidence.json)。

## 本次实现

- 新增[Community Node](n8n-nodes-astron-rpa/nodes/AstronRpa/AstronRpa.node.ts)及凭据类型，提供工作流列表、详情、Async／Wait／Sync 执行、执行查询和精准取消，业务操作统一通过 MCP。
- 实现[持久等待编排](n8n-nodes-astron-rpa/execution/workflow.ts)与[执行状态观察](n8n-nodes-astron-rpa/execution/runner.ts)：使用 n8n 公开接口创建子执行、保存等待检查点；派发前保存固定请求和幂等键，响应丢失时有界恢复，取得执行 ID 后查询原执行。
- 实现批量顺序等待、输入项关联和错误路由；前项状态未确认时阻止后项派发。区分网络请求超时、调用方等待预算与 RPA 执行期限。
- 新增服务端[声明与准入策略](../../backend/openapi-service/app/services/integration_policy.py)，由管理员维护声明并绑定工作流版本、输入 Schema 和完整声明摘要。在纳入管理的范围内，固定 MCP、动态 MCP 与 REST 共用准入校验，拒绝未知、失效或不完整的声明。
- 调整[已受理执行的管理契约](../../backend/openapi-service/app/services/workflow_control.py)：普通重新发布后仍可查询、同键恢复和取消原执行，同时保留所有权、工作流开放状态及鉴权检查。这也改变了既有 REST 行为：详情接口 `GET /executions/{execution_id}` 不再仅因当前发布版本变化而拒绝原执行查询，列表接口 `GET /executions/get` 同样保留符合授权条件的旧版本执行；返回的仍是原执行版本，新执行仍须使用当前发布版本。
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

PR 审阅修订回归（2026-09-30）：在最新 main 上变基后，OpenAPI 定向测试 212 项、节点测试 19 项通过。新增策略缓存测试覆盖未变更文件只读取/解析一次、mtime 变化、同 mtime 原子替换、文件缺失/损坏/不可读、读取期间更新、配置路径变化和调用方修改隔离；错误时仍拒绝使用旧策略。修改涉及的 Python 文件 Ruff 与格式检查、节点构建、类型检查、ESLint、README 格式及差异检查通过。本轮未重做真实联调；全仓 `make check` 仍停在下文记录的 frontend 根目录缺少 `tsconfig.json` 问题。目标 n8n `2.36.9` 的官方 Dockerfile 固定 Node.js `24.18.1`，满足包的 `>=24` 声明；此项为镜像构建文件核对，不代表本轮运行了 Docker 镜像。

## JSON 数据契约审阅修订验证（2026-10-08）

`data-driven_flows` 已变基到本地 main `ea33dd5b`，只重放 JSON 数据能力提交。以下为本轮迁移、启动检查与结果边界修订的验证，后文保留此前公共框架的验证记录。

使用本机已安装的 n8n `2.40.7`、Node.js `24.18.0`、tarball 安装的修订节点，以及现有真实 MySQL、OpenAPI 服务和 Windows 客户端。客户端托管协议为 1，服务端与客户端状态均正常。

| 验证 | 结果 |
| --- | --- |
| 本地回归与静态检查 | OpenAPI 定向测试 244 项、节点测试 24 项通过；TypeScript 构建和类型检查、ESLint、修改 Python 文件的 Ruff 检查与格式检查通过。后端仍有 4 个既有 SQLite datetime adapter 警告 |
| 节点格式 | 修改文件的默认 Prettier 检查通过；完整包使用 `--end-of-line auto` 通过。Windows `core.autocrlf=true` 下，完整包默认命令会对既有 CRLF 文件报换行差异 |
| 缺迁移启动 | 在隔离的真实 MySQL 旧库中，缺少 `data_contract` 时 Uvicorn 以退出码 3 结束，诊断明确列出缺列及 002 迁移；服务未进入就绪状态 |
| 旧库与新库一致性 | 在表默认字符集为 `utf8mb3` 的旧库执行完整 002，已有中文和 emoji 数据保留；四个 JSON 列的类型、NULL 属性、注释、字符集与排序规则均与新建库一致，两库通过启动检查 |
| JSON 往返与幂等 | 经 n8n → MCP → 现有客户端执行，`0`、`false`、`null`、嵌套数据、中文和 emoji 完整往返；同键返回同一 executionId / runId，客户端只有一条执行回执 |
| 精确字节边界 | 客户端生成的业务结果为 1,048,576 字节时，服务端成功持久化，n8n 读取成功；额外的执行状态和身份信息不消耗业务结果额度 |
| 超限和 Schema 不匹配 | 1,048,577 字节及输出 Schema 不匹配的结果均转为 `FAILED / UNSUPPORTED_RESULT`；真实数据库仅保存失败封装 `data: null`，并保留受理时冻结的 limits 和 outputSchema |
| 产物一致性 | 同步的 49 个服务端文件校验一致；节点 tarball 的 17 个文件与 n8n 安装目录逐字节一致 |

本轮额外修复了实测发现的两处边界问题：旧表的 `MODIFY COLUMN` 会回退 JSON 列字符集；节点将整个执行封装计入结果额度，会误拒绝精确 1 MiB 的合法结果。相关自动化回归及修复后的真实执行均通过。

临时 MySQL 库、机器人、服务端工作流、n8n 工作流与执行数据、上传包、服务器测试备份和两个临时客户端运行目录均已清理；原准入策略已恢复，临时明文凭据已删除。n8n 测试进程已停止，客户端保持登录并处于 ready / 空闲状态，本轮无非终态执行。服务端和客户端执行审计记录保留。执行证据见 `validation-evidence.json` 的 `jsonContractReview`。

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

按当时全部 25 个组件的操作行为核对分类，本类准入清单为 5 个组件、29 个操作。下表与执行标识保留 2026-09-20 的历史覆盖记录，不据此认定当前代码的全部 29 个操作已独立复验。完整操作名见 [分类清单](n8n-nodes-astron-rpa/capabilities/shared/catalog.ts)及机器可读证据。

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

## 浏览器读取与服务连接变基验证（2026-10-10）

`browser-service` 已变基到本地 main `79f8f6db`，重放两个独有提交，验证代码为 `434b5f46`。本轮未增加功能修订，以下记录对应变基后的代码，不替代上面的历史验收。

使用本机现有 n8n `2.40.7`、Node.js `24.18.0`、tarball 安装的 `n8n-nodes-astron-rpa@0.1.0-dev.2`，以及现有 OpenAPI 服务和已启动的 Windows 客户端。实际 MCP 入口使用 HTTPS 30998 端口，TLS 校验通过，证书有效期为 2026-09-14 至 2026-12-13；默认 443 端口的证书情况不代表该入口。

| 验证 | 本轮结果 |
| --- | --- |
| 本地定向回归 | OpenAPI 279 项、节点 36 项、Engine 相关 18 项通过；后端保留 4 个既有 SQLite datetime 弃用警告 |
| 静态检查 | TypeScript 构建、类型检查、ESLint 通过；完整节点包 Prettier 使用 `--end-of-line auto` 通过。修改涉及的 Python 文件格式检查通过，与 main 对照无新增 Ruff 诊断，既有诊断仍存在 |
| 六类真实场景 | 浏览器读取、HTTP GET/HEAD、SQLite 查询、FTP 目录元数据、IMAP 邮件与共享变量读取，均完成 n8n → MCP／显式 REST → 服务端 → 客户端 → 终态回执闭环 |
| 本轮操作覆盖 | 19 个不同操作：浏览器 8、数据库 3、网络 6、邮件 1、共享变量 1；2026-09-20 的 29 个操作记录仅为历史证据，本轮没有重跑全部 29 个操作 |
| 幂等与查询 | HTTP 同键跨 MCP/REST 重放返回相同 executionId/runId；成功执行在两通道的查询快照一致，客户端回执与 n8n 结果一致且无重复执行 |
| 拒绝边界 | 未声明、非法操作、不完整只读审核在节点及两通道服务端均拒绝；MCP-only 声明使用 REST 返回 `TRANSPORT_NOT_ALLOWED`，拒绝用例无执行记录 |
| 取消隔离 | 取消取得真实 `cancelled`；新执行处于 running 时重复取消旧 ID，新执行仍正常完成 |
| 只读与释放 | IMAP 使用 EXAMINE、BODY.PEEK，未标记已读；FTP 与 IMAP 连接数均归零 |
| 运行数据 | 18 条测试执行均已终态：15 COMPLETED、2 CANCELLED、1 FAILED；首次浏览器活动窗口错误导致的失败不计成功，切回测试页后两通道均通过。所有执行均保留冻结 outputSchema 与 1 MiB limits |
| 部署一致性 | 服务端 48 个文件（OpenAPI app 与网关 Lua）、客户端 9 个组件文件、安装包 29 个文件与本地核对一致；部署环境 Nginx 配置校验通过 |

已恢复原准入策略，清理 11 个临时机器人、临时服务端工作流与共享变量数据、服务器测试包和备份，以及 n8n 临时工作流、其 59 条父子执行记录和 webhook。本机 7 个临时客户端运行目录、导出的明文凭据及测试 TLS 私钥已删除；测试 n8n 进程和回环 HTTP/FTP/IMAP 服务已停止，端口均关闭。原有工作流、凭据与服务端/客户端执行审计保留，客户端处于 ready／空闲状态，无非终态测试执行。n8n 安装所引用的 tarball 保留在仓库外。

本轮仍限定于上述受控 Windows 环境和可信已审核工作流；数据库真实场景为 SQLite，浏览器需要指定插件窗口的活动页。未重建完整客户端 EXE，未重跑全仓检查或完整 Docker 网关 shell 测试。联调期间出现的间歇连接超时按原执行 ID 或同一幂等键恢复，未关闭 TLS 校验或通过自动切换通道重发。
