import { log } from '../3rd/log'
/**
 * @file Manages communication with the native messaging host.
 */
import { NATIVE_HOST_NAME } from '../common/constant'
import { Utils } from '../common/utils'

let port: chrome.runtime.Port | null = null
const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$'
/**
 * Establishes a connection to the native messaging host.
 */
export function connectToNativeHost() {
  if (isFirefox) {
    log.info('Firefox does not connect to native host.')
    return
  }
  if (port) {
    log.info('Already connected to native host.')
    return
  }

  log.info(`Connecting to native host: ${NATIVE_HOST_NAME}`)
  try {
    port = chrome.runtime.connectNative(NATIVE_HOST_NAME)
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
  return port
}

/**
 * Sends a message to the native messaging host.
 * @param message The message object to send.
 */
export function sendNativeMessage(message: any) {
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
