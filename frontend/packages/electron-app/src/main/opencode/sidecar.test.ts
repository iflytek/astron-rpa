import { EventEmitter } from 'node:events'
import path from 'node:path'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const spawnMock = vi.fn()
const existsSyncMock = vi.fn(() => true)
const fetchMock = vi.fn()

vi.mock('electron', () => ({
  app: {
    isPackaged: false,
    getAppPath: () => 'D:/Projects/PAREO/astron-rpa/frontend/packages/electron-app',
    getPath: (name: string) => {
      if (name === 'userData') {
        return 'C:/Users/zyzhou23/AppData/Roaming/astron-rpa'
      }
      throw new Error(`Unexpected app path request: ${name}`)
    },
  },
}))

vi.mock('node:child_process', () => ({
  spawn: spawnMock,
}))

vi.mock('node:fs', async () => {
  const actual = await vi.importActual<typeof import('node:fs')>('node:fs')
  return {
    ...actual,
    existsSync: existsSyncMock,
  }
})

vi.mock('node:net', () => ({
  createServer: () => ({
    once: vi.fn(),
    listen: (_port: number, _host: string, callback: () => void) => callback(),
    address: () => ({ port: 43123 }),
    close: (callback?: () => void) => callback?.(),
  }),
}))

function createFakeChildProcess() {
  const process = new EventEmitter() as EventEmitter & {
    kill: ReturnType<typeof vi.fn>
    stdout: EventEmitter
    stderr: EventEmitter
  }
  process.kill = vi.fn()
  process.stdout = new EventEmitter()
  process.stderr = new EventEmitter()
  return process
}

describe('createSidecarManager', () => {
  beforeEach(() => {
    spawnMock.mockReset()
    existsSyncMock.mockClear()
    fetchMock.mockReset()
    fetchMock.mockResolvedValue({ ok: true })
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('passes isolated opencode XDG directories under astron-rpa userData', async () => {
    const fakeChild = createFakeChildProcess()
    spawnMock.mockReturnValue(fakeChild)

    const { createSidecarManager } = await import('./sidecar')
    const manager = createSidecarManager()

    await manager.start()

    const isolatedRoot = path.join('C:/Users/zyzhou23/AppData/Roaming/astron-rpa', 'opencode')
    expect(spawnMock).toHaveBeenCalledTimes(1)
    const spawnEnv = spawnMock.mock.calls[0]?.[2]?.env
    expect(spawnEnv).toMatchObject({
      XDG_DATA_HOME: path.join(isolatedRoot, 'data'),
      XDG_CONFIG_HOME: path.join(isolatedRoot, 'config'),
      XDG_STATE_HOME: path.join(isolatedRoot, 'state'),
      XDG_CACHE_HOME: path.join(isolatedRoot, 'cache'),
    })
  })
})
