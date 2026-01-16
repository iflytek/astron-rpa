import log from 'electron-log'
import { join } from 'node:path'

import { appWorkPath } from './path'

// 配置 electron-log 的日志文件路径
log.transports.file.resolvePathFn = () => {
  return join(appWorkPath, 'logs', 'main.log')
}

const logger = log

export default logger
