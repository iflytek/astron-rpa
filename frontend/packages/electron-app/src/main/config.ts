import fs from 'node:fs'
import { nativeImage } from 'electron'
import { parse as parseYAML } from 'yaml'

import appIcon from '../../../../public/icons/icon.ico?asset'

import { confPath } from './path'
import type { IConfig } from '../types'

export const APP_ICON_PATH = nativeImage.createFromPath(appIcon)

export const MAIN_WINDOW_LABEL = 'main'

function loadConfig(): IConfig {
  try {
    const yamlData = fs.readFileSync(confPath, { encoding: 'utf-8' });
    return parseYAML(yamlData) as IConfig;
  } catch (error) {
    console.error(`FATAL: Failed to load config file at ${confPath}. App cannot start.`, error);
    process.exit(1);
  }
}

export const config = loadConfig();
