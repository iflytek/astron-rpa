# AI Studio 与 OpenCode 集成说明（从规划到落地）

本文档整理自整体迁移规划起，到当前 astron-rpa 中「弃用 OpenRPA 壳、保留 opencode 逻辑 + Vue AI Studio」相关改动的摘要，便于后续维护与排障。

---

## 1. 目标与原则

- **目标**
  - 不在产品内承载 OpenRPA 的桌面 UI，保留其与 **opencode** 相关的运行时能力。
  - 将上述能力接入 **astron-rpa 现有 Electron 工程**，由 **Vue 3 AI Studio** 作为唯一前端壳。
  - 会话、助手/群聊模板、消息等走 **真实 opencode 后端**（IPC → 主进程 → sidecar），避免 mock 会话 ID 或纯本地假数据误入生产路径。
  - 视觉与交互尽量对齐 **source-only** 参考工程中的 AI Studio。
- **原则**
  - 主进程侧沿用 OpenRPA 移植的 `opencode/`、`store/`、`adapter`、IPC 契约。
  - 渲染进程通过 `window.opencodeApi` 与主进程通信；无该 API 时可回退 mock（开发/纯 Web 场景）。

---

## 2. 架构概览

```text
Vue AI Studio (web-app)
    │  Pinia: useAIStudioStore
    │  AIStudioProvider: mock / opencodeProvider
    ▼
preload contextBridge → window.opencodeApi
    ▼
Electron main: opencode-ipc.ts
    ├── assistant-store / settings-store / session 等
    ├── opencode/adapter.ts（数据映射）
    └── opencode sidecar（Go 二进制）
```

---

## 3. Electron 主进程与共享层

### 3.1 路径与工作目录（Windows）

- **文件**：`frontend/packages/electron-app/src/main/path.ts`
- **要点**：Windows 下开发环境也统一使用 `userDataPath` 作为 `appWorkPath`，使 `python_core`、日志、扩展目录在 dev/prod 一致（例如 `%APPDATA%/astron-rpa/...`）。

### 3.2 OpenCode 侧

- **目录**：`frontend/packages/electron-app/src/main/opencode/`
  - 侧car 启动、`api`、`config`、`events` 等与 OpenRPA 对齐的调整主要在 import 与装配点。
- **配置生成**：`opencode/config.ts` 读取 `settings-store` 的 provider 配置，写入 opencode 可识别的 `provider` / `model` 形态。

### 3.3 数据适配

- **文件**：`frontend/packages/electron-app/src/main/opencode/adapter.ts`
- **要点**：将 assistant / group room 等映射为前端 `StudioAssistant`、`StudioAssistantGroup` 等类型；补充字段示例：
  - `persona`、`capabilities`、`skills`
  - 群聊：`groupParticipantAssistantIds`、`groupCollaborationMode`（与 `shared/assistants.ts` 中协作模式类型一致）

### 3.4 Assistant / 群聊 持久化

- **文件**：`frontend/packages/electron-app/src/main/store/assistant-store.ts`
- **共享类型**：`frontend/packages/electron-app/src/shared/assistants.ts`
- **要点**：群聊模板支持 `collaborationMode`；创建/更新时校验并落库。

### 3.5 IPC

- **文件**：`frontend/packages/electron-app/src/main/opencode-ipc.ts`
- **典型行为**：
  - `getBootstrap`：在列举会话前调用 `cleanupMissingRuntimeSessions` / `cleanupMissingGroupRoomSessions`，清理失效映射。
  - `createSession`：payload 支持 `assistantId`、`groupRoomId`；创建成功后 `attachRuntimeSession` 或 `attachGroupRoomSession`。
  - `deleteSession`：删除 sidecar 会话后再次执行上述 cleanup，保持本地映射一致。
  - `getSettings` / `saveProvider` / `saveDefaultModel`：与 `settings-store` 对接。

### 3.6 Provider 注册表（与 OpenRPA 对齐）

- **文件**：`frontend/packages/electron-app/src/shared/provider-registry.ts`
- **内容**：与 OpenRPA `PROVIDER_REGISTRY` 同构，包含 `ready` 与 `coming_soon`、OpenAI 兼容网关、自定义接口等；主进程校验与落盘均依赖此表。

---

## 4. Preload

- **文件**：`frontend/packages/electron-app/src/preload/index.ts`、`index.d.ts`
- **暴露**：`window.opencodeApi`，含 `getBootstrap`、`getSession`、`createSession`（含 assistant/group 参数）、`deleteSession`、`sendMessage`、`getSettings`、`saveProvider`、`saveDefaultModel`、助手/群聊 CRUD 等。

---

## 5. 前端 web-app（AI Studio）

### 5.1 状态与 Provider 切换

- **文件**：`frontend/packages/web-app/src/stores/useAIStudioStore.ts`
- **要点**：
  - 存在 `window.opencodeApi` 时使用 `opencodeProvider`，否则 mock。
  - Electron 下 **`activeSessionId` 初值不再用 mock 默认 ID**，避免对不存在的会话请求 `getSession` 导致 400。
  - `createAssistant` / `updateAssistant` / `deleteAssistant`、`deleteSession` 等在桌面模式下走 IPC，并以 **`refreshBootstrap`** 刷新侧栏与当前会话状态。
  - `createSession` 向主进程传递 `assistantId` / 群聊 ID（与 preload 契约一致）。

### 5.2 Opencode Provider

- **文件**：`frontend/packages/web-app/src/views/AIStudio/providers/opencodeProvider.ts`
- **要点**：封装 `window.opencodeApi`，`createSession` 映射 assistant / group 等参数。

### 5.3 页面与布局

- **路由/菜单**：`router/index.ts`、`constants/menu.ts`（如 `AISTUDIOHOME` 等）。
- **壳层**：`components/HomeContent.vue` 对齐 source-only 的 AI Studio 布局与背景样式。
- **AI Studio 入口**：`views/AIStudio/index.vue` 中 `activeSessionId` 与创建会话/助手提交流程与 store `await` 对齐。

### 5.4 UI 组件与样式

- **补充**：`src/components/ui/*`、`src/lib/utils.ts`（`cn`），以及 `package.json` 中 `clsx`、`tailwind-merge`、`reka-ui`、`lucide-vue-next` 等依赖。
- **全局样式**：`assets/css/default.css` 中字体与 CSS 变量与 source-only 对齐。
- **侧栏微调**：`views/AIStudio/components/AssistantSidebar.vue` 弱化搜索区与列表区的视觉割裂（在保留设计语言前提下）。

### 5.5 配置中心（大模型供应商）

- **文件**：`frontend/packages/web-app/src/views/AIStudio/components/SettingsCenterView.vue`
- **原问题**：仅硬编码 6 个供应商，与主进程 `provider-registry` 不一致，用户感觉「支持的供应商很少」。
- **现状**：
  - 列表按与 OpenRPA/opencode 一致的 **完整 provider 定义** 展开（含 `OpenRouter`、`Vercel`、`xAI`、`DeepSeek`、 Moonshot / MiniMax / Z.AI、`custom-openai-compatible` 等）。
  - **`coming_soon`** 供应商仅展示说明，不提供完整保存流程。
  - 通过 **`getSettings` / `saveProvider` / `saveDefaultModel`** 与主进程真实设置联动；支持 Base URL、显示名称（自定义兼容接口）等字段。
  - 默认模型选项来自「已配置且带模型 ID」的供应商，并单独提供「保存默认模型」按钮。

> 说明：`PROVIDER_OPTIONS` 目前在前端文件中维护一份与 `electron-app/src/shared/provider-registry.ts` 同步的清单。若后续要避免双份维护，可将 registry 抽成 monorepo 内共享包或构建时同步。

---

## 6. 资源与 Sidecar

- opencode 二进制通过 electron-app 脚本拉取并放入 **resources**，**electron-builder** `extraResources` 等与打包说明以工程内实际配置为准。
- 用户需在 **`electron-app` 包目录** 执行 `npm run fetch:opencode`（而非误在仓库根或其它包执行）。

---

## 7. 常见问题与排障

| 现象 | 可能原因 | 处理方向 |
|------|----------|----------|
| `getSession` 400 / `prompt_async` Bad Request | 仍使用 mock 会话 ID（如 `finance-q3`） | 确保 Electron 下默认会话来自 bootstrap，初值勿写死 mock ID |
| Vite 无法解析 `@/components/ui/*` | 组件未拷贝或路径错误 | 补齐 `components/ui` 与 `@/lib/utils` |
| `clsx` 重复声明 | `utils.ts` 被重复拼接 | 保留单份 `cn` 实现 |
| Python 路径指向 `electron-app/data/...` | 旧 `appWorkPath` 逻辑 | 确认 Windows 下 dev 也走 `userDataPath` |
| 心跳 `/api/robot/terminal/beat` 500 | 远端路由/API 偶发 | 对照 route 日志，区分本地与上游问题 |
| 配置页供应商仍很少 | 旧版仅 6 项硬编码 | 使用已接 `opencodeApi` 的 `SettingsCenterView` |

---

## 8. 建议验证步骤

1. 启动 Electron 应用，打开 AI Studio，确认侧栏会话与模板来自 **bootstrap**，无非法默认会话请求。
2. 新建/编辑/删除助手与群聊模板，刷新后仍存在（IPC + `refreshBootstrap`）。
3. 新建/删除会话，侧栏与 opencode 侧一致，映射无脏数据。
4. 打开配置中心：供应商列表完整；配置 Key/Model/Base URL 后 **保存**，重启应用后仍生效；**保存默认模型** 后主进程 `defaultModel` 正确。

---

## 9. 后续可做（非本文档范围但若需要可继续）

- 将前端 `PROVIDER_OPTIONS` 与 `electron-app` 的 `provider-registry` **单一数据源化**。
- 将 `coming_soon`（Ollama、LM Studio、Vertex、Bedrock、Copilot）逐类补齐 **环境变量 / OAuth / 本地发现** 与主进程落盘格式。
- MCP / Skills / 行为配置若需真实生效，需分别对接 scheduler、opencode 或自有配置存储（当前 UI 部分可能仍为演示数据）。

---

## 10. 关键文件索引

| 区域 | 路径 |
|------|------|
| Provider 注册（主进程） | `frontend/packages/electron-app/src/shared/provider-registry.ts` |
| 设置持久化 | `frontend/packages/electron-app/src/main/store/settings-store.ts` |
| IPC | `frontend/packages/electron-app/src/main/opencode-ipc.ts` |
| Preload | `frontend/packages/electron-app/src/preload/index.ts` |
| AI Studio Store | `frontend/packages/web-app/src/stores/useAIStudioStore.ts` |
| Opencode Provider | `frontend/packages/web-app/src/views/AIStudio/providers/opencodeProvider.ts` |
| 配置中心 UI | `frontend/packages/web-app/src/views/AIStudio/components/SettingsCenterView.vue` |
| 主布局 | `frontend/packages/web-app/src/components/HomeContent.vue` |
| Windows 工作路径 | `frontend/packages/electron-app/src/main/path.ts` |

---

*文档版本：与当前仓库变更同步整理；如有新增 IPC 或 registry 字段，请同步更新第 3、5、10 节。*
