# IM 集成方案记录

## 目的

记录 Astron 助手通过飞书等 IM 平台接入的方案结论，便于后续按文档继续实现。

当前优先记录的是：

- i 讯飞当前可用的飞书自部署方案
- 基于飞书 `事件与回调` 模式接入 openclaw / Astron 的实现思路

## 当前结论

### 1. 没有 WebSocket 也能实现飞书消息收发

即使当前环境不支持飞书 WebSocket，只支持 `事件与回调`，也仍然可以实现完整的机器人对话。

核心模式不是长连接，而是：

1. 飞书把用户消息事件推送到开发者服务
2. 开发者服务快速确认收到事件
3. 开发者服务异步调用 openclaw / Astron 处理消息
4. 开发者服务再主动调用飞书发送消息接口，把结果发回用户

所以本质上是：

- 收消息：靠飞书事件推送
- 发消息：靠飞书开放接口主动发送

### 2. 长耗时、多次返回也能支持

如果 openclaw 执行时间较长，或者中间会产生多段结果，也可以支持。

正确做法是：

1. 飞书事件回调到达后，服务端立即返回 `200`
2. 后台异步创建任务，交给 openclaw 执行
3. openclaw 产生阶段性结果时，服务端多次调用飞书发送接口
4. 最终结果完成后，再发送最终答复

不能采用的方式：

- 让飞书回调接口一直阻塞，等 openclaw 跑完再返回

原因：

- 飞书回调需要快速响应
- 否则会超时、重试，甚至造成重复执行

## 推荐链路

```text
飞书用户发消息
  -> 飞书事件推送到 Astron 服务
  -> Astron 服务快速 ACK
  -> 异步投递给 openclaw
  -> openclaw 产生中间事件 / 工具结果 / 最终结果
  -> Astron 服务调用飞书发送消息接口
  -> 飞书用户收到多次回复
```

## 适合 Astron 的实现方式

### 收消息链路

建议新增一个飞书回调入口，例如：

```text
POST /api/im/feishu/events
```

职责：

- 接收飞书事件
- 完成 challenge 校验
- 完成 token / 签名 / 加密校验
- 识别消息事件，例如 `im.message.receive_v1`
- 抽取消息上下文并投递异步任务

### 处理链路

飞书事件入站后，建议转换为统一的内部结构：

```ts
type ImInboundMessage = {
  platform: 'feishu'
  tenantKey?: string
  chatId: string
  messageId: string
  userId?: string
  openId?: string
  text: string
  sessionKey: string
  rawEvent: unknown
}
```

然后交给 Astron / openclaw 统一处理。

### 发消息链路

飞书消息回复建议使用两类接口：

1. 新发消息

```text
POST /open-apis/im/v1/messages
```

2. 回复某条消息

```text
POST /open-apis/im/v1/messages/{message_id}/reply
```

建议策略：

- 单轮答复：优先使用 `reply`
- 长任务阶段通知：可使用 `reply` 或 `messages`
- 最终答复：建议继续挂在原消息线程下回复

## openclaw 长任务适配建议

如果 openclaw 处理时间长，建议把输出拆成阶段事件：

```text
task.started
tool.running
tool.result
assistant.partial
assistant.final
task.failed
```

飞书侧可映射为：

- `task.started` -> “已收到，正在处理中”
- `tool.running` -> 可选，不一定发，避免刷屏
- `tool.result` -> 重要中间结果才发
- `assistant.partial` -> 阶段性自然语言总结
- `assistant.final` -> 最终答复
- `task.failed` -> 失败提示

## 建议的数据映射

为避免消息丢失和重复回复，建议保存以下关系：

```text
feishu_event_id
feishu_message_id
feishu_chat_id
feishu_open_id / user_id
astron_session_id
openclaw_task_id
status
created_at
updated_at
```

其中：

- `feishu_event_id` 用于幂等
- `astron_session_id` 用于多轮对话
- `openclaw_task_id` 用于跟踪长任务执行

## 幂等与重试

飞书事件推送存在重试可能，必须做幂等。

建议：

1. 使用飞书事件唯一标识做去重
2. 同一 `message_id` 或 `event_id` 只创建一次任务
3. 如果已经处理过，直接返回成功

## 第一阶段推荐实现范围

先做最小可用版本：

1. 支持飞书事件接收
2. 支持 challenge 验证
3. 支持文本消息 `im.message.receive_v1`
4. 支持把消息转给 openclaw
5. 支持最终结果回消息
6. 支持简单失败提示

第二阶段再补：

1. 中间状态多次推送
2. 群聊 @ 识别
3. 回复消息线程化
4. 幂等表
5. 卡片消息
6. 文件 / 图片类消息

## 当前推荐模式

对 i 讯飞当前环境，推荐优先走：

```text
飞书事件与回调 + 服务端主动发送消息
```

不依赖 WebSocket。

原因：

- 当前环境明确支持
- 能覆盖消息接收、最终回复、长任务异步回复
- 架构上也方便后续扩展到钉钉、企微、QQ

## i 讯飞是否需要单独配置模块

当前结论：

`大概率不需要给 i 讯飞单独做一套配置模块，优先复用飞书配置模块。`

### 判断依据

如果 i 讯飞本质上仍然是基于飞书开放平台的自部署接入，只是当前环境不开放 WebSocket，而是只支持 `事件与回调`，那么它仍然属于飞书通道的一种接入形态，而不是全新的 IM 平台。

如果满足以下条件：

1. 事件接收仍然走飞书 `事件与回调`
2. 鉴权仍然使用飞书体系，例如 `App ID / App Secret / Verification Token / Encrypt Key`
3. 回消息仍然调用飞书开放接口
4. 事件结构、消息结构、接口协议与飞书标准模型兼容

则系统设计上应视为：

```text
IM 平台 = 飞书
接入方式 = WebSocket / Webhook
部署环境 = 标准飞书 / i讯飞环境
```

而不建议直接视为：

```text
IM 平台 = 飞书
IM 平台 = i讯飞
```

### 推荐实现方式

现阶段建议：

1. 继续复用飞书配置模块
2. 飞书配置里支持 `websocket` / `webhook`
3. 如后续确有必要，只在飞书配置中增加轻量环境字段，例如：
   - `environment`
   - `baseUrl`
   - `callbackPath`
   - `tenantName`
4. 不单独新增一个 “i讯飞” IM 渠道卡片

### 什么时候才需要拆出 i 讯飞独立配置

只有出现以下情况，才考虑把 i 讯飞从飞书里拆出来：

1. 事件结构与飞书标准事件不兼容
2. 发送消息接口不是飞书标准接口
3. 鉴权方式不同
4. 域名、租户、权限模型完全独立
5. 业务上必须把 “标准飞书环境” 与 “i讯飞环境” 视为两种独立运营渠道

### 当前设计结论

对于当前 Astron 助手的 IM 集成设计：

- i 讯飞先不作为独立 IM 平台建模
- 先作为飞书 `Webhook` 方案的一种部署环境看待
- UI 和配置优先复用飞书配置模块
- 后续若文档确认存在协议差异，再决定是否拆分

## 后续实现时建议新增的模块

建议优先新增，而不是大改原代码：

```text
backend/.../im/feishu/
  controller/
  service/
  dto/
  client/
  mapper/
```

或者如果继续沿着 openclaw 插件层做，则建议：

```text
openclaw/extensions/feishu-webhook-adapter/
```

## 待确认项

后续正式实现前，需要结合飞书正式文档确认：

1. 当前应用使用的是事件订阅还是交互回调
2. 回调是否开启签名校验
3. 是否启用了 Encrypt Key
4. 当前可申请的飞书权限范围
5. 回消息优先使用 `reply` 还是 `messages`
6. 是否需要支持群聊场景

## 一句话结论

对于 i 讯飞当前“只支持飞书事件与回调，不支持 WebSocket”的环境：

可以实现完整消息收发，也可以支持 openclaw 长耗时、多次返回。

实现原理是：

`飞书推送事件 -> Astron 异步处理 -> Astron 主动调用飞书发送消息接口回推结果`
