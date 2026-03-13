import { log } from './3rd/log'
import { createWsApp } from './3rd/rpa_websocket'
import { bgHandler, contentMessageHandler } from './background/backgroundInject'
import { connectToNativeHost } from './background/native'
import { BROWSER_MAP, IGNORE_LOG_KEYS, OLD_EXTENSION_IDS } from './common/constant'

let wsApp: any = null
let connectedTimestamp: number = 0

function getAllTabs() {
  return new Promise<chrome.tabs.Tab[]>((resolve) => {
    chrome.tabs.query({}, (tabs) => {
      resolve(tabs)
    })
  })
}

function reloadAllTabs() {
  getAllTabs().then((tabs: chrome.tabs.Tab[]) => {
    for (const tab of tabs) {
      chrome.tabs.reload(tab.id)
    }
  })
}

function getInstalledExtensions() {
  return new Promise<chrome.management.ExtensionInfo[]>((resolve) => {
    chrome.management.getAll((exts: chrome.management.ExtensionInfo[]) => {
      resolve(exts)
    })
  })
}

function disableOldExtensions() {
  getInstalledExtensions().then((exts: chrome.management.ExtensionInfo[]) => {
    exts.forEach((ext) => {
      if (OLD_EXTENSION_IDS.includes(ext.id) && ext.enabled) {
        chrome.management.setEnabled(ext.id, false)
      }
    })
  })
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  contentMessageHandler(request, sender, sendResponse)
  return true
})
chrome.runtime.onInstalled.addListener(() => {
  reloadAllTabs()
  disableOldExtensions()
  chrome.alarms.create('weakAlarm', { delayInMinutes: 1, periodInMinutes: 1 })
})
chrome.runtime.onStartup.addListener(() => {
  reloadAllTabs()
})
chrome.management.onEnabled.addListener((info) => {
  if (info.id === chrome.runtime.id) {
    reloadAllTabs()
    disableOldExtensions()
    chrome.alarms.create('weakAlarm', { delayInMinutes: 1, periodInMinutes: 1 })
  }
})
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'weakAlarm') {
    log.info('Alive alarm triggered')
  }
})
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === 'Astron-Service-Worker') {
    const now = Date.now()
    const last = connectedTimestamp
    if (now - last > 10000) {
      log.info('Astron-Service-Worker connected')
      connectedTimestamp = now
    }
  }
})

async function connectToWebsocket(pipeName = '') {
  const agent = BROWSER_MAP[pipeName] || pipeName
  log.info(`Pipe name: ${pipeName}, Agent: ${agent}`)
  if (wsApp) {
    log.info('WebSocket already connected, closing existing connection')
    wsApp.close()
  }
  wsApp = await createWsApp(agent)
  wsApp.start()
  wsApp.event('browser', '', (msg) => {
    const newMsg = msg.to_reply()
    wsHandler(msg).then((result) => {
      newMsg.data = result
      wsApp.send(newMsg)
    })
  })
}

async function wsHandler(message) {
  const msgObject = typeof message === 'string' ? JSON.parse(message) : message
  if (!IGNORE_LOG_KEYS.includes(msgObject.key)) {
    log.info(msgObject.key, msgObject)
    // log.time(msgObject.key)
  }
  const result = await bgHandler(msgObject)
  if (!IGNORE_LOG_KEYS.includes(msgObject.key)) {
    // log.timeEnd(msgObject.key)
    log.info(msgObject.key, result)
  }
  return result
}

; (function () {
  connectToWebsocket()
  try {
    const port = connectToNativeHost()
    if (port) {
      port.postMessage({ type: 'ASTRON_GET_IPC_KEY', data: Date.now() })
      port.onMessage.addListener((message) => {
        log.info('Received message from native host:', message)
        if (message?.type === 'ASTRON_GET_IPC_KEY' && message?.data) {
          const pipeName = message.data.split('_')[1].toLowerCase()
          connectToWebsocket(pipeName)
        }
        if (message?.type === 'ASTRON_IPC_START') {
          port.postMessage({ type: 'ASTRON_IPC_STARTED', data: Date.now() })
        }
        if (message?.type === 'ASTRON_IPC_PING') {
          port.postMessage({ type: 'ASTRON_IPC_PONG', data: Date.now() })
        }
      })
    }
  }
  catch (error) {
    log.error('Error connecting to native host:', error)
  }
})()
