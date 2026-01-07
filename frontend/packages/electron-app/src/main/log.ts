import fs from 'node:fs/promises'
import { join } from 'node:path'

import { appWorkPath } from './path'

const logPath = join(appWorkPath, 'logs')
fs.mkdir(logPath, { recursive: true })
const today = new Date().toLocaleDateString().replaceAll('/', '-')
const logFile = join(logPath, `main-${today}.log`)

const logger = {
  info: (...args: any[]) => {
    console.log('INFO:', ...args)
    fs.writeFile(logFile, `${new Date().toLocaleString()} INFO: ${args}\n`, { flag: 'a' })
  },
  warn: (...args: any[]) => {
    console.warn('WARN:', ...args)
    fs.writeFile(logFile, `${new Date().toLocaleString()} WARN: ${args}\n`, { flag: 'a' })
  },
  error: (...args: any[]) => {
    console.error('ERROR:', ...args)
    fs.writeFile(logFile, `${new Date().toLocaleString()} ERROR: ${args}\n`, { flag: 'a' })
  },
}

export default logger
