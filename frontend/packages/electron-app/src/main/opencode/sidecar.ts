import { randomUUID } from 'node:crypto'
import { spawn, type ChildProcessByStdio } from 'node:child_process'
import { existsSync } from 'node:fs'
import { createServer } from 'node:net'
import path from 'node:path'
import type { Readable } from 'node:stream'
import { app } from 'electron'

import {
  APP_NAME,
  SIDECAR_FILENAME,
  SIDECAR_HEALTH_PATH,
  SIDECAR_HEALTH_POLL_INTERVAL_MS,
  SIDECAR_HEALTH_TIMEOUT_MS,
  SIDECAR_HOST,
  SIDECAR_USERNAME,
} from './constants'
import { createLogger } from './logging'

export type RuntimePhase = 'stopped' | 'starting' | 'ready' | 'error'

export type RuntimeStatus = {
  phase: RuntimePhase
  host: string | null
  port: number | null
  url: string | null
  startedAt: string | null
  readyAt: string | null
  stoppedAt: string | null
  error: string | null
}

export type RuntimeCredentials = {
  username: string
  password: string
}

export type SidecarConnection = {
  baseUrl: string
  headers: Record<string, string>
}

export type SidecarManager = {
  start: () => Promise<RuntimeStatus>
  stop: () => Promise<RuntimeStatus>
  restart: () => Promise<RuntimeStatus>
  getStatus: () => RuntimeStatus
  awaitInitialization: () => Promise<RuntimeStatus>
  getConnection: () => Promise<SidecarConnection>
}

type ExitInfo = { code: number | null; signal: NodeJS.Signals | null }
type SidecarProcess = ChildProcessByStdio<null, Readable, Readable>
type SidecarManagerOptions = {
  getConfigContent?: () => Promise<string | null | undefined> | string | null | undefined
}

const logger = createLogger('sidecar')
const STOP_ERROR_MESSAGE = 'Sidecar stopped'
const SHUTDOWN_TIMEOUT_MS = 5_000

export function createSidecarManager(options: SidecarManagerOptions = {}): SidecarManager {
  let child: SidecarProcess | null = null
  let startupPromise: Promise<RuntimeStatus> | null = null
  let shutdownPromise: Promise<RuntimeStatus> | null = null
  let startupAbortController: AbortController | null = null
  let stopping = false
  let credentials: RuntimeCredentials | null = null
  let status = createInitialStatus()

  const manager: SidecarManager = {
    start: async () => {
      if (shutdownPromise) {
        await shutdownPromise.catch(() => undefined)
        if (startupPromise) {
          await startupPromise.catch(() => undefined)
        }
      }

      if (startupPromise) {
        return startupPromise
      }

      if (status.phase === 'ready') {
        return snapshot(status)
      }

      stopping = false
      startupAbortController = new AbortController()
      const signal = startupAbortController.signal
      status = {
        ...createInitialStatus(),
        phase: 'starting',
        startedAt: new Date().toISOString(),
      }

      startupPromise = (async () => {
        try {
          const port = await getFreePort()
          assertNotAborted(signal)

          const host = SIDECAR_HOST
          const configContent = await options.getConfigContent?.()
          const url = `http://${host}:${port}`
          credentials = createCredentials()
          const executable = getSidecarPath({
            isPackaged: app.isPackaged,
            resourcesPath: process.resourcesPath,
          })

          if (!existsSync(executable)) {
            throw new Error(`Bundled sidecar is missing at ${executable}`)
          }

          status = { ...status, host, port, url }

          logger.info('starting bundled sidecar', {
            appName: APP_NAME,
            executable,
            hasInlineConfig: Boolean(configContent),
            url,
          })

          child = spawn(
            executable,
            ['--print-logs', '--log-level', 'WARN', 'serve', '--hostname', host, '--port', `${port}`],
            {
              env: {
                ...process.env,
                OPENCODE_CLIENT: 'desktop',
                OPENCODE_SERVER_USERNAME: credentials.username,
                OPENCODE_SERVER_PASSWORD: credentials.password,
                ...(configContent ? { OPENCODE_CONFIG_CONTENT: configContent } : {}),
              },
              windowsHide: true,
              stdio: ['ignore', 'pipe', 'pipe'],
            },
          )

          const currentChild = child
          if (!currentChild) {
            throw new Error('Failed to create bundled sidecar process')
          }

          const spawnErrorPromise = new Promise<never>((_, reject) => {
            currentChild.once('error', (error: Error) => {
              child = null
              if (signal.aborted || stopping) {
                reject(createStopError())
                return
              }

              status = {
                ...status,
                phase: 'error',
                stoppedAt: new Date().toISOString(),
                error: error.message || 'Sidecar failed to start',
              }
              logger.error('bundled sidecar spawn error', error)
              reject(error)
            })
          })

          if (currentChild.stdout) {
            currentChild.stdout.on('data', (chunk: Buffer) => {
              logger.info('sidecar stdout', { output: chunk.toString('utf8').trim() })
            })
          }

          if (currentChild.stderr) {
            currentChild.stderr.on('data', (chunk: Buffer) => {
              logger.warn('sidecar stderr', { output: chunk.toString('utf8').trim() })
            })
          }

          const healthPromise = waitForHealth(url, credentials, signal)
          const exitPromise = new Promise<never>((_, reject) => {
            const onStartupExit = (code: number | null, signalName: NodeJS.Signals | null) => {
              child = null
              if (signal.aborted || stopping) {
                reject(createStopError())
                return
              }

              const payload = formatExitInfo({ code, signal: signalName })
              const error = new Error(`Sidecar exited before becoming healthy (${payload})`)
              status = {
                ...status,
                phase: 'error',
                stoppedAt: new Date().toISOString(),
                error: error.message,
              }
              reject(error)
            }

            currentChild.once('exit', onStartupExit)
          })

          await Promise.race([healthPromise, exitPromise, spawnErrorPromise])
          assertNotAborted(signal)

          currentChild.removeAllListeners('exit')
          currentChild.once('exit', (code, signalName) => {
            child = null

            if (stopping) {
              status = {
                ...status,
                phase: 'stopped',
                stoppedAt: new Date().toISOString(),
                error: null,
              }
              logger.info('bundled sidecar stopped', { url })
              return
            }

            const payload = formatExitInfo({ code, signal: signalName })
            status = {
              ...status,
              phase: 'error',
              stoppedAt: new Date().toISOString(),
              error: `Sidecar exited after becoming ready (${payload})`,
            }
            logger.error('bundled sidecar exited after readiness', {
              url,
              code: code ?? null,
              signal: signalName ?? null,
            })
          })

          status = {
            ...status,
            phase: 'ready',
            readyAt: new Date().toISOString(),
            error: null,
          }

          logger.info('bundled sidecar is healthy', { url: status.url })

          return snapshot(status)
        }
        catch (error) {
          const message = error instanceof Error ? error.message : String(error)
          if (stopping || message === STOP_ERROR_MESSAGE) {
            status = {
              ...status,
              phase: 'stopped',
              stoppedAt: new Date().toISOString(),
              error: null,
            }
            credentials = null
            logger.info('sidecar startup stopped')
            return snapshot(status)
          }

          status = {
            ...status,
            phase: 'error',
            stoppedAt: new Date().toISOString(),
            error: message,
          }
          logger.error('failed to start bundled sidecar', error instanceof Error ? error : String(error))
          return snapshot(status)
        }
        finally {
          startupPromise = null
          startupAbortController = null
        }
      })()

      return startupPromise
    },
    stop: async () => {
      if (shutdownPromise) {
        return shutdownPromise
      }

      shutdownPromise = (async () => {
        stopping = true
        startupAbortController?.abort()

        if (!child) {
          if (startupPromise) {
            await startupPromise.catch(() => undefined)
          }

          status = {
            ...status,
            phase: 'stopped',
            stoppedAt: new Date().toISOString(),
            error: null,
          }
          credentials = null
          return snapshot(status)
        }

        const current = child
        child = null

        try {
          current.kill()
        }
        catch (error) {
          logger.warn('failed to stop sidecar cleanly', error instanceof Error ? error : String(error))
        }

        await waitForChildExit(current, SHUTDOWN_TIMEOUT_MS)

        status = {
          ...status,
          phase: 'stopped',
          stoppedAt: new Date().toISOString(),
          error: null,
        }
        credentials = null
        return snapshot(status)
      })().finally(() => {
        shutdownPromise = null
      })

      return shutdownPromise
    },
    restart: async () => {
      await manager.stop()
      return manager.start()
    },
    getStatus: () => snapshot(status),
    awaitInitialization: () => startupPromise ?? Promise.resolve(snapshot(status)),
    getConnection: async () => {
      const currentStatus =
        status.phase === 'ready' ? snapshot(status) : startupPromise ? await startupPromise : await manager.start()

      if (currentStatus.phase !== 'ready' || !currentStatus.url || !credentials) {
        throw new Error('Bundled runtime is not ready.')
      }

      return {
        baseUrl: currentStatus.url,
        headers: {
          authorization: `Basic ${Buffer.from(`${credentials.username}:${credentials.password}`).toString('base64')}`,
        },
      }
    },
  }

  return manager
}

export function getSidecarPath(options: { isPackaged: boolean; resourcesPath?: string }) {
  if (options.isPackaged) {
    if (!options.resourcesPath) {
      throw new Error('resourcesPath is required when resolving the packaged sidecar path')
    }

    return path.join(options.resourcesPath, SIDECAR_FILENAME)
  }

  // In dev mode, first try app root / resources, then walk up from the electron-app package
  // to the monorepo root (3 levels up: electron-app → packages → frontend → astron-rpa)
  const candidates = [
    path.resolve(app.getAppPath(), 'resources', SIDECAR_FILENAME),
    path.resolve(app.getAppPath(), '..', '..', '..', 'resources', SIDECAR_FILENAME),
  ]

  for (const candidate of candidates) {
    try {
      if (require('node:fs').existsSync(candidate)) {
        return candidate
      }
    }
    catch { /* continue */ }
  }

  return candidates[0]!
}

async function waitForHealth(url: string, credentials: RuntimeCredentials, signal: AbortSignal) {
  const deadline = Date.now() + SIDECAR_HEALTH_TIMEOUT_MS

  while (Date.now() < deadline) {
    assertNotAborted(signal)
    if (await checkHealth(url, credentials, signal)) {
      return
    }

    await delay(SIDECAR_HEALTH_POLL_INTERVAL_MS, signal)
  }

  throw new Error(`Timed out waiting for sidecar health at ${url}${SIDECAR_HEALTH_PATH}`)
}

async function checkHealth(url: string, credentials: RuntimeCredentials, signal: AbortSignal) {
  const healthUrl = new URL(SIDECAR_HEALTH_PATH, url)
  const headers = new Headers()
  headers.set('authorization', `Basic ${Buffer.from(`${credentials.username}:${credentials.password}`).toString('base64')}`)

  try {
    const healthSignal = createCombinedAbortSignal(signal, AbortSignal.timeout(3_000))
    const response = await fetch(healthUrl, { headers, method: 'GET', signal: healthSignal })
    assertNotAborted(signal)
    return response.ok
  }
  catch {
    return false
  }
}

async function waitForChildExit(childProcess: SidecarProcess, timeoutMs: number) {
  let settled = false

  const exitPromise = new Promise<void>((resolve) => {
    childProcess.once('exit', () => { settled = true; resolve() })
    childProcess.once('error', () => { settled = true; resolve() })
  })

  await Promise.race([
    exitPromise,
    delay(timeoutMs).then(() => {
      if (!settled) {
        logger.warn('timed out waiting for sidecar shutdown', { timeoutMs })
      }
    }),
  ])
}

function createCredentials(): RuntimeCredentials {
  return { username: SIDECAR_USERNAME, password: randomUUID() }
}

async function getFreePort() {
  return await new Promise<number>((resolve, reject) => {
    const server = createServer()
    server.once('error', reject)
    server.listen(0, SIDECAR_HOST, () => {
      const address = server.address()
      if (typeof address !== 'object' || !address) {
        server.close()
        reject(new Error('Could not allocate a free port'))
        return
      }

      const port = address.port
      server.close(() => resolve(port))
    })
  })
}

function createInitialStatus(): RuntimeStatus {
  return {
    phase: 'stopped',
    host: null,
    port: null,
    url: null,
    startedAt: null,
    readyAt: null,
    stoppedAt: null,
    error: null,
  }
}

function snapshot(status: RuntimeStatus): RuntimeStatus {
  return { ...status }
}

function formatExitInfo(info: ExitInfo) {
  return `code=${info.code ?? 'unknown'} signal=${info.signal ?? 'unknown'}`
}

function assertNotAborted(signal: AbortSignal) {
  if (signal.aborted) {
    throw createStopError()
  }
}

function createStopError() {
  return new Error(STOP_ERROR_MESSAGE)
}

function createCombinedAbortSignal(...signals: AbortSignal[]) {
  if (typeof AbortSignal.any === 'function') {
    return AbortSignal.any(signals)
  }

  const controller = new AbortController()
  const onAbort = () => controller.abort()

  for (const signal of signals) {
    if (signal.aborted) {
      controller.abort()
      break
    }

    signal.addEventListener('abort', onAbort, { once: true })
  }

  return controller.signal
}

function delay(ms: number, signal?: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => { cleanup(); resolve() }, ms)

    const onAbort = () => { cleanup(); reject(createStopError()) }

    function cleanup() {
      clearTimeout(timer)
      if (signal) {
        signal.removeEventListener('abort', onAbort)
      }
    }

    if (signal) {
      if (signal.aborted) {
        cleanup()
        reject(createStopError())
        return
      }

      signal.addEventListener('abort', onAbort, { once: true })
    }
  })
}
