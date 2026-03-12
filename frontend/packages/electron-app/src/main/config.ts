import fs from 'node:fs'
import path from 'node:path'

import { app, nativeImage } from 'electron'
import { parse as parseYAML } from 'yaml'
import type { IAppConfig, UserSetting } from '@rpa/shared/platform'
import { get } from 'lodash'

import appIcon from '../../../../public/icons/icon.ico?asset'

import { confPath, settingPath, resourcePath } from './path'

export const electronInfo = {
  electronVersion: process.versions.electron,
  appPath: app.getPath('exe'),
  userDataPath: app.getPath('userData'),
  appVersion: app.getVersion(),
  release: process.getSystemVersion(),
  arch: process.arch,
  platform: process.platform,
  preload: path.join(__dirname, '../preload/index.js'),
  resourcePath,
}

export const APP_ICON_PATH = nativeImage.createFromPath(appIcon)

export const MAIN_WINDOW_LABEL = 'main'

export async function loadSetting(): Promise<UserSetting> {
  try {
    const jsonData = await fs.promises.readFile(settingPath, { encoding: 'utf-8' });
    let setting = JSON.parse(jsonData) as UserSetting;

    const version = get(setting, 'version')
    const platform = get(setting, 'platform')

    if (version !== electronInfo.appVersion || platform !== electronInfo.platform) {
      setting = {
        ...setting,
        version: electronInfo.appVersion,
        platform: electronInfo.platform,
      }
      saveSetting(setting)
    }

    return setting;
  } catch (error) {
    console.error(`FATAL: Failed to load setting file at ${settingPath}. App cannot start.`, error);
    return {} as UserSetting;
  }
}

export async function saveSetting(setting: UserSetting): Promise<void> {
  try {
    await fs.promises.writeFile(settingPath, JSON.stringify(setting));
  } catch (error) {
    console.error(`FATAL: Failed to save setting file at ${settingPath}. App cannot start.`, error);
  }
}

function loadConfig(): IAppConfig {
  try {
    const yamlData = fs.readFileSync(confPath, { encoding: 'utf-8' });
    return parseYAML(yamlData) as IAppConfig;
  } catch (error) {
    console.error(`FATAL: Failed to load config file at ${confPath}. App cannot start.`, error);
    process.exit(1);
  }
}

loadSetting()

export const config = loadConfig();
