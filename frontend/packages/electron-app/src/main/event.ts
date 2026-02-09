import { Buffer } from 'node:buffer'
import fs from 'node:fs/promises'
import { join } from 'node:path'

import { BrowserWindow } from 'electron'
import { clipboard, dialog, globalShortcut, ipcMain, screen, shell } from 'electron'
import throttle from 'lodash/throttle'
import { IPluginConfig } from '@rpa/shared'

import logger from './log'
import { openPath } from './path'
import { getMainWindow, getWindowFromLabel } from './window'
import { checkForUpdates, quitAndInstallUpdates } from './updater'
import { config } from './config'
import { loadExtensions } from './extension'

type MainToRender = (channel: string, msg: string, _win?: BrowserWindow, encode?: boolean) => void

export const mainToRender: MainToRender = throttle<MainToRender>(
  (channel, msg, _win, encode) => {
    const win = _win || getMainWindow()
    const message = encode ? Buffer.from(msg).toString('base64') : msg
    win?.webContents.send(channel, message)
  },
  1000,
  { leading: true, trailing: false },
)

export function listenRender() {
  // window-show
  ipcMain.on('window-show', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.show()
  })
  // window-hide
  ipcMain.on('window-hide', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.hide()
  })
  // window-close
  ipcMain.on('window-close', (event, data) => {
    const { label, confirm = false } = data
    const win = label ? getWindowFromLabel(label) : BrowserWindow.fromWebContents(event.sender)

    if (confirm) {
      // 如果 confirm 为 true，则不关闭窗口
      // 发送一个事件给渲染进程，通知它窗口关闭需要确认
      win?.webContents.send('window-close-confirm', true)
    }
    else {
      win?.close()
    }
  })
  // window-destroy
  ipcMain.on('window-destroy', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.destroy()
  })
  // window-maximize
  ipcMain.handle('window-maximize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.maximize()
    return !!win
  })
  // window-minimize
  ipcMain.handle('window-minimize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.minimize()
    return !!win
  })

  // window-unmaximize
  ipcMain.handle('window-unmaximize', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.unmaximize()
    return !!win
  })
  // window-restore
  ipcMain.handle('window-restore', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.restore()
    win?.focus()
    return !!win
  })

  // window-focus
  ipcMain.handle('window-focus', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.focus()
    return !!win
  })

  // window-set-title
  ipcMain.on('window-set-title', (event, title) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.setTitle(title)
  })

  // window-set-size
  ipcMain.on('window-set-size', (event, width, height) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.setBounds({ width, height })
  })

  // window-set-position
  ipcMain.on('window-set-position', (event, x, y) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.setPosition(Math.floor(x), Math.floor(y))
  })

  // window-set-resizable
  ipcMain.handle('window-set-resizable', (event, resizable) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.setResizable(resizable)
    return !!win
  })

  // window-is-maximized
  ipcMain.handle('window-is-maximized', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    return win ? win.isMaximized() : false
  })

  // window-is-minimized
  ipcMain.handle('window-is-minimized', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    return win ? win.isMinimized() : false
  })

  // window-is-focused
  ipcMain.handle('window-is-focused', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    return win ? win.isFocused() : false
  })

  // window-center
  ipcMain.on('window-center', (event) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.center()
  })

  // window-set-menubar not effective
  ipcMain.on('window-set-titlebar', (event, visible) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.setMenuBarVisibility(visible)
    win?.setAutoHideMenuBar(!visible)
  })

  // window-set-always-on-top
  ipcMain.on('window-set-always-on-top', (event, alwaysOnTop) => {
    const win = BrowserWindow.fromWebContents(event.sender)
    win?.setAlwaysOnTop(alwaysOnTop, 'pop-up-menu')
  })

  // get-workarea
  ipcMain.handle('get-workarea', () => {
    return screen.getPrimaryDisplay().workArea
  })

  ipcMain.on('open-in-browser', (_event, url) => {
    shell.openExternal(url).catch((err: Error) => {
      logger.error('Failed to open URL in browser:', err)
    })
  })

  ipcMain.handle('open-path', (_event, targetPath) => {
    return new Promise((resolve, reject) => {
      openPath(targetPath).then(() => resolve(true)).catch(reject)
    })
  })

  ipcMain.handle('clipboard-write-text', (_event, text) => {
    try {
      clipboard.writeText(text)
      return true
    }
    catch (err) {
      logger.error('Failed to write text to clipboard:', err)
      return false
    }
  })

  ipcMain.handle('clipboard-read-text', (_event) => {
    try {
      const text = clipboard.readText()
      return text
    }
    catch (err) {
      logger.error('Failed to read text from clipboard:', err)
      return ''
    }
  })

  ipcMain.handle('read-file', async (_event, filePath, encoding = 'utf-8') => {
    try {
      return await fs.readFile(filePath, encoding)
    }
    catch (err) {
      logger.error('Failed to read file:', filePath, err)
      throw err
    }
  })

  ipcMain.handle('save-file', async (_event, fileName: string, buffer: Buffer | string): Promise<boolean> => {
    try {
      const { canceled, filePath } = await dialog.showSaveDialog({
        title: '保存文件',
        defaultPath: fileName,
      })

      if (canceled || !filePath)
        return false

      await fs.writeFile(filePath, buffer)
      return true
    }
    catch (err) {
      logger.error('Failed to save file:', fileName, err)
      return false
    }
  })

  ipcMain.handle('path-join', (_event, ...paths) => {
    return new Promise((resolve, reject) => {
      try {
        const joinedPath = join(...paths)
        resolve(joinedPath)
      }
      catch (err) {
        logger.error('Failed to join paths:', paths, err)
        reject(err)
      }
    })
  })

  ipcMain.handle('global-shortcut-register', (_event, shortcut, callback) => {
    return new Promise((resolve, reject) => {
      try {
        const success = globalShortcut.register(shortcut, callback)
        if (success) {
          resolve(true)
        }
        else {
          logger.error(`Failed to register global shortcut: ${shortcut}`)
          resolve(false)
        }
      }
      catch (err) {
        logger.error('Error registering global shortcut:', err)
        reject(err)
      }
    })
  })

  ipcMain.handle('global-shortcut-unregister', (_event, shortcut) => {
    return new Promise((resolve, reject) => {
      try {
        globalShortcut.unregister(shortcut)
        resolve(true)
      }
      catch (err) {
        logger.error('Error unregistering global shortcut:', err)
        reject(err)
      }
    })
  })

  ipcMain.handle('global-shortcut-unregister-all', () => {
    return new Promise((resolve, reject) => {
      try {
        globalShortcut.unregisterAll()
        resolve(true)
      }
      catch (err) {
        logger.error('Error unregistering all global shortcuts:', err)
        reject(err)
      }
    })
  })

  ipcMain.handle('open-dialog', (_event, dialogObj) => {
    return new Promise((resolve, reject) => {
      dialog.showOpenDialog(dialogObj).then((result) => {
        if (result.filePaths.length) {
          resolve(result.filePaths[0])
        }
        else {
          resolve(null)
        }
      }).catch((err) => {
        logger.error('Error showing open dialog:', err)
        reject(err)
      })
    })
  })

  ipcMain.handle('check-for-updates', async () => {
    return await checkForUpdates()
  })

  ipcMain.on('quit-and-install-updates', () => {
    quitAndInstallUpdates()
  })

  ipcMain.handle('get-app-config', () => {
    return config
  })

  ipcMain.handle('get-plugin-list', async (): Promise<IPluginConfig[]> => {
    return loadExtensions()
  })
}
