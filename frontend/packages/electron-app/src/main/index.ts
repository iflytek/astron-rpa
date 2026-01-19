import { app, ipcMain, protocol, session } from 'electron'
import path from 'node:path'

import type { W2WType } from '../types'

import logger from './log'
import { envJson } from './env'
import { listenRender } from './event'
import { checkPythonRpaProcess, startBackend } from './server'
import { changeTray, createTray } from './tray'
import { createSubWindow, createMainWindow as createWindow, electronInfo, getWindowFromLabel, getMainWindow, WindowStack } from './window'
import { rendererPath, windowBaseUrl } from './path'

const startTime = Date.now()
globalThis.MainWindowLoaded = false

app.commandLine.appendSwitch('ignore-certificate-errors')
app.commandLine.appendSwitch('disable-web-security')
app.disableHardwareAcceleration()
/**
 * 把 rpa 协议注册为“特权协议”，赋予 standard 和 secure 等权限
 * 使其拥有完整的浏览器上下文（localStorage、fetch、ServiceWorker 等）。
 */
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'rpa',
    privileges: {
      secure: true,
      standard: true,
      supportFetchAPI: true,
      corsEnabled: true,
      allowServiceWorkers: true,
    },
  },
])

function createMainWindow() {
  const mainWindow = createWindow()
  const url = windowBaseUrl + 'boot.html'
  logger.info(`app load url: ${url}`)

  mainWindow.loadURL(url).then(() => electronInfo(mainWindow)).catch(() => logger.error('Failed to load URL'))
  mainWindow.once('ready-to-show', () => {
    WindowStack.set('main', mainWindow)
    mainWindow.show()
    logger.info(`app show: ${`${Date.now() - startTime}ms`}`)
  })
  mainWindow.on('close', () => {
    process.platform !== 'darwin' ? app.quit() : app.exit()
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

function registerRpaProtocol() {
  // 注册自定义协议 rpa://localhost/boot.html 映射到本地 rendererPath/boot.html
  protocol.registerFileProtocol('rpa', (request, callback) => {
    try {
      const u = new URL(request.url)
      const filePath = path.join(rendererPath, u.pathname)
      callback({ path: filePath })
    }
    catch (err) {
      logger.error('rpa protocol file resolve error:', err)
    }
  })
}

async function ready() {
  logger.info('app ready')
  await checkProcess()
  sessionHanlder()
  registerRpaProtocol()
  listenRender()
  createMainWindow()
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
  app.on('second-instance', () => {
    // 聚焦到已有窗口
    const mainWindow = getMainWindow()
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  });
  // 在Electron完成初始化时被触发
  app.whenReady().then(ready).catch((err) => {
    logger.error('app ready error', err.toString())
  })
}

app.on('window-all-closed', () => {
  app.quit()
})

ipcMain.handle('ipcCreateWindow', (_event, options) => {
  const local_win = createSubWindow(options)
  const id = local_win.id
  const mainWindow = getMainWindow()
  local_win.once('close', () => {
    mainWindow?.webContents.send('window-close', id)
    options.label && WindowStack.delete(options.label)
  })
  return id
})

ipcMain.handle('w2w', (_event, arg: W2WType) => {
  logger.info('w2w', JSON.stringify(arg))
  const targetWin = getWindowFromLabel(arg.target) || getMainWindow()
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
