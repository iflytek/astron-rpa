import fs from 'node:fs/promises'

import { nativeImage } from 'electron'

import appIcon from '../../../../public/icons/icon.ico?asset'

import logger from './log'
import { confPath } from './path'

export const APP_ICON_PATH = nativeImage.createFromPath(appIcon)

export const MAIN_WINDOW_LABEL = 'main'

export async function readConfig() {
  const data = await fs.readFile(confPath, { encoding: 'utf-8' })
  try {
    const json = JSON.parse(data)
    return json
  }
  catch {
    logger.error(`读取配置文件失败`)
    return null
  }
}
