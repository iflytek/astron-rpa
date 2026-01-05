import { app, BrowserWindow, ipcMain, session } from 'electron'

import type { W2WType, WindowOptions } from '../types'

import { envJson } from './env'
import { listenRender } from './event'
import logger from './log'
import { notFoundPath } from './path'
import { checkPythonRpaProcess, startBackend } from './server'
import { changeTray, createTray } from './tray'
import { createSubWindow, createMainWindow as createWindow, electronInfo, getMainWindow, WindowStack } from './window'

const isPackaged = app.isPackaged
const startTime = Date.now()
globalThis.MainWindowLoaded = false

app.commandLine.appendSwitch('ignore-certificate-errors')
app.commandLine.appendSwitch('disable-web-security')
app.disableHardwareAcceleration()

function createMainWindow(options?: any) {
  const mainWindow = createWindow(options)
  const url = isPackaged ? envJson.APP_URL : envJson.DEV_URL
  logger.info(`app load url: ${url}`)
  mainWindow.loadURL(url).then(() => electronInfo(mainWindow)).catch(() => mainWindow.loadFile(notFoundPath))
  mainWindow.once('ready-to-show', () => {
    WindowStack.set('main', mainWindow.id)
    mainWindow.show()
    logger.info(`app show: ${`${Date.now() - startTime}ms`}`)
  })
  mainWindow.on('close', () => {
    if (process.platform !== 'darwin') {
      app.quit()
    }
    else {
      app.exit()
    }
  })
  createTray(mainWindow)
}

function sessionHanlder() {
  let setCookieKey = ''
  let jsessionIdValue = ''
  const pattern = /jwt=(.*?);/i
  session.defaultSession.webRequest.onHeadersReceived(
    {
      urls: envJson.REQUEST_WHITE_URL,
    },
    (details, callback) => {
      if (details.responseHeaders && details.responseHeaders['Set-Cookie']) {
        setCookieKey = 'Set-Cookie'
      }
      else {
        setCookieKey = 'set-cookie'
      }
      if (details.responseHeaders && details.responseHeaders[setCookieKey] && details.responseHeaders[setCookieKey].length) {
        for (let i = 0; i < details.responseHeaders[setCookieKey].length; i++) {
          details.responseHeaders[setCookieKey][i] += '; SameSite=None; Secure'
          const match = details.responseHeaders[setCookieKey][i].match(pattern)
          const val = match && match[1]
          jsessionIdValue = val || ''
        }
      }
      callback({ responseHeaders: details.responseHeaders })
    },
  )
  session.defaultSession.webRequest.onBeforeSendHeaders(
    {
      urls: envJson.REQUEST_WHITE_URL,
    },
    (details, callback) => {
      const headers = details.requestHeaders
      headers.Cookie = `jwt=${jsessionIdValue};`
      callback({ cancel: false, requestHeaders: headers })
    },
  )
}

function argsOptions(args) {
  const options: WindowOptions = { url: '' }
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    if (arg.startsWith('--url=')) {
      options.url = arg.split('--url=')[1] || ''
    }
    if (arg.startsWith('--width=')) {
      options.width = Number.parseInt(arg.split('--width=')[1] || '800')
    }
    if (arg.startsWith('--height=')) {
      options.height = Number.parseInt(arg.split('--height=')[1] || '600')
    }
    if (arg.startsWith('--pos=')) {
      options.position = arg.split('--pos=')[1] || 'center'
    }
    if (arg.startsWith('--top=')) {
      options.top = arg.split('--top=')[1] === 'true'
    }
  }
  return options
}

async function ready() {
  logger.info('app ready')
  await checkProcess()
  sessionHanlder()
  listenRender()
  // 获取命令行启动参数
  const commandArgs = process.argv
  logger.info('commandArgs', JSON.stringify(commandArgs))
  if (commandArgs.find(i => i.startsWith('--url='))) {
    const options = argsOptions(commandArgs)
    createSubWindow(options)
  }
  else {
    createMainWindow()
  }
}

async function checkProcess() {
  const isRunning = await checkPythonRpaProcess()
  if (isRunning) {
    logger.warn(`Another python setup is already running.`)
    app.quit()
  }
  else {
    logger.info(`No other python setup found.`)
  }
}

const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
}
else {
  app.on('second-instance', (_event, argv, _workingDirectory, _additionalData) => {
    logger.info('second-instance', JSON.stringify(argv))
    if (argv.find(i => i.startsWith('--url='))) { // 第二次打开携带参数，新建窗口
      const options = argsOptions(argv)
      createSubWindow(options)
    }
    else {
      const mainWindow = getMainWindow()
      if (mainWindow?.isMinimized()) {
        mainWindow?.restore()
      }
      mainWindow?.focus()
    }
  })
  // 在Electron完成初始化时被触发
  app.whenReady().then(ready).catch((err) => {
    logger.error('app ready error', err.toString())
  })
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
  else {
    app.quit()
  }
})
ipcMain.handle('ipcCreateWindow', (event, options) => {
  const local_win = createSubWindow(options)
  const id = local_win.id
  const mainWindow = getMainWindow()
  local_win.once('close', () => {
    mainWindow?.webContents.send('window-close', id)
    WindowStack.delete(options.label)
  })
  return id
})
ipcMain.handle('w2w', (_event, arg: W2WType) => {
  logger.info('w2w', JSON.stringify(arg))
  const { target } = arg
  const targetWinId = WindowStack.get(target)
  const targetWin = BrowserWindow.fromId(targetWinId || 1)
  targetWin?.webContents.send('w2w', arg)
  return true
})
ipcMain.handle('main_window_onload', (_event) => {
  if (globalThis.MainWindowLoaded)
    return true
  startBackend()
  globalThis.MainWindowLoaded = true
  return true
})
ipcMain.handle('tray_change', (_event, { mode, status }) => {
  const mainWindow = getMainWindow()
  mainWindow && changeTray(mainWindow, mode, status)
})
