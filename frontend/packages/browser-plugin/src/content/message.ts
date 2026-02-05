import { ASTRON_SW_NAME } from './constant'

function isExtensionContextValid() {
  try {
    return !!(chrome.runtime && chrome.runtime.id)
  }
  catch (error) {
    console.error('Error checking extension context:', error)
    return false
  }
}
function sendToBackground(message) {
  return new Promise((resolve, reject) => {
    if (!isExtensionContextValid()) {
      resolve('Extension context is not valid')
      return
    }
    try {
      chrome.runtime.sendMessage(message, (response) => {
        resolve(response)
      })
    }
    catch (error) {
      reject(error)
    }
  })
}

export function sendElementData(elementData) {
  sendToBackground({
    type: 'element',
    data: elementData,
  })
}

export function requestFrame() {
  return sendToBackground({
    type: 'requestFrameId',
  })
}

export function keepServiceWorkerAlive() {
  const port = chrome.runtime.connect(chrome.runtime.id, { name: ASTRON_SW_NAME })
  port.onDisconnect.addListener(() => {
    sendToBackground({ type: 'keepServiceWorkerAlive' }).then(() => {
      keepServiceWorkerAlive()
    })
  })
}

export function notifyContentLoaded() {
  return sendToBackground({
    type: 'contentLoaded',
  })
}
