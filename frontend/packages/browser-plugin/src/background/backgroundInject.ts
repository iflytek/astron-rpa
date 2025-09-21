import type { BatchElementParams } from '../types/data_grab'

import { StatusCode } from './constant'
import { Cookie } from './cookie'
import DataTable from './data_table'
import { getSimilarElement, isSameIdStart } from './similar'
import { Tabs } from './tab'
import { Utils } from './utils'
import { WindowControl } from './window'

globalThis.activeElement = null // 当前激活的元素

function contentMessageHandler(request, sender: chrome.runtime.MessageSender, _sendResponse: () => void) {
  if (request.type === 'element' && sender.tab) {
    const info = {
      tabTitle: sender.tab.title,
      tabUrl: sender.tab.url,
      // favIconUrl: sender.tab.favIconUrl,// chrome 与 firefox 不一致
      isFrame: sender.frameId !== 0,
      frameId: sender.frameId,
    }
    globalThis.activeElement = { ...request.data, ...info }
  }
  return true
}

// 这是一个处理帧的异步函数。它遍历给定的帧路径，并在每个帧上执行特定的操作。如果操作成功，它会将结果添加到iframeDepthInfo数组中，并更新位置参数p。如果操作失败，它会记录错误并返回活动元素。
async function processFrames(tab: chrome.tabs.Tab, framePath: number[], p: Point, activeElement: ElementInfo) {
  const iframeDepthInfo = []
  for (const frame of framePath) {
    try {
      const res = await Tabs.executeFuncOnFrame(tab.id, frame, (arg) => {
        // @ts-expect-error 插件content_script中的window对象
        return window.handleSync({
          key: 'getIframeElement',
          data: arg,
        })
      }, [p])

      iframeDepthInfo.push(res)
      const { nextPos } = res as { nextPos: Point }
      p.x = nextPos.x
      p.y = nextPos.y
    }
    catch {
      return [activeElement]
    }
  }
  return iframeDepthInfo
}
// 获取iframe 元素的完整路径
async function getIframeElement(p: Point, activeElement: ElementInfo) {
  const tab = await Tabs.getActiveTab()
  const frames = await Tabs.getAllFrames(tab.id)
  const iframeElementInfo = JSON.parse(JSON.stringify(activeElement))

  let targetFrame = frames.find(frame => frame.frameId === activeElement.frameId)
  const framePath: number[] = []
  // 获取到 frame 相对于 父 frame 的位置
  while (targetFrame) {
    framePath.unshift(targetFrame.frameId)
    targetFrame = frames.find(frame => frame.frameId === targetFrame.parentFrameId)
  }
  const iframeDepthInfo = await processFrames(tab, framePath, p, activeElement)

  if (iframeDepthInfo.length > 0) {
    const lastElement = iframeDepthInfo[iframeDepthInfo.length - 1]
    const isPathEqual = lastElement.xpath === activeElement.xpath
    const isUrlEqual = lastElement.url === activeElement.url
    if (!isPathEqual || !isUrlEqual) {
      // 不一致，则把 activeElement 替换为 iframeDepthInfo 最后一个元素
      iframeDepthInfo[iframeDepthInfo.length - 1] = iframeElementInfo
    }

    // 拼接 xpath， cssSelector, pathDirs
    iframeDepthInfo.forEach((frameInfo, index) => {
      if (index === 0) {
        iframeElementInfo.iframeXpath = frameInfo.xpath
      }
      else {
        iframeElementInfo.iframeXpath = `${iframeElementInfo.iframeXpath}/$iframe$${frameInfo.xpath}`
      }
      // 计算 iframe contentRect
      if (frameInfo.iframeContentRect) {
        iframeElementInfo.rect.x += frameInfo.iframeContentRect.x
        iframeElementInfo.rect.y += frameInfo.iframeContentRect.y
      }
    })
    // width, height 无需重新计算
    // 重新计算 iframeElementInfo left, top, right, bottom,
    iframeElementInfo.rect.left = iframeElementInfo.rect.x
    iframeElementInfo.rect.top = iframeElementInfo.rect.y
    iframeElementInfo.rect.right = iframeElementInfo.rect.x + iframeElementInfo.rect.width
    iframeElementInfo.rect.bottom = iframeElementInfo.rect.y + iframeElementInfo.rect.height

    // 删除掉 iframeXpath 中的最后一个iframe
    iframeElementInfo.iframeXpath = iframeElementInfo.iframeXpath.split('/$iframe$').slice(0, -1).join('/$iframe$')

    return iframeElementInfo
  }
  else {
    return activeElement
  }
}
// url 匹配 iframe
function findFrameByUrl(frames: FrameDetails[], url: string) {
  return frames.find(frame => frame.url.includes(url))
}
/**
 * 根据 iframeXpath 逐级在 frames 中解析并返回最内层 frame。
 * iframeXpath 形如： "xpathA/$iframe$xpathB/$iframe$xpathC"
 *
 * 逻辑：
 * 1. 拆分路径片段（过滤空字符串，兼容首尾/重复分隔符）
 * 2. 从顶层 frame(frameId = 0) 开始，逐级在 frames 中寻找 parentFrameId = 当前层 frameId 且 iframeXpath 匹配的子 frame
 * 3. 任一层未命中返回 null，全部命中返回最后一层 frame
 */
function findFrameByXpath(frames: FrameDetails[], iframeXpath: string) {
  if (!iframeXpath || !Array.isArray(frames) || frames.length === 0)
    return null

  const segments = iframeXpath
    .split('/$iframe$')
    .map(s => s.trim())
    .filter(Boolean)
  if (segments.length === 0)
    return null

  const rootFrame = frames.find(f => f.frameId === 0)
  if (!rootFrame)
    return null

  // 逐级下钻
  let current: FrameDetails | null = rootFrame
  for (const seg of segments) {
    // 在同级中寻找 iframeXpath = seg 且 parentFrameId = current.frameId 的子 frame
    const next = frames.find(f => f.iframeXpath === seg && f.parentFrameId === current!.frameId)
    if (!next)
      return null
    current = next
  }
  return current
}
// 获取 iframe 路径
function getFramePath(frames: FrameDetails[], targetFrame: FrameDetails) {
  const framePath: FrameDetails[] = []
  while (targetFrame) {
    framePath.unshift(targetFrame)
    targetFrame = frames.find(frame => frame.frameId === targetFrame.parentFrameId)
  }
  return framePath
}
// 计算 iframe 的绝对位置
async function calculateAbsolutePosition(tabId: number, framePath: FrameDetails[]) {
  const posPromises = framePath.slice(0, -1).map((frame, index) => {
    const nextFrame = framePath[index + 1]
    const args = [{
      iframeXpath: nextFrame.iframeXpath,
      url: nextFrame.url,
    }]
    return Tabs.executeFuncOnFrame(tabId, frame.frameId, (arg) => {
      // @ts-expect-error 插件content_script中的window对象
      return window.handleSync({
        key: 'getFramePosition',
        data: arg,
      })
    }, args)
  })

  const posRes = await Promise.all(posPromises) as Point[]
  return posRes.reduce(
    (acc, pos) => {
      acc.x += pos.x
      acc.y += pos.y
      return acc
    },
    { x: 0, y: 0 },
  )
}
// 调整 iframe 元素的位置, 支持数组
function adjustPosition(rect: DOMRectT | DOMRectT[], absolutePos: Point) {
  if (Array.isArray(rect)) {
    rect.forEach(r => adjustRectPosition(r, absolutePos))
  }
  else {
    adjustRectPosition(rect, absolutePos)
  }
}
// 调整 iframe 元素的位置
function adjustRectPosition(rect: DOMRectT, absolutePos: Point) {
  rect.x += absolutePos.x
  rect.y += absolutePos.y
  rect.left = rect.x
  rect.top = rect.y
  rect.right = rect.x + rect.width
  rect.bottom = rect.y + rect.height
}

// 找到对应的frame
async function findTabAndFrame(params: ElementParams) {
  const { url, iframeXpath, isFrame, tabUrl } = params.data
  let tab = await Tabs.getActiveTab()
  if (!tab) {
    tab = await Tabs.activeTargetTabByTabUrl(tabUrl)
    if (!tab) {
      throw new Error('未找到活动标签页')
    }
  }
  if (!isFrame) {
    return { tab, frameId: 0 }
  }
  else {
    const frames = await Tabs.getAllFrames(tab.id)
    const targetFrame = iframeXpath ? findFrameByXpath(frames, iframeXpath) : findFrameByUrl(frames, url)
    if (targetFrame) {
      return { tab, frameId: targetFrame.frameId }
    }
    else {
      return { tab, frameId: Number.NaN }
    }
  }
}

const Handlers = {
  version: '5.1.7',
  tabsHandler() {
    return {
      // 重载
      async reloadTab() {
        const res = await Tabs.reload()
        return Utils.success(res)
      },
      // 停止加载
      async stopLoad() {
        const res = await Tabs.stopLoad()
        return Utils.success(res)
      },
      // 打开新tab
      async openNewTab(params) {
        const tab = await Tabs.create(params.data)
        return Utils.success(tab)
      },
      // 关闭tab
      async closeTab(params) {
        let { url, id } = params.data
        let tab: chrome.tabs.Tab
        if (id && typeof id !== 'number') {
          try {
            id = Number.parseInt(id, 10)
            if (Number.isNaN(id)) {
              return Utils.fail('id 必须是数字')
            }
          }
          catch {
            return Utils.fail('id 必须是数字')
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
      // 更新tab
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
      // 激活tab
      async activeTab(params) {
        const { url } = params.data
        const tab = await Tabs.getTab(url)
        await Tabs.activeTargetTab(tab.id)
        return Utils.success(true)
      },
      // 获取当前活动tab
      async getActiveTab() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        return Utils.success(tab)
      },
      // 切换tab
      async switchTab(params) {
        let { url, title, id } = params.data
        if (id && typeof id !== 'number') {
          try {
            id = Number.parseInt(id, 10)
            if (Number.isNaN(id)) {
              return Utils.fail('id 必须是数字')
            }
          }
          catch {
            return Utils.fail('id 必须是数字')
          }
        }
        const tab = await Tabs.switchTab(url, title, id)
        if (tab) {
          return Utils.success(tab)
        }
        else {
          return Utils.fail('未找到标签页')
        }
      },
      // 获取所有tab
      async getAllTabs() {
        const tabs = await Tabs.getAllTabs()
        return Utils.success(tabs)
      },
      // 前进后退
      async backward() {
        const res = await Tabs.goBack()
        return Utils.success(res)
      },
      async forward() {
        const res = await Tabs.goForward()
        return Utils.success(res)
      },
      // 窗口最大化 最小化
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
      // 执行代码
      async executeScriptOnFrame(params) {
        const { url, code } = params.data
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        const frames = await Tabs.getAllFrames(tab.id)
        const frame = frames.find(frame => frame.url === url)
        const frameId = frame ? frame.frameId : 0
        const res = await Tabs.executeScriptOnFrame(tab.id, frameId, code)
        return Utils.success(res)
      },
      // 获取标题
      async getTitle() {
        const title = await Tabs.getTitle()
        return Utils.success(title)
      },
      // 获取url
      async getUrl() {
        const title = await Tabs.getUrl()
        return Utils.success(title)
      },
      // 获取截屏
      async captureScreen() {
        const res = await Tabs.captureScreen()
        if (res) {
          return Utils.success(res)
        }
      },
      // 截取页面截图
      async capturePage() {
        const res = await Tabs.capturePage()
        if (res) {
          return Utils.success(res)
        }
      },
      // 加载是否完成
      async loadComplete() {
        const { lastError } = chrome.runtime
        const activeTab = await Tabs.getActiveTab()
        if (!activeTab) {
          return Utils.fail('未找到活动标签页')
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
      // 获取所有frame
      async getFrames() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        const frames = await Tabs.getAllFrames(tab.id)
        return frames
      },
      async getExtFrames() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        const frames = await Tabs.getExtFrames(tab.id)
        return frames
      },
      // 重置缩放
      async resetZoom() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        const res = await Tabs.resetZoom(tab.id)
        return res
      },
      // 获取tabId
      async getTabId() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        return Utils.success(tab.id)
      },
    }
  },

  elementHandler() {
    return {
      // 获取元素内容
      async getElement(params) {
        const activeElement = globalThis.activeElement
        if (activeElement && activeElement.isFrame) {
          /**
           * frame 中的元素, 需要通过位置确定具体是哪一个 frame
           * 通过位置 x,y 从顶层frame 开始查找
           * 通过 frameId ， parentFrameId 来获取 frame 的层级关系
           * 然后逐层 减去iframe 的位置得到 新的x,y 再发送到对应的iframe 获取元素位置，还是iframe 的话就继续递归
           * 直到找到具体的元素 与 activeElement 的属性相同，则认为是目标元素
           */
          const { x, y } = params.data
          if (!x || !y) {
            return Utils.success(activeElement)
          }
          const result = await getIframeElement({ x, y }, activeElement)
          return Utils.success(result)
        }
        return Utils.success(activeElement)
      },
      async handleInContent(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.fail('未找到元素对应的iframe', StatusCode.ELEMENT_NOT_FOUND)
        }
        if (!Utils.isSupportProtocal(tab.url)) {
          return Utils.fail(`${tab.url} 当前标签页不支持web拾取协议`)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        if (result.code !== StatusCode.SUCCESS) {
          return Utils.fail(result.msg, result.code)
        }
        else {
          return Utils.success(result.data)
        }
      },
      // 获取元素位置相对浏览器网页窗口左上角的位置
      async getElementPos(params: ElementParams) {
        const { url, isFrame, iframeXpath, tabUrl } = params.data
        let tab = await Tabs.getActiveTab()
        if (!tab) {
          tab = await Tabs.activeTargetTabByTabUrl(tabUrl)
        }
        if (!Utils.isSupportProtocal(tab.url)) {
          return Utils.fail(`${tab.url} 当前标签页不支持web拾取协议`)
        }
        if (!isFrame) {
          const result = await Tabs.sendTabFrameMessage(tab.id, params, 0)
          return Utils.result(result.data, result.msg, result.code)
        }

        const frames = await Tabs.getAllFrames(tab.id)
        const targetFrame = iframeXpath ? findFrameByXpath(frames, iframeXpath) : findFrameByUrl(frames, url)

        if (!targetFrame) {
          return Utils.fail('未找到元素对应的iframe', StatusCode.ELEMENT_NOT_FOUND)
        }

        const framePath = getFramePath(frames, targetFrame)

        const absolutePos = await calculateAbsolutePosition(tab.id, framePath)

        const elementPosResult = await Tabs.sendTabFrameMessage(tab.id, params, targetFrame.frameId)

        if (elementPosResult.code !== StatusCode.SUCCESS) {
          return Utils.fail(elementPosResult.msg, elementPosResult.code)
        }

        adjustPosition(elementPosResult.data.rect, absolutePos)

        return Utils.success(elementPosResult.data)
      },
      // 校验元素
      async checkElement(params: ElementParams) {
        const res = await Handlers.elementHandler().getElementPos(params)
        return res
      },
      // 使元素可见
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
      // 相似元素
      async similarElement(params: ElementParams) {
        let activeElement = globalThis.activeElement
        const { tabUrl } = params.data
        let activeTab = await Tabs.getActiveTab()
        if (!activeTab) {
          return Utils.fail('未找到活动标签页')
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
            console.log('reSimilarElement result: ', res)
            if (res.data) {
              params.data = res.data.preData
              activeElement = res.data
              delete params.data.preData
            }
          }
          const similarElementInfo = getSimilarElement(params.data, activeElement)
          if (similarElementInfo) {
            // 获取相似元素个数
            const res = await Handlers.elementHandler().handleInContent({
              ...params,
              data: similarElementInfo,
            })
            similarElementInfo.similarCount = res.data?.similarCount || 0
            return Utils.success(similarElementInfo)
          }
          else {
            return Utils.fail('该元素不是相似元素', StatusCode.ELEMENT_NOT_FOUND)
          }
        }
        catch (error) {
          return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
        }
      },
      // 根据元素信息获取到元素信息
      async elementFromSelect(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 当前元素是否存在
      async elementIsRender(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
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
      // 当前元素是否存在, 网页加载完成
      async elementIsReady(params: ElementParams) {
        const activeTab = await Tabs.getActiveTab()
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.success(false)
        }
        params.key = 'elementIsRender'
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        const complete = activeTab.status === 'complete'
        if (result) {
          return Utils.success(result.data && complete)
        }
        else {
          return Utils.success(false)
        }
      },
      // 元素是否是table
      async elementIsTable(params: ElementParams) {
        if (!params.data.xpath) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const isTable = !!res.data
        const elementResult = { isTable, ...params.data }
        return Utils.success(elementResult)
      },
      // table 数据抓取
      async tableDataBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          // 如果不存在xpath不存在元素
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const values = res.data?.values || []
        const dataTable = new DataTable(res.data, values, 'table') // 创建table对象
        const table = dataTable.getTable()
        return Utils.success(table)
      },
      // table 列抓取
      async tableColumnDataBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          // 如果不存在xpath不存在元素
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const value = res.data?.value || []
        const dataTable = new DataTable(res.data, value, 'similar') // 以 similar 方式创建table对象
        const table = dataTable.getTable()
        return Utils.success(table)
      },
      // 相似元素抓取
      async similarBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          // 如果不存在xpath不存在元素
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
        const dataTable = new DataTable(res.data, value, 'similar') // 创建table对象
        const table = dataTable.getTable()
        return Utils.success(table)
      },
      // 表头抓取
      async tableHeaderBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          // 如果不存在xpath不存在元素
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 相似元素抓取数据
      async simalarListBatch(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 元素高亮列
      async highLightColumn(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 获取抓取数据
      async getBatchData(params: { key: string, data: BatchElementParams }) {
        if (params.data?.openSourcePage) {
          const activeTab = await Tabs.getActiveTab()
          if (!activeTab || activeTab.url !== params.data.tabUrl) {
            await Tabs.openTab(params.data.tabUrl)
          }
        }
        // 等待 3s
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
      // 元素截图
      async elementShot(params: ElementParams) {
        // 1,网页滚动到最顶部,2,网页缩放重置,3,获取元素位置大小,4,开启debugger,5,截图, 6,关闭debugger, 7,返回图片数据
        params.key = 'scrollToTop'
        await Handlers.elementHandler().scrollToTop(params)
        await Handlers.tabsHandler().resetZoom()
        params.key = 'getElementPos'
        const res = await Handlers.elementHandler().getElementPos(params)
        const { x, y, width, height } = res.data?.rect
        const data = await Tabs.captureElement({ x, y, width, height })
        return Utils.success(data)
      },
      // 滚动到顶部
      async scrollToTop(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return Utils.success(res)
      },
      // 迭代相似元素，支持单个/批量获取相似元素对象
      async getSimilarIterator(params: ElementParams) {
        params.key = 'elementFromSelect'
        const index = params.data?.index || 0 // 默认从第0个开始
        const count = params.data?.count || 1 // 默认获取一个
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
          return Utils.fail('未找到相似元素')
        }
      },
      // 获取关联元素，通过元素信息获取子元素/父元素/兄弟元素
      async getRelativeElement(params: ElementParams) {
        const { relativeOptions } = params.data
        if (!relativeOptions) {
          return Utils.fail('关联元素参数错误')
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 通过xpath/css选择器获取元素
      async generateElement(params: { key: string, data: GenerateParamsT }) {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail('未找到活动标签页')
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, 0)
        return result
      },
      // 点击元素
      async clickElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 输入
      async inputElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 获取文本
      async getElementText(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 获取属性
      async getElementAttrs(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 移除属性
      async removeElementAttr(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 设置属性
      async setElementAttr(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 获取checked
      async getElementChecked(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 设置checked
      async setElementChecked(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 获取selected
      async getElementSelected(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 设置selected
      async setElementSelected(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 获取 表格数据
      async getTableData(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
      // 滚动元素
      async scrollWindow(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
    }
  },

  jsHandler() {
    return {
      // 执行js 代码
      async runJS(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.fail('未找到元素对应的iframe', StatusCode.ELEMENT_NOT_FOUND)
        }
        await Tabs.getAllFrames(tab.id)
        try {
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

  noHandler() {
    return Utils.fail('暂未实现')
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
        // 相似抓取对象格式与元素格式不一致，在此处做参数兼容
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
    else {
      result = handlers.noHandler()
      return result
    }
  }
  catch (error) {
    return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
  }
}

export { bgHandler, contentMessageHandler, Handlers }
