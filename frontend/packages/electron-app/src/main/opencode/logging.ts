import { mkdirSync, appendFileSync } from 'node:fs'
import path from 'node:path'
import util from 'node:util'

type LogDetails = Record<string, unknown> | Error | unknown[] | string | number | boolean | null | undefined

export type Logger = {
  info: (message: string, details?: LogDetails) => void
  warn: (message: string, details?: LogDetails) => void
  error: (message: string, details?: LogDetails) => void
}

let logFilePath: string | null = null

export function initializeFileLogger(nextLogFilePath: string) {
  mkdirSync(path.dirname(nextLogFilePath), { recursive: true })
  logFilePath = nextLogFilePath
}

function write(level: 'info' | 'warn' | 'error', scope: string, message: string, details?: LogDetails) {
  const prefix = `[opencode:${scope}] ${message}`
  if (typeof details === 'undefined') {
    console[level](prefix)
    writeToFile(level, scope, message)
    return
  }

  console[level](prefix, details)
  writeToFile(level, scope, message, details)
}

export function createLogger(scope: string): Logger {
  return {
    info: (message, details) => write('info', scope, message, details),
    warn: (message, details) => write('warn', scope, message, details),
    error: (message, details) => write('error', scope, message, details),
  }
}

function writeToFile(level: 'info' | 'warn' | 'error', scope: string, message: string, details?: LogDetails) {
  if (!logFilePath) {
    return
  }

  const timestamp = new Date().toISOString()
  const detailText = formatDetails(details)
  const line = `${timestamp} [${level.toUpperCase()}] [opencode:${scope}] ${message}${detailText ? ` ${detailText}` : ''}\n`
  appendFileSync(logFilePath, line, 'utf8')
}

function formatDetails(details?: LogDetails) {
  if (typeof details === 'undefined') {
    return ''
  }

  if (details instanceof Error) {
    return details.stack || details.message
  }

  if (
    typeof details === 'string' ||
    typeof details === 'number' ||
    typeof details === 'boolean' ||
    details === null
  ) {
    return String(details)
  }

  return util.inspect(details, { depth: 6, breakLength: Infinity, compact: true })
}
