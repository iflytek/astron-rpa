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
  openclaw: {
    getToken: async () => {
      try {
        const token = await ipcRenderer.invoke('get_openclaw_token')
        return token
      } catch (err) {
        console.error('Failed to get OpenClaw token:', err)
        return undefined
      }
    },
    getDeviceIdentity: async () => {
      try {
        return await ipcRenderer.invoke('get_openclaw_device_identity')
      } catch (err) {
        console.error('Failed to get OpenClaw device identity:', err)
        return undefined
      }
    },
    signDevicePayload: async (payload: string) => {
      try {
        return await ipcRenderer.invoke('sign_openclaw_device_payload', payload)
      } catch (err) {
        console.error('Failed to sign OpenClaw device payload:', err)
        return undefined
      }
    },
    getDeviceToken: async (role = 'operator') => {
      try {
        return await ipcRenderer.invoke('get_openclaw_device_token', role)
      } catch (err) {
        console.error('Failed to get OpenClaw device token:', err)
        return undefined
      }
    },
    storeDeviceToken: async (params: { role?: string, token: string, scopes?: string[] }) => {
      try {
        await ipcRenderer.invoke('store_openclaw_device_token', params)
        return true
      } catch (err) {
        console.error('Failed to store OpenClaw device token:', err)
        return false
      }
    },
    approveDeviceRequest: async (requestId: string) => {
      try {
        await ipcRenderer.invoke('approve_openclaw_device_request', requestId)
        return true
      } catch (err) {
        console.error('Failed to approve OpenClaw device request:', err)
        return false
      }
    },
    chatCompletions: async (params: {
      messages: Array<{ role: 'system' | 'developer' | 'user' | 'assistant' | 'tool', content: string }>
      sessionKey?: string
      attachments?: Array<{ type: 'image', mimeType: string, fileName?: string, content: string }>
      allowCliFallback?: boolean
    }) => {
      try {
        return await ipcRenderer.invoke('openclaw_chat_completion', params)
      } catch (err) {
        console.error('Failed to request OpenClaw chat completion:', err)
        throw err
      }
    },
    readLocalFile: async (params: { path: string, mode: 'text' | 'data-url' }) => {
      try {
        return await ipcRenderer.invoke('openclaw_read_local_file', params)
      } catch (err) {
        console.error('Failed to read local file for OpenClaw:', err)
        return undefined
      }
    },
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
