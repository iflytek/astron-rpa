import { bgRed, bgYellow, blue, green } from 'ansis'

export type LogType = 'error' | 'warn' | 'info'
export type LogLevel = LogType | 'silent'

export interface LoggerOptions {
  customLogger?: Logger
  console?: Console
  failOnWarn?: boolean
}

export const LogLevels: Record<LogLevel, number> = {
  silent: 0,
  error: 1,
  warn: 2,
  info: 3,
}

export interface Logger {
  level: LogLevel
  info: (...args: any[]) => void
  warn: (...args: any[]) => void
  warnOnce: (...args: any[]) => void
  error: (...args: any[]) => void
  success: (...args: any[]) => void
}

function format(msgs: any[]) {
  return msgs.filter(arg => arg !== undefined && arg !== false).join(' ')
}

const warnedMessages = new Set<string>()

export function createLogger(
  level: LogLevel = 'info',
  {
    customLogger,
    console = globalThis.console,
    failOnWarn = false,
  }: LoggerOptions = {},
): Logger {
  if (customLogger) {
    return customLogger
  }

  function output(type: LogType, msg: string) {
    const thresh = LogLevels[logger.level]
    if (thresh < LogLevels[type])
      return

    const method = type === 'info' ? 'log' : type
    console[method](msg)
  }

  const logger: Logger = {
    level,

    info(...msgs: any[]): void {
      output('info', `${blue`ℹ`} ${format(msgs)}`)
    },

    warn(...msgs: any[]): void {
      const message = format(msgs)
      if (failOnWarn) {
        throw new Error(message)
      }
      warnedMessages.add(message)
      output('warn', `\n${bgYellow` WARN `} ${message}\n`)
    },

    warnOnce(...msgs: any[]): void {
      const message = format(msgs)
      if (warnedMessages.has(message)) {
        return
      }

      if (failOnWarn) {
        throw new Error(message)
      }
      warnedMessages.add(message)

      output('warn', `\n${bgYellow` WARN `} ${message}\n`)
    },

    error(...msgs: any[]): void {
      output('error', `\n${bgRed` ERROR `} ${format(msgs)}\n`)
    },

    success(...msgs: any[]): void {
      output('info', `${green`✔`} ${format(msgs)}`)
    },
  }
  return logger
}

export const globalLogger: Logger = createLogger()
