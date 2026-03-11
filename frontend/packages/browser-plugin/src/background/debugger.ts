import { log } from '../3rd/log'
import { ErrorMessage } from '../common/constant'
import { Utils } from '../common/utils'

const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$'

export function checkDebuggerDetached(tabId, attempts = 0) {
  return new Promise((resolve, reject) => {
    if (attempts > 10) {
      reject(new Error(ErrorMessage.DEBUGGER_TIMOUT))
      return
    }

    chrome.debugger.getTargets((targets) => {
      const stillAttached = targets.some(target => target.tabId === tabId)

      if (!stillAttached) {
        resolve(true)
      }
      else {
        setTimeout(() => checkDebuggerDetached(tabId, attempts + 1), 500)
      }
    })
  })
}

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
  frameContextIdMap: {
    0: [], // frameId 0 executionContextIds
  } as Record<string, number[]>, // frameId executionContextIds
  networkEnabled: false,
  networkFilters: [] as NetworkRequestFilter[],
  networkCallbacks: [] as NetworkRequestCallback[],
  networkFilterdRequests: [] as NetworkRequestData[],
  pendingRequests: new Map<string, any>(),
  attachDebugger: (tabId: number) => {
    return new Promise((resolve, reject) => {
      if (Debugger.attached) {
        return reject(new Error('Debugger is already attached to a tab'))
      }
      chrome.debugger.attach({ tabId }, '1.3', () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          log.info('Debugger attached successfully')
          Debugger.tabId = tabId
          Debugger.attached = true
          resolve(true)
        }
      })
    })
  },
  enableRuntime: (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Runtime.enable', {}, () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(true)
        }
      })
    })
  },
  enableNetwork: (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Network.enable', {}, () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          Debugger.networkEnabled = true
          log.info('Network monitoring enabled')
          resolve(true)
        }
      })
    })
  },
  disableNetwork: (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Network.disable', {}, () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          Debugger.networkEnabled = false
          log.info('Network monitoring disabled')
          resolve(true)
        }
      })
    })
  },
  detachDebugger: (tabId: number) => {
    return new Promise((resolve) => {
      chrome.debugger.detach({ tabId }, () => {
        log.info('Debugger detached successfully')
        Debugger.attached = false
        Debugger.networkEnabled = false
        Debugger.frameContextIdMap = { 0: [] }
        Debugger.pendingRequests.clear()
        Debugger.networkFilterdRequests = []
        resolve(true)
      })
    })
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
    await Utils.wait(1)

    const currentFrameContextIds = Debugger.frameContextIdMap[frameId] || []
    if (!currentFrameContextIds.length) {
      throw new Error(ErrorMessage.CONTEXT_NOT_FOUND)
    }
    const allPromise = currentFrameContextIds?.map(item => chrome.debugger.sendCommand({ tabId }, 'Runtime.evaluate', { expression: code, contextId: item }))
    const allRes = await Promise.all(allPromise)
    const successRes = allRes.find(item => !item.exceptionDetails)
    const failRes = allRes.find(item => item.exceptionDetails)
    log.info('evaluate successRes: ', successRes, 'evaluate failRes: ', failRes)
    await Debugger.detachDebugger(tabId)
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
  getFrameTree: async (tabId: number) => {
    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    const frameTree = await new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Page.getFrameTree', {}, (result) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(result)
        }
      })
    })
    await Debugger.detachDebugger(tabId)
    return frameTree
  },
  getDomSnapshot: async (tabId: number) => {
    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    const domSnapshot = await new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'DOMSnapshot.captureSnapshot', {
        computedStyles: [],
        includeDOMRects: true,
      }, (result) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError)
        }
        resolve(result)
      })
    })
    await Debugger.detachDebugger(tabId)
    return domSnapshot
  },
  printToPDF: async (tabId: number, printOptions: PrintOptions) => {
    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    const pdfData = await new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Page.printToPDF', printOptions, (result) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(result.data)
        }
      })
    })
    await Debugger.detachDebugger(tabId)
    return pdfData
  },
  /**
   * start monitoring network requests with specified filters
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
}
/**
 * Listen to console.log to obtain the correspondence between frameId and executionContextId
 * The rpa_debugger_on code in the content will print the frameId
 */
if (!isFirefox) {
  chrome.debugger.onEvent.addListener(async (source, method, params) => {
    if (source.tabId !== Debugger.tabId)
      return

    if (method === 'Runtime.consoleAPICalled' && params.type === 'log' && params.args?.length) {
      const logValue = params.args[0]?.value || ''
      const executionContextId = params.executionContextId

      if (logValue.includes('rpa_debugger_on')) {
        const frameId = `${logValue.split(':')[1]}`
        if (!Debugger.frameContextIdMap[frameId]) {
          Debugger.frameContextIdMap[frameId] = [executionContextId]
        }
        if (!Debugger.frameContextIdMap[frameId].includes(executionContextId)) {
          Debugger.frameContextIdMap[frameId].push(executionContextId)
        }
      }
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
  })
  chrome.debugger.onDetach.addListener(() => {
    Debugger.attached = false
    Debugger.networkEnabled = false
    Debugger.frameContextIdMap = { 0: [] }
    Debugger.pendingRequests.clear()
    Debugger.networkFilterdRequests = []
    log.info('Debugger detached, state reset')
  })
}

export { Debugger }
