import path from 'node:path'

import { app, BrowserWindow, screen } from 'electron'

import type { WindowOptions } from '../types'

import { APP_ICON_PATH, MAIN_WINDOW_LABEL } from './config'
import { resourcePath } from './path'
import logger from './log'

export const WindowStack: Map<string, number> = new Map()

export function getWindow(label: string, id?: number) {
  const winId = id ?? WindowStack.get(label)
  return winId ? BrowserWindow.fromId(winId) : null
}

export function getMainWindow() {
  return getWindow(MAIN_WINDOW_LABEL)
}

export function electronInfo(win: BrowserWindow) {
  const electronVersion = process.versions.electron
  const electronInfo = JSON.stringify({
    electronVersion,
    appPath: app.getPath('exe'),
    userDataPath: app.getPath('userData'),
    appVersion: app.getVersion(),
    release: process.getSystemVersion(),
    arch: process.arch,
    platform: process.platform,
    preload: path.join(__dirname, '../preload/index.js'),
    resourcePath,
  })
  win.webContents.send('electron-info', electronInfo)
}

function createWindow(options: Electron.BrowserWindowConstructorOptions, label?: string) {
  const win = new BrowserWindow(options)

  if (label) {
    WindowStack.set(label, win.id)
  }

  return win
}

export function createMainWindow() {
  const mainWindowOptions: Electron.BrowserWindowConstructorOptions = {
    title: 'iflyrpa',
    autoHideMenuBar: true,
    titleBarStyle: 'hidden',
    width: 1280,
    height: 750,
    icon: APP_ICON_PATH,
    resizable: true,
    center: true,
    show: false,
    frame: false,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
    },
  }

  return createWindow(mainWindowOptions, MAIN_WINDOW_LABEL)
}

export function createSubWindow(options: WindowOptions) {
  logger.info('createSubWindow', JSON.stringify(options))
  const { width = 800, height = 600, name = 'SubWindow', url, position = 'center' } = options

  const display = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = display.workAreaSize

  let x: number
  let y: number

  switch (position) {
    case 'left_top':
      x = 2
      y = 2
      break
    case 'right_top':
      x = screenWidth - width - 2
      y = 2
      break
    case 'left_bottom':
      x = 2
      y = screenHeight - height - 2
      break
    case 'right_bottom':
      x = screenWidth - width - 2
      y = screenHeight - height - 2
      break
    case 'top_center':
      x = Math.round((screenWidth - width) / 2)
      y = 2
      break
    case 'center':
    default:
      x = Math.round((screenWidth - width) / 2)
      y = Math.round((screenHeight - height) / 2)
      break
  }

  const subWindowOptions: Electron.BrowserWindowConstructorOptions = {
    ...options,
    x,
    y,
    width,
    height,
    title: name,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
    },
    icon: APP_ICON_PATH,
    frame: false,
  }

  const window = createWindow(subWindowOptions, options.label)
  window.loadURL(url).then(() => electronInfo(window)).catch(() => logger.error('Failed to load URL'))
  window.on('ready-to-show', () => {
    if (options?.visible !== false) {
      window.show()
    }
    window.focus()
  })

  return window
}
