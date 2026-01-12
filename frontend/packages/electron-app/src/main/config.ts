import fs from 'node:fs/promises'

import { nativeImage } from 'electron'
import { parse as parseYAML } from 'yaml'

import appIcon from '../../../../public/icons/icon.ico?asset'

import logger from './log'
import { confPath } from './path'
import type { IConfig } from '../types'

export const APP_ICON_PATH = nativeImage.createFromPath(appIcon)

export const MAIN_WINDOW_LABEL = 'main'

export async function readConfig() {
  try {
    const yamlData = await fs.readFile(confPath, { encoding: 'utf-8' })
    return parseYAML(yamlData) as IConfig
  }
  catch {
    logger.error(`读取配置文件失败`)
    return null
  }
}
