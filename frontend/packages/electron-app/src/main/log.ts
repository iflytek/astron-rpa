import fs from 'node:fs/promises'
import { join } from 'node:path'

import { userDataPath } from './path'

const logPath = join(userDataPath, 'logs')
fs.mkdir(logPath, { recursive: true })
const today = new Date().toLocaleDateString().replaceAll('/', '-')
const logFile = join(logPath, `main_${today}.log`)

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
