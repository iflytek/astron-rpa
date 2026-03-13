import { log } from '../3rd/log'
import { ErrorMessage, StatusCode } from '../common/constant'
import { Utils } from '../common/utils'

import { Cookie } from './cookie'
import DataTable from './data_table'
import { adjustPosition, calculateAbsolutePosition, findTabAndFrame, getFramePath, getIframeElement } from './iframe'
import * as NetworkMonitor from './network_monitor'
import { getSimilarElement, isSameIdStart } from './similar'
import { Tabs } from './tab'
import { WindowControl } from './window'

globalThis.activeElement = null
globalThis.requestInterceptionFilters = []

function contentMessageHandler(request, sender: chrome.runtime.MessageSender, _sendResponse: (args) => void) {
  if (request.type === 'element' && sender.tab) {
    const info = {
      tabTitle: sender.tab.title,
      tabUrl: sender.tab.url,
      // favIconUrl: sender.tab.favIconUrl,// different in chrome and firefox
      isFrame: sender.frameId !== 0,
      frameId: sender.frameId,
      tabId: sender.tab.id,
    }
    globalThis.activeElement = { ...request.data, ...info }
  }
  if (request.type === 'requestFrameId' && sender.tab) {
    _sendResponse(sender.frameId)
  }
  if (request.type === 'keepBackgroundAlive' && sender.tab) {
    _sendResponse(true)
  }
  if (request.type === 'contentLoaded' && sender.tab) {
    _sendResponse(true)
  }
  // if (request.type === 'nativeMessage') {
  //   sendNativeMessage(request.data);
  // }
  return true
}

const Handlers = {
  tabsHandler() {
    return {
      async reloadTab() {
        const res = await Tabs.reload()
        return Utils.success(res)
      },
      async stopLoad() {
        const res = await Tabs.stopLoad()
        return Utils.success(res)
      },
      async openNewTab(params) {
        const tab = await Tabs.create(params.data)
        return Utils.success(tab)
      },
      async closeTab(params) {
        let { url, id } = params.data
        let tab: chrome.tabs.Tab
        if (id && typeof id !== 'number') {
          try {
            id = Number.parseInt(id, 10)
            if (Number.isNaN(id)) {
              return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
            }
          }
          catch {
            return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
          }
          await Tabs.remove(id)
          return Utils.success(true)
        }
        if (url) {
          tab = await Tabs.getTab(url)
        }
        if (!tab) {
          tab = await Tabs.getActiveTab()
        }
        if (!tab) {
          return Utils.fail('tab not found')
        }
        await Tabs.remove(tab.id)
        return Utils.success(true)
      },
      async updateTab(params) {
        const { url } = params.data
        const tab = await Tabs.getActiveTab()
        if (tab) {
          await Tabs.update(tab.id, { url })
          return Utils.success(true)
        }
        else {
          return Utils.fail('tab not found')
        }
      },
      async activeTab(params) {
        const { url } = params.data
        const tab = await Tabs.getTab(url)
        await Tabs.activeTargetTab(tab.id)
        return Utils.success(true)
      },
      async getActiveTab() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        return Utils.success(tab)
      },
      async switchTab(params) {
        let { url, title, id } = params.data
        if (id && typeof id !== 'number') {
          try {
            id = Number.parseInt(id, 10)
            if (Number.isNaN(id)) {
              return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
            }
          }
          catch {
            return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
          }
        }
        const tab = await Tabs.switchTab(url, title, id)
        if (tab) {
          return Utils.success(tab)
        }
        else {
          return Utils.fail(ErrorMessage.TAB_GET_ERROR)
        }
      },

      async getAllTabs() {
        const tabs = await Tabs.getAllTabs()
        return Utils.success(tabs)
      },

      async backward() {
        const res = await Tabs.goBack()
        return Utils.success(res)
      },
      async forward() {
        const res = await Tabs.goForward()
        return Utils.success(res)
      },

      async maxWindow() {
        const wind = await WindowControl.getCurrent()
        const maxWin = await WindowControl.update(wind.id, {
          state: 'maximized',
        })
        if (maxWin) {
          return Utils.success(true)
        }
        const { lastError } = chrome.runtime
        if (lastError) {
          return Utils.fail(lastError.message, StatusCode.EXECUTE_ERROR)
        }
      },
      async minWindow() {
        const wind = await WindowControl.getCurrent()
        const minWin = await WindowControl.update(wind.id, {
          state: 'minimized',
        })
        if (minWin) {
          return Utils.success(true)
        }
        const { lastError } = chrome.runtime
        if (lastError) {
          return Utils.fail(lastError.message, StatusCode.EXECUTE_ERROR)
        }
      },
      async executeScriptOnFrame(params) {
        const { url, code } = params.data
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const frames = await Tabs.getAllFrames(tab.id)
        const frame = frames.find(frame => frame.url === url)
        const frameId = frame ? frame.frameId : 0
        const res = await Tabs.executeScriptOnFrame(tab.id, frameId, code)
        return Utils.success(res)
      },
      async getTitle() {
        const title = await Tabs.getTitle()
        return Utils.success(title)
      },
      async getUrl() {
        const title = await Tabs.getUrl()
        return Utils.success(title)
      },
      async captureScreen() {
        const res = await Tabs.captureScreen()
        if (res) {
          return Utils.success(res)
        }
      },
      async capturePage() {
        const res = await Tabs.capturePage()
        if (res) {
          return Utils.success(res)
        }
      },
      async loadComplete() {
        const { lastError } = chrome.runtime
        const activeTab = await Tabs.getActiveTab()
        if (!activeTab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        if (lastError) {
          return Utils.fail(lastError.message, StatusCode.EXECUTE_ERROR)
        }
        if (activeTab.status === 'complete') {
          return Utils.success(true)
        }
        else {
          return Utils.success(false)
        }
      },
      async getFrames() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const frames = await Tabs.getAllFrames(tab.id)
        return frames
      },
      async getExtFrames() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const frames = await Tabs.getExtFrames(tab.id)
        return frames
      },
      async resetZoom() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const res = await Tabs.resetZoom(tab.id)
        return res
      },
      async getTabId() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        return Utils.success(tab.id)
      },
      async getFrameTree() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const res = await Tabs.getFrameTree(tab.id)
        return Utils.success(res)
      },
      async printPage(params: PrintOptions) {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const res = await Tabs.printPage(tab.id, params)
        return Utils.success(res)
      },
    }
  },

  elementHandler() {
    return {
      async getElement(params) {
        const activeElement = globalThis.activeElement
        if (activeElement && activeElement.isFrame) {
          const { x, y } = params.data
          if (!x || !y) {
            return Utils.success(activeElement)
          }
          const result = await getIframeElement({ x, y }, activeElement)
          return Utils.success(result)
        }
        return Utils.success(activeElement)
      },
      async getOuterHTML(params) {
        try {
          const result = await Handlers.elementHandler().getElement(params)
          params.data = result?.data || globalThis.activeElement
          const { tab, frameId } = await findTabAndFrame({ ...params })
          const htmlResult = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
          const mergedInfo = { ...params.data, ...htmlResult.data }
          return Utils.success(mergedInfo)
        }
        catch (error) {
          console.log('ignore getOuterHTML error: ', error)
          const elementInfo = globalThis.activeElement
          return Utils.success(elementInfo)
        }
      },
      async handleInContent(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (frameId === null) {
          return Utils.fail(ErrorMessage.FRAME_GET_ERROR, StatusCode.ELEMENT_NOT_FOUND)
        }
        if (!Utils.isSupportProtocal(tab.url)) {
          return Utils.fail(`${tab.url} ${ErrorMessage.CURRENT_TAB_UNSUPPORT_ERROR}`)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        if (result === null) {
          return Utils.fail(ErrorMessage.CONTENT_MESSAGE_ERROR, StatusCode.UNKNOWN_ERROR)
        }
        if (result.code !== StatusCode.SUCCESS) {
          return Utils.fail(result.msg, result.code)
        }
        else {
          return Utils.success(result.data)
        }
      },
      async getElementPos(params: ElementParams) {
        const { isFrame } = params.data
        const { tab, frameId, frames } = await findTabAndFrame(params)
        if (frameId === null) {
          return Utils.fail(ErrorMessage.FRAME_GET_ERROR, StatusCode.ELEMENT_NOT_FOUND)
        }

        if (!Utils.isSupportProtocal(tab.url)) {
          return Utils.fail(`${tab.url} ${ErrorMessage.CURRENT_TAB_UNSUPPORT_ERROR}`)
        }
        if (!isFrame) {
          const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
          return Utils.result(result.data, result.msg, result.code)
        }

        const targetFrame = frames.find(frame => frame.frameId === frameId)
        const framePath = getFramePath(frames, targetFrame)
        const absolutePos = await calculateAbsolutePosition(tab.id, framePath)
        const elementPosResult = await Tabs.sendTabFrameMessage(tab.id, params, targetFrame.frameId)

        if (elementPosResult.code !== StatusCode.SUCCESS) {
          return Utils.fail(elementPosResult.msg, elementPosResult.code)
        }

        adjustPosition(elementPosResult.data.rect, absolutePos)

        return Utils.success(elementPosResult.data)
      },
      async checkElement(params: ElementParams) {
        const res = await Handlers.elementHandler().getElementPos(params)
        return res
      },
      async scrollIntoView(params: ElementParams) {
        if (params.data?.openSourcePage) {
          const activeTab = await Tabs.getActiveTab()
          if (!activeTab || activeTab.url !== params.data.tabUrl) {
            await Tabs.openTab(params.data.url)
          }
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async similarElement(params: ElementParams) {
        let activeElement = globalThis.activeElement
        const { tabUrl } = params.data
        let activeTab = await Tabs.getActiveTab()
        if (!activeTab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        if (activeTab.url !== tabUrl) {
          activeTab = await Tabs.getTab(tabUrl)
        }
        try {
          const isSameId = isSameIdStart(params.data.pathDirs, activeElement.pathDirs)
          if (!isSameId) {
            const res = await Handlers.elementHandler().handleInContent({
              ...params,
              key: 'reSimilarElement',
              data: { ...activeElement, preData: params.data },
            })
            log.info('reSimilarElement result: ', res)
            if (res.data) {
              params.data = res.data.preData
              activeElement = res.data
              delete params.data.preData
            }
          }
          const similarElementInfo = getSimilarElement(params.data, activeElement)
          if (similarElementInfo) {
            const res = await Handlers.elementHandler().handleInContent({
              ...params,
              data: similarElementInfo,
            })
            similarElementInfo.similarCount = res.data?.similarCount || 0
            return Utils.success(similarElementInfo)
          }
          else {
            return Utils.fail(ErrorMessage.NOT_SIMILAR_ELEMENT, StatusCode.ELEMENT_NOT_FOUND)
          }
        }
        catch (error) {
          return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
        }
      },

      async elementFromSelect(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async elementIsRender(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (frameId === null) {
          return Utils.success(false)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        if (result) {
          return Utils.success(result.data)
        }
        else {
          return Utils.success(false)
        }
      },

      async elementIsReady(params: ElementParams) {
        const activeTab = await Tabs.getActiveTab()
        const { tab, frameId } = await findTabAndFrame(params)
        if (frameId === null) {
          return Utils.success(false)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        const complete = activeTab.status === 'complete'
        if (result) {
          return Utils.success(result.data && complete)
        }
        else {
          return Utils.success(false)
        }
      },

      async elementIsTable(params: ElementParams) {
        if (!params.data.xpath) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const isTable = !!res.data
        const elementResult = { isTable, ...params.data }
        return Utils.success(elementResult)
      },

      async tableDataBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const values = res.data?.values || []
        const dataTable = new DataTable(res.data, values, 'table')
        const table = dataTable.getTable()
        return Utils.success(table)
      },

      async tableColumnDataBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const value = res.data?.value || []
        const dataTable = new DataTable(res.data, value, 'similar')
        const table = dataTable.getTable()
        return Utils.success(table)
      },

      async similarBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        if ('batchType' in params.data && ['similar', 'similarAdd'].includes(params.data.batchType)) {
          const res = await Handlers.elementHandler().similarElement(params)
          if (res.code !== StatusCode.SUCCESS) {
            return res
          }
          params.data = res.data
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const value = res.data?.value || []
        const dataTable = new DataTable(res.data, value, 'similar')
        const table = dataTable.getTable()
        return Utils.success(table)
      },

      async tableHeaderBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async simalarListBatch(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async highLightColumn(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getBatchData(params: { key: string, data: BatchElementParams }) {
        if (params.data?.openSourcePage) {
          const activeTab = await Tabs.getActiveTab()
          if (!activeTab || activeTab.url !== params.data.tabUrl) {
            await Tabs.openTab(params.data.tabUrl)
          }
        }
        await Utils.wait(3)
        if (params.data && params.data.produceType === 'similar') {
          params.key = 'simalarListBatch'
          const res = await Handlers.elementHandler().simalarListBatch(params)
          return res
        }
        else {
          params.key = 'tableDataBatch'
          const res = await Handlers.elementHandler().tableDataBatch(params)
          return res
        }
      },

      async elementShot(params: ElementParams) {
        // 1, scrollToTop 2, resetZoom 3, getElementPos 4, debugger attach  5, capture 6, debugger detach 7, return data
        params.key = 'scrollToTop'
        await Handlers.elementHandler().scrollToTop(params)
        await Handlers.tabsHandler().resetZoom()
        params.key = 'getElementPos'
        const res = await Handlers.elementHandler().getElementPos(params)
        const { x, y, width, height } = res.data?.rect
        const data = await Tabs.captureElement({ x, y, width, height })
        return Utils.success(data)
      },

      async scrollToTop(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return Utils.success(res)
      },

      async getSimilarIterator(params: ElementParams) {
        params.key = 'elementFromSelect'
        const index = params.data?.index || 0
        const count = params.data?.count || 1
        const res = await Handlers.elementHandler().elementFromSelect(params)
        if (res.data && Array.isArray(res.data)) {
          if (index < res.data.length) {
            let data = [res.data[index]]
            if (index + count <= res.data.length) {
              data = res.data.slice(index, index + count)
            }
            else {
              data = res.data.slice(index)
            }
            data = data.map((item, index) => {
              item.index += index
              return { ...item, similarCount: res.data.length }
            })
            return Utils.success(data)
          }
          else {
            return Utils.success([])
          }
        }
        else {
          return Utils.fail(ErrorMessage.SIMILAR_NOT_FOUND, StatusCode.ELEMENT_NOT_FOUND)
        }
      },

      async getRelativeElement(params: ElementParams) {
        const { relativeOptions } = params.data
        if (!relativeOptions) {
          return Utils.fail(ErrorMessage.RELATIVE_ELEMENT_PARAMS_ERROR)
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async generateElement(params: { key: string, data: GenerateParamsT }) {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, 0)
        return result
      },

      async getParentElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      async getChildElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // --------------- v3
      async clickElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async inputElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementText(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementAttrs(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async removeElementAttr(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async setElementAttr(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementChecked(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async setElementChecked(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementSelected(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async setElementSelected(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getTableData(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async scrollWindow(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
    }
  },

  jsHandler() {
    return {

      async runJS(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (frameId === null) {
          return Utils.fail(ErrorMessage.FRAME_GET_ERROR, StatusCode.ELEMENT_NOT_FOUND)
        }
        try {
          await Tabs.getAllFrames(tab.id)
          const result = await Tabs.runJS(tab.id, frameId, params)
          return Utils.success(result)
        }
        catch (error) {
          return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
        }
      },
    }
  },

  cookieHandler() {
    return { ...Cookie }
  },

  otherHandler() {
    return {
      currentExtension() {
        return new Promise((resolve) => {
          chrome.management.getSelf((info) => {
            resolve(info)
          })
        })
      },
      backgroundInject() {
        return Utils.success(true)
      },
      contentInject() {
        return Utils.success(true)
      },
    }
  },

  networkHandler() {
    return {
      async getRequestInterceptionFilters() {
        const filters = globalThis.requestInterceptionFilters || []
        return Utils.success(filters)
      },
      async setRequestInterceptionFilters(filters: NetworkRequestFilter[]) {
        globalThis.requestInterceptionFilters = filters || []
        return Utils.success(true)
      },
      async addRequestInterceptionFilter(filters: NetworkRequestFilter[]) {
        globalThis.requestInterceptionFilters = [...globalThis.requestInterceptionFilters, ...filters]
        return Utils.success(true)
      },
      async removeRequestInterceptionFilter(filters: NetworkRequestFilter[]) {
        const currentFilters = globalThis.requestInterceptionFilters || []
        globalThis.requestInterceptionFilters = currentFilters.filter((currentFilter) => {
          return !filters.some((filter) => {
            return filter.urlPattern === currentFilter.urlPattern && filter.pathPattern === currentFilter.pathPattern
          })
        })
        return Utils.success(true)
      },
      async startDebugNetworkListen(filters: NetworkRequestFilter[]) {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        // 统一调用 network_monitor 导出的函数（Chrome 和 Firefox）
        await NetworkMonitor.startNetworkMonitor(tab.id, filters)
        return Utils.success(true)
      },
      async stopDebugNetworkListen() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        // 统一调用 network_monitor 导出的函数（Chrome 和 Firefox）
        await NetworkMonitor.stopNetworkMonitor(tab.id)
        return Utils.success(true)
      },
      async getDebugNetworkData() {
        // 统一调用 network_monitor 导出的函数（Chrome 和 Firefox）
        const data = NetworkMonitor.getNetworkData()
        return Utils.success(data)
      },
      async clearDebugNetworkData() {
        // 统一调用 network_monitor 导出的函数（Chrome 和 Firefox）
        NetworkMonitor.clearNetworkData()
        return Utils.success(true)
      },
    }
  },

  noHandler() {
    return Utils.fail(ErrorMessage.UNSUPPORT_ERROR, StatusCode.VERSION_ERROR)
  },
}

async function bgHandler(params) {
  let result = null
  const { key } = params
  const handlers = Handlers
  try {
    if (handlers[key]) {
      result = await handlers[key](params)
      return result
    }
    else if (handlers.tabsHandler()[key]) {
      result = await handlers.tabsHandler()[key](params)
      return result
    }
    else if (handlers.elementHandler()[key]) {
      if (params.data && 'produceType' in params.data && params.data.produceType === 'similar') {
        params.data = { ...params.data, ...params.data.values[0] }
      }
      result = await handlers.elementHandler()[key](params)
      return result
    }
    else if (handlers.jsHandler()[key]) {
      result = await handlers.jsHandler()[key](params)
      return result
    }
    else if (handlers.cookieHandler()[key]) {
      result = await handlers.cookieHandler()[key](params.data)
      return result
    }
    else if (handlers.otherHandler()[key]) {
      result = await handlers.otherHandler()[key](params.data)
      return result
    }
    else if (handlers.networkHandler()[key]) {
      result = await handlers.networkHandler()[key](params.data)
      return result
    }
    else {
      result = handlers.noHandler()
      return result
    }
  }
  catch (error) {
    if (error.toString().includes('connection')) {
      return Utils.fail(ErrorMessage.CONTEXT_NOT_FOUND, StatusCode.UNKNOWN_ERROR)
    }
    return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
  }
}

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  const tab = await Tabs.getActiveTab()
  const matchingRule = globalThis.requestInterceptionFilters.find((rule) => {
    try {
      const urlMatch = new RegExp(rule.urlPattern).test(details.url)
      return urlMatch
    }
    catch {
      return false
    }
  })
  if (details.url === tab.url && matchingRule) {
    Handlers.networkHandler().startDebugNetworkListen(globalThis.requestInterceptionFilters)
  }
})

export { bgHandler, contentMessageHandler }
