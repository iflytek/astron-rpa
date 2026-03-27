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

contextBridge.exposeInMainWorld('opencodeApi', {
  getRuntimeStatus: () => ipcRenderer.invoke('opencode:getRuntimeStatus'),
  awaitInitialization: () => ipcRenderer.invoke('opencode:awaitInitialization'),
  getBootstrap: () => ipcRenderer.invoke('opencode:getBootstrap'),
  getSession: (sessionId: string) => ipcRenderer.invoke('opencode:getSession', sessionId),
  createSession: (payload: { title?: string | null; assistantId?: string | null; groupRoomId?: string | null }) => ipcRenderer.invoke('opencode:createSession', payload),
  deleteSession: (sessionId: string) => ipcRenderer.invoke('opencode:deleteSession', sessionId),
  sendMessage: (payload: { sessionID: string; text: string; model?: string | null; providerId?: string | null }) =>
    ipcRenderer.invoke('opencode:sendMessage', payload),
  getSettings: () => ipcRenderer.invoke('opencode:getSettings'),
  saveProvider: (input: unknown) => ipcRenderer.invoke('opencode:saveProvider', input),
  saveDefaultModel: (input: unknown) => ipcRenderer.invoke('opencode:saveDefaultModel', input),
  listAssistants: () => ipcRenderer.invoke('opencode:listAssistants'),
  saveAssistant: (input: unknown) => ipcRenderer.invoke('opencode:saveAssistant', input),
  deleteAssistant: (id: string) => ipcRenderer.invoke('opencode:deleteAssistant', id),
  listGroupRooms: () => ipcRenderer.invoke('opencode:listGroupRooms'),
  saveGroupRoom: (input: unknown) => ipcRenderer.invoke('opencode:saveGroupRoom', input),
  deleteGroupRoom: (id: string) => ipcRenderer.invoke('opencode:deleteGroupRoom', id),
  listSkills: () => ipcRenderer.invoke('opencode:listSkills'),
  onRuntimeEvent: (listener: (event: unknown) => void) => {
    const handler = (_: Electron.IpcRendererEvent, event: unknown) => listener(event)
    ipcRenderer.on('opencode:runtimeEvent', handler)
    return () => ipcRenderer.off('opencode:runtimeEvent', handler)
  },
})
