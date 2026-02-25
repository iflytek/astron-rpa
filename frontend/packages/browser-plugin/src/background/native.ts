import { log } from '../3rd/log'

/**
 * @file Manages communication with the native messaging host.
 */
import { NATIVE_HOST_NAME } from './constant'

let port: chrome.runtime.Port | null = null

/**
 * Establishes a connection to the native messaging host.
 */
function connectToNativeHost() {
  if (port) {
    log.info('Already connected to native host.')
    return
  }

  log.info(`Connecting to native host: ${NATIVE_HOST_NAME}`)
  try {
    port = chrome.runtime.connectNative(NATIVE_HOST_NAME)

    port.onMessage.addListener((message) => {
      log.info('Received message from native host:', message)
      // Handle incoming messages from the native host here
    })

    port.onDisconnect.addListener(() => {
      if (chrome.runtime.lastError) {
        log.error('Native host disconnected with error:', chrome.runtime.lastError.message)
      }
      else {
        log.info('Native host disconnected.')
      }
      port = null
    })
  }
  catch (error) {
    log.error('Failed to connect to native host:', error)
    port = null
  }
}

/**
 * Sends a message to the native messaging host.
 * @param message The message object to send.
 */
export function sendNativeMessage(message: object) {
  if (!port) {
    log.warn('Not connected to native host. Attempting to connect...')
    connectToNativeHost()
    if (!port) {
      log.error('Failed to send message: Connection to native host not established.')
      return
    }
  }

  try {
    log.info('Sending message to native host:', message)
    port.postMessage(message)
  }
  catch (error) {
    log.error('Error sending message to native host:', error)
  }
}

/**
 * Disconnects from the native messaging host.
 */
export function disconnectFromNativeHost() {
  if (port) {
    log.info('Disconnecting from native host.')
    port.disconnect()
    port = null
  }
}
/**
 * Sends periodic heartbeat messages to keep the native host connection alive.
 */
export function nativeMessageHeartbeat() {
  const t = setTimeout(() => {
    if (port) {
      sendNativeMessage({ type: 'heartbeat', timestamp: Date.now() })
      clearTimeout(t)
      nativeMessageHeartbeat()
    }
  }, 10 * 1000)
}

// Automatically connect when the background script starts.
connectToNativeHost()
