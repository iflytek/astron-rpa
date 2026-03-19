import { log } from '../3rd/log'
import { ErrorMessage } from '../common/constant'
import { Utils } from '../common/utils'

const isFirefox = Utils.isFirefox()

export function checkDebuggerDetached(tabId, attempts = 10) {
  return new Promise((resolve, reject) => {
    if (attempts <= 0) {
      reject(new Error(ErrorMessage.DEBUGGER_TIMOUT))
      return
    }

    chrome.debugger.getTargets((targets) => {
      const stillAttached = targets.some(target => target.tabId === tabId)

      if (!stillAttached) {
        resolve(true)
      }
      else {
        setTimeout(() => checkDebuggerDetached(tabId, attempts - 1), 500)
      }
    })
  })
}

/**
 * Debugger listener and related functions
 */
let debuggerEventListener: ((source: chrome.debugger.Debuggee, method: string, params?: any) => void) | null = null
let debuggerDetachListener: ((source: chrome.debugger.Debuggee, reason: chrome.debugger.DetachReason) => void) | null = null

/**
 * Debugger-related functions
 * 1. attach debugger
 * 2. Listen for events and obtain the execution context
 * 3, execute the code
 * 4. detach debugger
 */
const Debugger = {
  attached: false,
  tabId: 0,
  frameContextIdMap: {} as Record<number, Array<{
    sameOrigin: boolean
    target: chrome.debugger.Debuggee | chrome.debugger.DebuggerSession
    contextId: number | null
  }>>,
  networkEnabled: false,
  networkFilters: [] as NetworkRequestFilter[],
  networkCallbacks: [] as NetworkRequestCallback[],
  networkFilterdRequests: [] as NetworkRequestData[],
  pendingRequests: new Map<string, any>(),
  listenersRegistered: false,
  /**
   * Attach the debugger to the specified tab and set up event listeners
   * @param tabId The ID of the tab to attach the debugger to
   */
  attachDebugger: async (tabId: number) => {
    if (!Debugger.attached) {
      try {
        await chrome.debugger.attach({ tabId }, '1.3')
        Debugger.tabId = tabId
        Debugger.attached = true
        Debugger.registerDebuggerListeners()
        log.info('Debugger attached successfully')
      }
      catch (error) {
        throw new Error(`Failed to attach debugger: ${error.message}`)
      }
    }
  },
  // Enable the Runtime domain to allow code execution
  enableRuntime: async (tabId: number) => {
    try {
      await chrome.debugger.sendCommand({ tabId }, 'Runtime.enable')
      log.info('Runtime domain enabled')
    }
    catch (error) {
      throw new Error(`Failed to enable Runtime domain: ${error.message}`)
    }
  },
  // Enable the Network domain to allow network monitoring
  enableNetwork: async (tabId: number) => {
    try {
      await chrome.debugger.sendCommand({ tabId }, 'Network.enable')
      Debugger.networkEnabled = true
      log.info('Network monitoring enabled')
    }
    catch (error) {
      throw new Error(`Failed to enable Network domain: ${error.message}`)
    }
  },
  // Disable the Network domain
  disableNetwork: async (tabId: number) => {
    try {
      await chrome.debugger.sendCommand({ tabId }, 'Network.disable')
      log.info('Network monitoring disabled')
      Debugger.networkEnabled = false
    }
    catch (error) {
      throw new Error(`Failed to disable Network domain: ${error.message}`)
    }
  },
  // Detach the debugger from the tab and clean up event listeners
  detachDebugger: async (tabId: number) => {
    try {
      await chrome.debugger.detach({ tabId })
      log.info('Debugger detached successfully')
      Debugger.attached = false
      Debugger.networkEnabled = false
      Debugger.frameContextIdMap = {}
      Debugger.pendingRequests.clear()
      Debugger.networkFilterdRequests = []
      Debugger.unregisterDebuggerListeners()
    }
    catch (error) {
      throw new Error(`Failed to detach debugger: ${error.message}`)
    }
  },
  // Set up auto-attach for new targets (e.g., iframes) within the tab
  setupAutoAttach: async (tabId: number) => {
    await chrome.debugger.sendCommand({ tabId }, 'Target.setAutoAttach', {
      autoAttach: true,
      waitForDebuggerOnStart: false,
      flatten: true,
    })
    await chrome.debugger.sendCommand({ tabId }, 'Runtime.enable')
  },
  /**
   * Execute code in the specified tab and frame
   * @param tabId Tab ID
   * @param code Code to be executed
   * @param frameId Frame ID
   * @returns Execution result
   */
  evaluate: async (tabId: number, code: string, frameId: number) => {
    code = `(function() { ${code} })()`

    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    await Debugger.setupAutoAttach(tabId)

    const currentFrameContextIds = Debugger.frameContextIdMap[frameId] || []
    if (!currentFrameContextIds.length) {
      throw new Error(ErrorMessage.CONTEXT_NOT_FOUND)
    }
    const allPromise = currentFrameContextIds.map(item => chrome.debugger.sendCommand(item.target, 'Runtime.evaluate', { expression: code, contextId: item.contextId, returnByValue: true }))
    const allRes = await Promise.all(allPromise)
    const successRes = allRes.find(item => !item.exceptionDetails)
    const failRes = allRes.find(item => item.exceptionDetails)
    log.info('evaluate success: ', successRes, 'evaluate fail: ', failRes)
    if (successRes) {
      return successRes.result.value || ''
    }
    else if (failRes) {
      throw new Error(failRes.result.description)
    }
    else {
      throw new Error(ErrorMessage.EXECUTE_ERROR)
    }
  },
  getDomSnapshot: async (tabId: number) => {
    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    const domSnapshot = await chrome.debugger.sendCommand({ tabId }, 'DOMSnapshot.captureSnapshot', {
      computedStyles: [],
      includeDOMRects: true,
    })
    return domSnapshot
  },
  printToPDF: async (tabId: number, printOptions: PrintOptions) => {
    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    const pdfData = await chrome.debugger.sendCommand({ tabId }, 'Page.printToPDF', printOptions)
    return pdfData.data
  },
  /**
   * start monitoring network requests with specified filters
   * @param tabId Tab ID
   * @param filters filters to apply when monitoring network requests
   */
  startNetworkMonitoring: async (tabId: number, filters: NetworkRequestFilter[]) => {
    if (!Debugger.attached) {
      await Debugger.attachDebugger(tabId)
    }
    await Debugger.enableNetwork(tabId)

    Debugger.networkFilters = filters

    log.info('Network monitoring started with filters:', filters)
  },
  /**
   * stop monitoring network requests and clear all related data
   */
  stopNetworkMonitoring: async (tabId: number) => {
    if (Debugger.networkEnabled) {
      await Debugger.disableNetwork(tabId)
      await Debugger.detachDebugger(tabId)
    }
    Debugger.networkFilters = []
    Debugger.networkCallbacks = []
    Debugger.pendingRequests.clear()
    log.info('Network monitoring stopped')
  },

  addNetworkFilter: (filter: NetworkRequestFilter) => {
    Debugger.networkFilters.push(filter)
  },

  removeNetworkFilter: (filter: NetworkRequestFilter) => {
    const index = Debugger.networkFilters.indexOf(filter)
    if (index > -1) {
      Debugger.networkFilters.splice(index, 1)
    }
  },

  matchesFilter: (url: string, method: string): boolean => {
    if (Debugger.networkFilters.length === 0) {
      return true
    }

    return Debugger.networkFilters.some((filter) => {
      if (filter.urlPattern) {
        try {
          const urlRegex = new RegExp(filter.urlPattern)
          if (!urlRegex.test(url)) {
            return false
          }
        }
        catch {
          return false
        }
      }

      if (filter.pathPattern) {
        try {
          const urlObj = new URL(url)
          const pathRegex = new RegExp(filter.pathPattern)
          if (!pathRegex.test(urlObj.pathname)) {
            return false
          }
        }
        catch {
          return false
        }
      }

      if (filter.method && filter.method.toUpperCase() !== method.toUpperCase()) {
        return false
      }

      return true
    })
  },
  // handle console messages to capture execution context IDs for same-origin frames
  handleConsoleMessage: async (source: chrome.debugger.Debuggee, params) => {
    for (const arg of params.args) {
      const logVal = arg.value
      if (typeof logVal === 'string' && logVal.startsWith('rpa_debugger_on:')) {
        const frameId = logVal.split('rpa_debugger_on:')[1]
        Debugger.frameContextIdMap[frameId] = [{ sameOrigin: true, target: source, contextId: params.executionContextId }]
      }
    }
  },
  // handle attached targets (e.g., iframes) to capture their execution context IDs
  handleAttachedTarget: async (source: chrome.debugger.Debuggee, params) => {
    const session = {
      tabId: source.tabId,
      sessionId: params.sessionId,
    }

    try {
      await chrome.debugger.sendCommand(session, 'Runtime.enable')
      await chrome.debugger.sendCommand(session, 'Target.setAutoAttach', {
        autoAttach: true,
        waitForDebuggerOnStart: false,
        flatten: true,
      })
      const res = await chrome.debugger.sendCommand(session, 'Runtime.evaluate', {
        expression: `
        // This code runs in the cross-origin iframe context to get frame identifier information.
        ;(function () {
          return {
            url: window.location.href,
            title: document.title,
            injected: true,
            frameId: document.documentElement.dataset.astronFrameId || 0
          }
        })()`,
        returnByValue: true,
      })
      if (res.exceptionDetails) {
        throw new Error(`Error evaluating code in target: ${res.result.description}`)
      }
      if (res.result) {
        const { frameId } = res.result.value
        Debugger.frameContextIdMap[frameId] = [{ sameOrigin: false, target: session, contextId: null }]
      }
    }
    catch (error) {
      throw new Error(`Error handling attached target: ${error.message}`)
    }
  },

  registerDebuggerListeners: () => {
    if (isFirefox || Debugger.listenersRegistered) {
      return
    }

    // create event listener
    debuggerEventListener = async (source: chrome.debugger.Debuggee, method: string, params) => {
      if (source.tabId !== Debugger.tabId)
        return

      if (method === 'Runtime.consoleAPICalled' && params.type === 'log' && params.args?.length) {
        Debugger.handleConsoleMessage(source, params).catch((error) => {
          log.error('Error handling console message:', error)
        })
      }

      if (method === 'Target.attachedToTarget') {
        Debugger.handleAttachedTarget(source, params).catch((error) => {
          log.error('Error handling attached target:', error)
        })
      }

      if (!Debugger.networkEnabled)
        return

      if (method === 'Network.requestWillBeSent') {
        const { requestId, request } = params
        if (Debugger.matchesFilter(request.url, request.method)) {
          Debugger.pendingRequests.set(requestId, {
            url: request.url,
            method: request.method,
            timestamp: Date.now(),
          })
        }
      }

      if (method === 'Network.responseReceived' || method === 'Network.loadingFinished') {
        const { requestId, response } = params
        const requestInfo = Debugger.pendingRequests.get(requestId)

        if (!requestInfo)
          return

        try {
          chrome.debugger.sendCommand(
            { tabId: source.tabId },
            'Network.getResponseBody',
            { requestId },
            (result) => {
              if (chrome.runtime.lastError) {
                log.warn('Failed to get response body:', method, requestInfo, chrome.runtime.lastError)
                return
              }

              let responseBody: any
              if (result && result.body) {
                try {
                  responseBody = JSON.parse(result.body)
                }
                catch {
                  responseBody = result.body
                }
              }

              const responseHeaders: Record<string, string> = {}
              if (response?.headers) {
                Object.keys(response.headers).forEach((key) => {
                  responseHeaders[key] = response.headers[key]
                })
              }

              const networkData: NetworkRequestData = {
                requestId,
                ...requestInfo,
                status: response ? response.status : 200,
                responseBody,
                responseHeaders,
              }

              // store the filtered request data
              Debugger.networkFilterdRequests.push(networkData)
              Debugger.pendingRequests.delete(requestId)
            },
          )
        }
        catch (error) {
          log.error('Error processing network response:', error)
          Debugger.pendingRequests.delete(requestId)
        }
      }

      if (method === 'Network.loadingFailed') {
        const { requestId } = params
        Debugger.pendingRequests.delete(requestId)
      }
    }

    // create detach listener
    debuggerDetachListener = () => {
      Debugger.attached = false
      Debugger.networkEnabled = false
      Debugger.frameContextIdMap = {}
      Debugger.pendingRequests.clear()
      Debugger.networkFilterdRequests = []
      Debugger.unregisterDebuggerListeners()
      log.info('Debugger detached, state reset')
    }

    // register listeners
    chrome.debugger.onEvent.addListener(debuggerEventListener)
    chrome.debugger.onDetach.addListener(debuggerDetachListener)
    Debugger.listenersRegistered = true

    log.info('Debugger listeners registered')
  },

  unregisterDebuggerListeners: () => {
    if (isFirefox || !Debugger.listenersRegistered) {
      return
    }

    if (debuggerEventListener) {
      chrome.debugger.onEvent.removeListener(debuggerEventListener)
      debuggerEventListener = null
    }

    if (debuggerDetachListener) {
      chrome.debugger.onDetach.removeListener(debuggerDetachListener)
      debuggerDetachListener = null
    }

    Debugger.listenersRegistered = false
    log.info('Debugger listeners unregistered')
  },
}

export { Debugger }
