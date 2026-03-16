import { log } from '../3rd/log'
import { Utils } from '../common/utils'

import { Debugger } from './debugger'

const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$'

/**
 * Firefox Network Monitor
 */
class FirefoxNetworkMonitor {
  private isEnabled = false
  private filters: NetworkRequestFilter[] = []
  private pendingRequests = new Map<string, any>()
  private filteredRequests: NetworkRequestData[] = []
  private urlPatterns: string[] = ['<all_urls>']

  /**
   * Start network monitoring
   */
  async startMonitoring(_tabId: number, filters: NetworkRequestFilter[]): Promise<void> {
    if (this.isEnabled) {
      log.warn('[Firefox] Network monitor already enabled')
      return
    }

    this.filters = filters
    this.urlPatterns = this.extractUrlPatterns(filters)
    this.registerListeners()
    this.isEnabled = true

    log.info('[Firefox] Network monitoring started with filters:', filters)
  }

  /**
   * Stop network monitoring
   */
  async stopMonitoring(_tabId: number): Promise<void> {
    if (!this.isEnabled) {
      return
    }

    this.unregisterListeners()
    this.isEnabled = false
    this.filters = []
    this.pendingRequests.clear()
    this.filteredRequests = []

    log.info('[Firefox] Network monitoring stopped')
  }

  /**
   * Get filtered request data
   */
  getFilteredRequests(): NetworkRequestData[] {
    return this.filteredRequests
  }

  /**
   * Clear request data
   */
  clearFilteredRequests(): void {
    this.filteredRequests = []
  }

  /**
   * Add a filter
   */
  addFilter(filter: NetworkRequestFilter): void {
    this.filters.push(filter)
    this.urlPatterns = this.extractUrlPatterns(this.filters)
  }

  /**
   * Remove a filter
   */
  removeFilter(filter: NetworkRequestFilter): void {
    const index = this.filters.indexOf(filter)
    if (index > -1) {
      this.filters.splice(index, 1)
      this.urlPatterns = this.extractUrlPatterns(this.filters)
    }
  }

  /**
   * Extract URL patterns from filters
   */
  private extractUrlPatterns(filters: NetworkRequestFilter[]): string[] {
    if (filters.length === 0) {
      return ['<all_urls>']
    }

    const patterns = new Set<string>()
    filters.forEach((filter) => {
      if (filter.urlPattern) {
        // Convert regular expressions to webRequest URL patterns
        // For example: 'https://api\.example\.com/.*' -> 'https://api.example.com/*'
        try {
          let pattern = filter.urlPattern
          // Simple conversion: remove escape characters, replace .* with *
          pattern = pattern.replace(/\\\./g, '.')
          pattern = pattern.replace(/\.\*/g, '*')
          patterns.add(pattern)
        }
        catch {
          patterns.add('<all_urls>')
        }
      }
      else {
        patterns.add('<all_urls>')
      }
    })

    return Array.from(patterns)
  }

  /**
   * Check if a request matches the filters
   */
  private matchesFilter(url: string, method: string): boolean {
    if (this.filters.length === 0) {
      return true
    }

    return this.filters.some((filter) => {
      // Check URL match
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

      // Check path match
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

      // Check method match
      if (filter.method && filter.method.toUpperCase() !== method.toUpperCase()) {
        return false
      }

      return true
    })
  }

  /**
   * Register webRequest listeners
   */
  private registerListeners(): void {
    if (!isFirefox) {
      log.warn('[Firefox] Not Firefox browser, skipping webRequest listeners')
      return
    }
    console.log('Registering webRequest listeners with URL patterns:', this.urlPatterns)
    // Listen for requests before they are sent (to get request information)
    chrome.webRequest.onBeforeRequest.addListener(
      this.onBeforeRequest.bind(this),
      { urls: this.urlPatterns },
      ['requestBody'],
    )

    // Listen for request headers being sent
    chrome.webRequest.onSendHeaders.addListener(
      this.onSendHeaders.bind(this),
      { urls: this.urlPatterns },
      ['requestHeaders'],
    )

    // Listen for response headers being received (use filterResponseData to get response body)
    chrome.webRequest.onHeadersReceived.addListener(
      this.onHeadersReceived.bind(this),
      { urls: this.urlPatterns },
      ['responseHeaders', 'blocking'],
    )

    // Listen for request completion
    chrome.webRequest.onCompleted.addListener(
      this.onCompleted.bind(this),
      { urls: this.urlPatterns },
      ['responseHeaders'],
    )

    // Listen for request errors
    chrome.webRequest.onErrorOccurred.addListener(
      this.onErrorOccurred.bind(this),
      { urls: this.urlPatterns },
    )

    log.info('[Firefox] WebRequest listeners registered')
  }

  /**
   * Unregister webRequest listeners
   */
  private unregisterListeners(): void {
    if (!isFirefox) {
      return
    }

    chrome.webRequest.onBeforeRequest.removeListener(this.onBeforeRequest)
    chrome.webRequest.onSendHeaders.removeListener(this.onSendHeaders)
    chrome.webRequest.onHeadersReceived.removeListener(this.onHeadersReceived)
    chrome.webRequest.onCompleted.removeListener(this.onCompleted)
    chrome.webRequest.onErrorOccurred.removeListener(this.onErrorOccurred)

    log.info('[Firefox] WebRequest listeners unregistered')
  }

  /**
   * Handle requests before they are sent
   */
  private onBeforeRequest(details: any): void {
    const { requestId, url, method, requestBody, timeStamp } = details

    // Check if the request matches the filters
    if (!this.matchesFilter(url, method)) {
      return
    }

    // Record request information
    this.pendingRequests.set(requestId, {
      url,
      method,
      requestBody,
      timestamp: timeStamp,
    })

    log.info(`[Firefox] Request started: ${method} ${url}`)
  }

  /**
   * Handle request headers being sent
   */
  private onSendHeaders(details: any): void {
    const { requestId, requestHeaders } = details
    const requestInfo = this.pendingRequests.get(requestId)

    if (requestInfo) {
      requestInfo.requestHeaders = this.headersToObject(requestHeaders)
    }
  }

  /**
   * Handle response headers being received (to get response body)
   */
  private onHeadersReceived(details: any): void {
    const { requestId, responseHeaders, statusCode, statusLine } = details
    const requestInfo = this.pendingRequests.get(requestId)

    if (!requestInfo) {
      return
    }

    requestInfo.status = statusCode
    requestInfo.statusText = statusLine
    requestInfo.responseHeaders = this.headersToObject(responseHeaders)

    // Check if the response body should be captured
    // The following cases do not use filterResponseData:
    // 1. 204 No Content or 205 Reset Content (no response body)
    // 2. 3xx Redirect (causes NS_ERROR_FAILURE)
    // 3. 304 Not Modified (no response body)
    if (statusCode === 204 || statusCode === 205 || statusCode === 304 || (statusCode >= 300 && statusCode < 400)) {
      log.info(`[Firefox] Skipping filterResponseData for status ${statusCode}`)
      return
    }

    // Use filterResponseData to get the response body (Firefox-specific)
    try {
      // @ts-expect-error Firefox specific API
      const filter = chrome.webRequest.filterResponseData(requestId)
      const decoder = new TextDecoder('utf-8')
      const chunks: Uint8Array[] = []

      filter.ondata = (event: any) => {
        try {
          chunks.push(new Uint8Array(event.data))
          // Pass data to the original response
          filter.write(event.data)
        }
        catch (error) {
          log.error('[Firefox] Error in filter.ondata:', error)
        }
      }

      filter.onstop = () => {
        try {
          // Combine all data chunks
          const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0)
          const combined = new Uint8Array(totalLength)
          let offset = 0
          chunks.forEach((chunk) => {
            combined.set(chunk, offset)
            offset += chunk.length
          })

          // Decode to string
          const responseText = decoder.decode(combined)
          requestInfo.responseBody = responseText

          log.info(`[Firefox] Response body captured for ${requestInfo.url} (${totalLength} bytes)`)
        }
        catch (error) {
          log.error('[Firefox] Error decoding response:', error)
        }
        finally {
          try {
            filter.disconnect()
          }
          catch (error) {
            log.error('[Firefox] Error disconnecting filter:', error)
          }
        }
      }

      filter.onerror = (event: any) => {
        log.error('[Firefox] Filter error for', requestInfo.url, ':', event)
        try {
          filter.disconnect()
        }
        catch {
          // Ignore disconnect errors
        }
      }
    }
    catch (error) {
      log.error('[Firefox] Failed to create filter for', requestInfo.url, ':', error)
    }
  }

  /**
   * Handle request completion
   */
  private onCompleted(details: any): void {
    const { requestId, url, method, statusCode } = details
    const requestInfo = this.pendingRequests.get(requestId)

    if (!requestInfo) {
      return
    }

    // Parse response body
    let responseBody = requestInfo.responseBody
    if (responseBody && typeof responseBody === 'string') {
      try {
        // Attempt to parse as JSON
        responseBody = JSON.parse(responseBody)
      }
      catch {
        // Keep as raw text
      }
    }

    // Build complete request data (keep the same structure as Chrome debugger API)
    const networkData: NetworkRequestData = {
      requestId,
      url,
      method,
      status: statusCode,
      responseBody,
      responseHeaders: requestInfo.responseHeaders || {},
      timestamp: requestInfo.timestamp,
    }

    log.info(`[Firefox] Request completed: ${method} ${url} - ${statusCode}`)

    // Store filtered request data
    this.filteredRequests.push(networkData)

    // Clean up completed requests
    this.pendingRequests.delete(requestId)
  }

  /**
   * Handle request errors
   */
  private onErrorOccurred(details: any): void {
    const { requestId, url, error } = details

    log.error(`[Firefox] Request failed: ${url} - ${error}`)

    // Clean up failed requests
    this.pendingRequests.delete(requestId)
  }

  /**
   * Convert response headers array to object
   */
  private headersToObject(headers: any[]): Record<string, string> {
    const result: Record<string, string> = {}
    if (Array.isArray(headers)) {
      headers.forEach((header) => {
        result[header.name] = header.value
      })
    }
    return result
  }
}

/**
 * Chrome Network Monitor
 * Uses Chrome debugger API implementation from Debugger
 */
class ChromeNetworkMonitor {
  /**
   * Start network monitoring (calls Debugger.startNetworkMonitoring)
   */
  async startMonitoring(tabId: number, filters: NetworkRequestFilter[]): Promise<void> {
    if (Debugger.networkEnabled) {
      log.warn('[Chrome] Network monitor already enabled')
      return
    }
    await Debugger.startNetworkMonitoring(tabId, filters)
    log.info('[Chrome] Network monitoring started with debugger API')
  }

  /**
   * Stop network monitoring (calls Debugger.stopNetworkMonitoring)
   */
  async stopMonitoring(tabId: number): Promise<void> {
    if (!Debugger.networkEnabled) {
      return
    }
    await Debugger.stopNetworkMonitoring(tabId)
    log.info('[Chrome] Network monitoring stopped')
  }

  /**
   * Get filtered request data (calls Debugger.getNetworkData)
   */
  getFilteredRequests(): NetworkRequestData[] {
    return Debugger.networkFilterdRequests
  }

  /**
   * Clear request data (calls Debugger.clearNetworkData)
   */
  clearFilteredRequests(): void {
    Debugger.networkFilterdRequests = []
  }

  /**
   * Add a filter (calls Debugger.addNetworkFilter)
   */
  addFilter(filter: NetworkRequestFilter): void {
    Debugger.addNetworkFilter(filter)
  }

  /**
   * Remove a filter (calls Debugger.removeNetworkFilter)
   */
  removeFilter(filter: NetworkRequestFilter): void {
    Debugger.removeNetworkFilter(filter)
  }
}

/**
 * Network monitor instance (automatically selects based on browser type)
 */
// eslint-disable-next-line import/no-mutable-exports
let networkMonitorInstance: FirefoxNetworkMonitor | ChromeNetworkMonitor | null = null
if (isFirefox) {
  networkMonitorInstance = new FirefoxNetworkMonitor()
}
else {
  networkMonitorInstance = new ChromeNetworkMonitor()
}

/**
 * Start network monitoring (unified interface)
 * @param tabId Tab ID
 * @param filters Array of filters
 */
export async function startNetworkMonitor(tabId: number, filters: NetworkRequestFilter[]): Promise<void> {
  await networkMonitorInstance.startMonitoring(tabId, filters)
}

/**
 * Stop network monitoring (unified interface)
 * @param tabId Tab ID
 */
export async function stopNetworkMonitor(tabId: number): Promise<void> {
  await networkMonitorInstance.stopMonitoring(tabId)
}

/**
 * Get network data (unified interface)
 */
export function getNetworkData(): NetworkRequestData[] {
  return networkMonitorInstance.getFilteredRequests()
}

/**
 * Clear network data (unified interface)
 */
export function clearNetworkData(): void {
  networkMonitorInstance.clearFilteredRequests()
}

/**
 * Add a filter (unified interface)
 */
export function addNetworkFilter(filter: NetworkRequestFilter): void {
  networkMonitorInstance.addFilter(filter)
}

/**
 * Remove a filter (unified interface)
 */
export function removeNetworkFilter(filter: NetworkRequestFilter): void {
  networkMonitorInstance.removeFilter(filter)
}

// Export instance
export { networkMonitorInstance as NetworkMonitor }
export default networkMonitorInstance
