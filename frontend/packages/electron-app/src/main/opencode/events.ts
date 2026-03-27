import { createLogger } from './logging'
import type { DesktopRuntimeEvent } from '../../shared/sessions'
import type { RuntimeApi } from './api'

export type RuntimeEventStream = {
  start: () => void
  stop: () => void
  subscribe: (listener: (event: DesktopRuntimeEvent) => void) => () => void
}

const logger = createLogger('runtime-events')
const RETRY_DELAY_MS = 1_000

export function createRuntimeEventStream(api: Pick<RuntimeApi, 'openEventStream'>): RuntimeEventStream {
  const listeners = new Set<(event: DesktopRuntimeEvent) => void>()
  let abortController: AbortController | null = null
  let running = false

  return {
    start: () => {
      if (running) {
        return
      }

      running = true
      void runLoop()
    },
    stop: () => {
      running = false
      abortController?.abort()
      abortController = null
    },
    subscribe: (listener) => {
      listeners.add(listener)
      return () => {
        listeners.delete(listener)
      }
    },
  }

  async function runLoop() {
    while (running) {
      abortController = new AbortController()

      try {
        const response = await api.openEventStream(abortController.signal)
        await readSse(response, abortController.signal)
      }
      catch (error) {
        if (!running || isAbortError(error)) {
          return
        }

        logger.warn('bundled runtime event stream disconnected; retrying', error instanceof Error ? error : String(error))
        await delay(RETRY_DELAY_MS)
      }
    }
  }

  async function readSse(response: Response, signal: AbortSignal) {
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Bundled runtime event stream returned no readable body.')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (running) {
      const { done, value } = await reader.read()
      if (done) {
        break
      }

      if (signal.aborted) {
        return
      }

      buffer += decoder.decode(value, { stream: true })
      buffer = processBuffer(buffer)
    }

    buffer += decoder.decode()
    processBuffer(`${buffer}\n\n`)
  }

  function processBuffer(buffer: string) {
    let remaining = buffer.replace(/\r\n/g, '\n')
    let boundary = remaining.indexOf('\n\n')

    while (boundary >= 0) {
      const frame = remaining.slice(0, boundary)
      remaining = remaining.slice(boundary + 2)
      emitFrame(frame)
      boundary = remaining.indexOf('\n\n')
    }

    return remaining
  }

  function emitFrame(frame: string) {
    if (!frame.trim()) {
      return
    }

    const data = frame
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart())
      .join('\n')

    if (!data) {
      return
    }

    const event = parseRuntimeEvent(data)
    if (!event) {
      return
    }

    for (const listener of listeners) {
      listener(event)
    }
  }
}

function parseRuntimeEvent(payload: string): DesktopRuntimeEvent | null {
  try {
    const parsed = JSON.parse(payload) as { type?: unknown; properties?: unknown }
    if (typeof parsed.type !== 'string' || !('properties' in parsed)) {
      return null
    }

    return parsed as DesktopRuntimeEvent
  }
  catch {
    return null
  }
}

function isAbortError(error: unknown) {
  return error instanceof Error && error.name === 'AbortError'
}

function delay(ms: number) {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms)
  })
}
