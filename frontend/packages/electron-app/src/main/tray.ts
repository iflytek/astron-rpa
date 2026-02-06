import type { BrowserWindow } from 'electron'
import { app, dialog, Menu, Tray } from 'electron'

import { APP_ICON_PATH } from './config'

let tray: Tray
let scheduling_mode = false

export function createTray(win: BrowserWindow) {
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示',
      click: () => {
        win.show()
        if (win.isMinimized())
          win.restore()
        win.focus()
      },
    },
    {
      label: '隐藏',
      click: () => {
        win.hide()
      },
    },
    {
      label: '退出',
      click: () => {
        app.quit()
      },
    },
  ])
  tray = new Tray(APP_ICON_PATH)
  tray.setContextMenu(contextMenu)
  tray.on('click', () => {
    if (!win)
      return
    if (scheduling_mode)
      return
    if (!win.isVisible()) {
      win.show()
      win.focus()
    }
    else if (win.isMinimized()) {
      win.restore()
      win.focus()
    }
    else {
      win.minimize()
    }
  })
  tray.setToolTip(app.name)
}

export function changeTray(win: BrowserWindow, mode: 'scheduling' | 'normal', status?: 'idle' | 'busy') {
  let options: Electron.MenuItemConstructorOptions[] = []
  scheduling_mode = mode === 'scheduling'
  if (mode === 'normal') {
    options = [
      {
        label: '显示',
        click: () => {
          win.show()
          if (win.isMinimized())
            win.restore()
          win.focus()
        },
      },
      {
        label: '隐藏',
        click: () => {
          win.hide()
        },
      },
      {
        label: '退出',
        click: () => {
          app.quit()
        },
      },
    ]
  }
  if (mode === 'scheduling') {
    options = [
      {
        label: status === 'busy' ? '调度模式（运行中）' : '调度模式（空闲）',
        click: () => {},
      },
    ]
    if (status === 'busy') {
      options.push({
        label: '中止当前任务',
        click: () => {
          dialog.showMessageBox(win, {
            type: 'warning',
            title: '中止任务',
            message: '是否确认中止当前任务？',
            buttons: ['确定', '取消'],
            defaultId: 0,
            cancelId: 1,
            noLink: true,
          }).then((result) => {
            if (result.response === 0) {
              changeTray(win, 'scheduling', 'idle')
              win.webContents.send('stop_task', {})
            }
          })
        },
      })
    }
    options = options.concat([
      {
        label: '退出调度模式',
        click: () => {
          dialog.showMessageBox(win, {
            type: 'warning',
            title: '退出调度模式',
            message: '退出后控制台无法下发任务到本机，当前的调度任务同时取消，请确认。',
            buttons: ['确定', '取消'],
            defaultId: 0,
            cancelId: 1,
            noLink: true,
          }).then((result) => {
            if (result.response === 0) {
              changeTray(win, 'normal')// 改变托盘菜单
              win.webContents.send('exit_scheduling_mode', {}) // 退出调度模式通知引擎
              win.show() // 显示主界面
            }
          })
        },
      },
      {
        label: '退出星火数字员工',
        click: () => {
          app.quit()
        },
      },
    ])
  }
  const contextMenu = Menu.buildFromTemplate(options)
  tray.setContextMenu(contextMenu)
}
