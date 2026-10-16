import fs from 'node:fs'
import { nativeImage } from 'electron'
import { parse as parseYAML } from 'yaml'
import type { IAppConfig } from '@rpa/shared/platform'

import appIcon from '../../../../public/icons/icon.ico?asset'

import { confPath } from './path'

export const APP_ICON_PATH = nativeImage.createFromPath(appIcon)

export const MAIN_WINDOW_LABEL = 'main'

function loadConfig(): IAppConfig {
  try {
    const yamlData = fs.readFileSync(confPath, { encoding: 'utf-8' });
    return parseYAML(yamlData) as IAppConfig;
  } catch (error) {
    console.error(`FATAL: Failed to load config file at ${confPath}. App cannot start.`, error);
    process.exit(1);
  }
}

export const config = loadConfig();

export function isEngineStartSkipped() {
  return Boolean(config.skip_engine_start || process.env.SKIP_ENGINE_START)
}

export function getSkippedEngineRoutePort() {
  const rawPort = process.env.ENGINE_ROUTE_PORT ?? process.env.ROUTER_PORT ?? '13159'
  const port = Number(rawPort)
  if (!Number.isInteger(port) || port <= 0 || port > 65535)
    throw new Error(`Invalid Engine route port: ${rawPort}`)
  return port
}
