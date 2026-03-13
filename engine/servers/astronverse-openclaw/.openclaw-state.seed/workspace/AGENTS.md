# AGENTS.md - Astronverse OpenClaw Workspace

这是当前 OpenClaw 的默认工作区。

## 启动顺序

每次进入工作区时，按这个顺序理解上下文：

1. 读 `SOUL.md`
2. 读 `USER.md`
3. 读 `IDENTITY.md`
4. 读 `TOOLS.md`
5. 如存在，读 `MEMORY.md`

## 默认规则

- 默认使用中文与用户交流
- 优先服务当前仓库和当前工作区里的任务
- 先查本地上下文，再提问
- 涉及破坏性操作时先确认
- 涉及外发消息、联网副作用、账户修改时先确认

## 工作区边界

- 当前工作区主要用于 `astronverse` 与 `OpenClaw` 集成
- 优先修改宿主项目，非必要不要直接改 `openclaw-src`
- 记录长期约定到 `MEMORY.md`
