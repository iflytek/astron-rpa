import { contextBridge, ipcRenderer } from 'electron'

ipcRenderer.on('electron-info', (ev, data) => {
  localStorage.setItem('electron', data)
})

contextBridge.exposeInMainWorld('electron', {
  ipcRenderer: {
    invoke: ipcRenderer.invoke.bind(ipcRenderer),
    send: ipcRenderer.send.bind(ipcRenderer),
    sendTo: ipcRenderer.sendTo.bind(ipcRenderer),
    on: ipcRenderer.on.bind(ipcRenderer),
    off: ipcRenderer.off.bind(ipcRenderer),
  },
  globalShortcut: {
    register: (shortcut: string, callback: () => void) => {
      return ipcRenderer
        .invoke('global-shortcut-register', shortcut, callback)
        .then(() => true)
        .catch((err: Error) => {
          console.error('Failed to register global shortcut:', err)
          return false
        })
    },
    unregister: (shortcut: string) => {
      return ipcRenderer
        .invoke('global-shortcut-unregister', shortcut)
        .then(() => true)
        .catch((err: Error) => {
          console.error('Failed to unregister global shortcut:', err)
          return false
        })
    },
    unregisterAll: () => {
      return ipcRenderer
        .invoke('global-shortcut-unregister-all')
        .then(() => true)
        .catch((err: Error) => {
          console.error('Failed to unregister all global shortcuts:', err)
          return false
        })
    },
  },
  clipboard: {
    readText: async () => {
      const text = await ipcRenderer.invoke('clipboard-read-text')
      return text
    },
    writeText: (text: string) => {
      return ipcRenderer
        .invoke('clipboard-write-text', text)
        .then(() => true)
        .catch((err: Error) => {
          console.error('Failed to write text to clipboard:', err)
          return false
        })
    },
  },
})
