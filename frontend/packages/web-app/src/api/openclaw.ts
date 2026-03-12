export type OpenClawChatMessage = {
  role: 'system' | 'developer' | 'user' | 'assistant' | 'tool'
  content: string
}

type WsFrame =
  | { type: 'req'; id: string; method: string; params?: any }
  | { type: 'res'; id: string; ok: boolean; payload?: any; error?: { code?: string; message?: string; details?: any } }
  | { type: 'event'; event: string; payload?: any; seq?: number; stateVersion?: any }

function wsUrlForOpenClawProxy(): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/openclaw`
}

async function openclawChatViaWs(params: {
  text: string
  token?: string
  sessionKey?: string
}): Promise<string> {
  const ws = new WebSocket(wsUrlForOpenClawProxy())

  const awaitOpen = new Promise<void>((resolve, reject) => {
    ws.addEventListener('open', () => resolve(), { once: true })
    ws.addEventListener('error', () => reject(new Error('无法连接到 openclaw gateway（WebSocket）')), { once: true })
  })

  const waitForRes = (id: string) => {
    return new Promise<Extract<WsFrame, { type: 'res' }>>((resolve, reject) => {
      const onMessage = (ev: MessageEvent) => {
        try {
          const frame = JSON.parse(String(ev.data ?? '')) as WsFrame
          if (frame?.type === 'res' && frame.id === id) {
            ws.removeEventListener('message', onMessage)
            if (frame.ok)
              resolve(frame)
            else
              reject(new Error(frame?.error?.message || 'openclaw 响应失败'))
          }
        }
        catch {
          // ignore non-json
        }
      }
      ws.addEventListener('message', onMessage)
      const onClose = () => {
        ws.removeEventListener('message', onMessage)
        reject(new Error('openclaw gateway 连接已关闭'))
      }
      ws.addEventListener('close', onClose, { once: true })
    })
  }

  await awaitOpen

  const connectId = crypto?.randomUUID?.() ?? String(Date.now())
  ws.send(JSON.stringify({
    type: 'req',
    id: connectId,
    method: 'connect',
    params: {
      minProtocol: 3,
      maxProtocol: 3,
      client: {
        id: 'webchat-ui',
        displayName: 'Astron RPA',
        version: 'web-app',
        platform: 'web',
        mode: 'ui',
      },
      role: 'operator',
      scopes: ['operator.read', 'operator.write'],
      auth: params.token ? { token: params.token } : undefined,
      userAgent: navigator.userAgent,
      locale: navigator.language,
    },
  } satisfies WsFrame))

  await waitForRes(connectId)

  const sendId = crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`
  let latestText = ''

  const finalText = new Promise<string>((resolve, reject) => {
    const onMessage = (ev: MessageEvent) => {
      let frame: WsFrame | null = null
      try {
        frame = JSON.parse(String(ev.data ?? '')) as WsFrame
      }
      catch {
        return
      }

      if (frame.type === 'event' && frame.event === 'chat') {
        const state = frame.payload?.state
        const text = frame.payload?.message?.content?.[0]?.text
        if (typeof text === 'string' && text.trim())
          latestText = text
        if (state === 'final') {
          cleanup()
          resolve(latestText || '（openclaw 没有返回内容）')
        }
        if (state === 'error') {
          cleanup()
          reject(new Error(frame.payload?.errorMessage || 'openclaw 执行出错'))
        }
      }

      if (frame.type === 'res' && frame.id === sendId && frame.ok === false) {
        cleanup()
        reject(new Error(frame?.error?.message || 'openclaw chat.send 失败'))
      }
    }

    const onClose = () => {
      cleanup()
      reject(new Error('openclaw gateway 连接已关闭'))
    }

    const cleanup = () => {
      ws.removeEventListener('message', onMessage)
      ws.removeEventListener('close', onClose)
      try {
        ws.close()
      }
      catch {
        // ignore
      }
    }

    ws.addEventListener('message', onMessage)
    ws.addEventListener('close', onClose)
  })

  ws.send(JSON.stringify({
    type: 'req',
    id: sendId,
    method: 'chat.send',
    params: {
      sessionKey: params.sessionKey ?? 'main',
      message: params.text,
      deliver: false,
      idempotencyKey: sendId,
    },
  } satisfies WsFrame))

  return await finalText
}

export async function openclawChatCompletions(params: {
  messages: OpenClawChatMessage[]
  model?: string
  token?: string
}): Promise<string> {
  // OpenClaw 默认稳定可用的是 Gateway WebSocket（chat.send + chat 事件流）
  // openai/openresponses HTTP 兼容端点通常需要在 openclaw 配置里显式开启
  const lastUser = [...params.messages].reverse().find(m => m.role === 'user')?.content ?? ''
  return await openclawChatViaWs({ text: lastUser, token: params.token })
}

