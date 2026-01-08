import { Buffer } from 'node:buffer'
import fs from 'node:fs'
import { join } from 'node:path'

import type { BrowserWindow } from 'electron'
import { clipboard, dialog, globalShortcut, ipcMain, screen, shell } from 'electron'
import throttle from 'lodash/throttle'

import logger from './log'
import { openPath } from './path'
import { getMainWindow, getWindow } from './window'
import { checkForUpdates, quitAndInstallUpdates } from './updater'

type MainToRender = (channel: string, msg: string, _win?: BrowserWindow, encode?: boolean) => void

export const mainToRender: MainToRender = throttle<MainToRender>(
  (channel, msg, _win, encode) => {
    const win = _win || getMainWindow()
    if (encode)
      msg = Buffer.from(msg).toString('base64')
    win?.webContents.send(channel, msg)
  },
  1000,
  { leading: true, trailing: false },
)

export function listenRender() {
  // window-show
  ipcMain.on('window-show', (_event) => {
    const win = getWindow('', _event.sender.id)
    win?.show()
    win?.focus()
  })
  // window-hide
  ipcMain.on('window-hide', (_event) => {
    const win = getWindow('', _event.sender.id)
    win?.hide()
  })
  // window-close
  ipcMain.on('window-close', (_event, data) => {
    const { label = 'main', confirm = false } = data
    const win = getWindow(label)

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
  ipcMain.on('window-destroy', (_event) => {
    const win = getWindow('', _event.sender.id)
    win?.destroy()
  })
  // window-maximize
  ipcMain.handle('window-maximize', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.maximize()
      return true
    }
    return false
  })
  // window-minimize
  ipcMain.handle('window-minimize', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.minimize()
      return true
    }
    return false
  })

  // window-unmaximize
  ipcMain.handle('window-unmaximize', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.unmaximize()
      return true
    }
    return false
  })
  // window-restore
  ipcMain.handle('window-restore', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.restore()
      win.focus()
      return true
    }
    return false
  })

  // window-focus
  ipcMain.handle('window-focus', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.focus()
      return true
    }
    return false
  })

  // window-set-title
  ipcMain.on('window-set-title', (_event, title) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.setTitle(title)
    }
  })

  // window-set-size
  ipcMain.on('window-set-size', (_event, width, height) => {
    const win = getWindow('', _event.sender.id)
    win?.setBounds({ width, height })
  })

  // window-set-position
  ipcMain.on('window-set-position', (_event, x, y) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.setPosition(Math.floor(x), Math.floor(y))
    }
  })

  // window-set-resizable
  ipcMain.handle('window-set-resizable', (_event, resizable) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.setResizable(resizable)
      return true
    }
    return false
  })

  // window-is-maximized
  ipcMain.handle('window-is-maximized', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      return win.isMaximized()
    }
    return false
  })

  // window-is-minimized
  ipcMain.handle('window-is-minimized', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      return win.isMinimized()
    }
    return false
  })

  // window-is-focused
  ipcMain.handle('window-is-focused', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      return win.isFocused()
    }
    return false
  })

  // window-center
  ipcMain.on('window-center', (_event) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.center()
    }
  })

  // window-set-menubar not effective
  ipcMain.on('window-set-titlebar', (_event, visible) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.setMenuBarVisibility(visible)
      win.setAutoHideMenuBar(!visible)
    }
  })
  // window-set-always-on-top
  ipcMain.on('window-set-always-on-top', (_event, alwaysOnTop) => {
    const win = getWindow('', _event.sender.id)
    if (win) {
      win.setAlwaysOnTop(alwaysOnTop, 'pop-up-menu')
    }
  })

  // get-workarea
  ipcMain.handle('get-workarea', () => {
    const workArea = screen.getPrimaryDisplay().workArea
    return workArea
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

  ipcMain.handle('read-file', (_event, filePath) => {
    try {
      return fs.readFileSync(filePath, 'utf-8')
    }
    catch (err) {
      logger.error('Failed to read file:', filePath, err)
      throw err
    }
  })

  ipcMain.handle('save-file', async (_event, fileName: string, buffer: Buffer) => {
    try {
      const { canceled, filePath } = await dialog.showSaveDialog({
        title: '保存文件',
        defaultPath: fileName,
      })

      if (canceled || !filePath)
        return false

      fs.writeFileSync(filePath, buffer)
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
}
