import fs from 'node:fs'
import { nativeImage } from 'electron'
import { parse as parseYAML } from 'yaml'

import appIcon from '../../../../public/icons/icon.ico?asset'

import { confPath } from './path'
import type { IConfig } from '../types'

export const APP_ICON_PATH = nativeImage.createFromPath(appIcon)

export const MAIN_WINDOW_LABEL = 'main'

const yamlData = fs.readFileSync(confPath, { encoding: 'utf-8' })
export const config = parseYAML(yamlData) as IConfig
