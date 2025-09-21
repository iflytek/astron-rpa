import { DEEP_SEARCH_TRIGGER, ELEMENT_SEARCH_TRIGGER, HIGH_LIGHT_BORDER, HIGH_LIGHT_DURATION, SCROLL_DELAY, SCROLL_TIMES, StatusCode } from './constant'
import { similarBatch, similarListBatch, tableColumnDataBatch, tableDataBatch, tableDataFormatterProcure, tableHeaderBatch } from './dataBatch'
import {
  checkElements,
  findElementByPoint,
  getBoundingClientRect,
  getChildElementByType,
  getElementByElementInfo,
  getElementBySelector,
  getElementDirectory,
  getElementsByXpath,
  getIFramesElements,
  getIframeTransform,
  getNthCssSelector,
  getSiblingElementByType,
  getText,
  getWindowFrames,
  getXpath,
  isTable,
  shadowRootElement,
} from './element'
import { sendElementData } from './message'
import { Utils } from './utils'
import { elementChangeWatcher } from './watcher'

let timeoutId: number | null
let deepTimeoutId: number | null
let highlightTime = 0
const frontCheckEnabled = false // 是否启用前端检验框
let deepSearchEnabled = false // 是否启用深度搜索
let currentFrameInfo = {
  frameId: 0,
  iframeXpath: '',
  iframeTransform: {
    scaleX: 1,
    scaleY: 1,
  },
}

function findElement(ev: MouseEvent, docu: Document | ShadowRoot, _extra) {
  if (typeof findElementByPoint !== 'function') {
    return
  }
  const { clientX: x, clientY: y } = ev
  let element = findElementByPoint({ x, y }, deepSearchEnabled, docu)
  if (!element) {
    element = ev.target as HTMLElement // 修复找不到html元素的问题
  }
  let shadowPath = ''
  let shadowDirs: ElementDirectory[] = []
  // shadowRoot存在时，获取shadowRoot中的元素
  if (element?.shadowRoot) {
    const shadowRoot = element?.shadowRoot
    const shadowElementPath = getNthCssSelector(element)
    const result = shadowRootElement({ x, y }, shadowRoot, shadowElementPath)
    if (result) {
      element = result.element
      shadowPath = result.path
      shadowDirs = result.dirs
    }
    docu = shadowRoot
  }
  if (element) {
    const elementData = formatElementInfo(element, docu, shadowPath, shadowDirs)
    sendElementData(elementData)
    frontCheckEnabled && checkElements([element])
  }
}

/* 鼠标事件 */
function moveListener(ev: MouseEvent, docu: Document | ShadowRoot, extra) {
  timeoutId && clearTimeout(timeoutId)
  deepTimeoutId && clearTimeout(deepTimeoutId)

  timeoutId = setTimeout(() => {
    findElement(ev, docu, extra)
    clearTimeout(timeoutId)
    // DEEP_SEARCH_TRIGGER 秒后，开启深度搜索
    deepTimeoutId = setTimeout(() => {
      deepSearchEnabled = true
      findElement(ev, docu, extra)
      deepSearchEnabled = false
      clearTimeout(deepTimeoutId)
    }, DEEP_SEARCH_TRIGGER)
  }, ELEMENT_SEARCH_TRIGGER)
}
/* 元素信息 */
function formatElementInfo(element: HTMLElement, target: Document | ShadowRoot, shadowPath = '', shadowDirs: ElementDirectory[] = []) {
  // 获取元素的xpath
  const xpath = getXpath(element)
  // 获取元素的cssSelector
  const cssSelector = getNthCssSelector(element)
  // 获取元素的目录
  const pathDirs = getElementDirectory(element)
  const selector = shadowPath ? `${shadowPath}>$shadow$>${cssSelector}` : cssSelector
  const dirs = shadowDirs.length > 0 ? shadowDirs.concat([{ tag: '$shadow$', checked: true, value: '$shadow$', attrs: [] }], pathDirs) : pathDirs
  const tag = Utils.getTag(element)
  const innerText = Utils.pureText(getText(element)).substring(0, 10) // 获取元素名称
  const text = innerText ? Utils.pureText(innerText) : '未知名称'
  const elementData = {
    matchTypes: [],
    checkType: 'shadowRoot' in target ? 'customization' : 'visualization', // 获取元素类型，可视化获取 / 自定义获取
    xpath,
    cssSelector: selector,
    pathDirs: dirs,
    rect: getBoundingClientRect(element), // 仅作为拾取元素时的高亮
    url: window.location.href,
    shadowRoot: target instanceof ShadowRoot,
    tag,
    text,
  }
  return elementData
}

/* iframe 消息处理 */
function messageHandler(ev: MessageEvent) {
  const { key, data } = ev.data
  if (data && key === 'setIflyrpaIframe') {
    currentFrameInfo = data
  }
  if (key === 'getIflyrpaIframe') {
    tagFrame()
  }
}
/* 标记iframe */
function tagFrame() {
  const iframes = getIFramesElements()
  iframes.forEach((iframe) => {
    const iframeInfo = {
      iframeXpath: getXpath(iframe),
      iframeTransform: getIframeTransform(iframe),
    }
    iframe.contentWindow?.postMessage(
      {
        key: 'setIflyrpaIframe',
        data: iframeInfo,
      },
      '*',
    )
  })
  if (window.parent !== window) {
    // 非顶层frame
    // 向父窗口发送消息
    window.parent.postMessage(
      {
        key: 'getIflyrpaIframe',
      },
      '*',
    )
  }
}

/**
 * 滚动查找元素，如果找不到，则滚动查找
 * 最多滚动20次当前窗口高度
 * SCROLL_TIMES = 20 最大滚动次数
 * SCROLL_DELAY = 1500ms //单次滚动后等待页面加载的时间
 */
async function scrollFindElement(data: ElementInfo) {
  const windowHeight = window.innerHeight
  let count = 1

  while (count <= SCROLL_TIMES) {
    window.scrollTo(window.scrollX, count * windowHeight)
    await new Promise(resolve => setTimeout(resolve, SCROLL_DELAY))
    const eles = getElementByElementInfo(data)
    if (eles) {
      return eles
    }
    count++
  }
  console.warn('Element lookup failed after maximum scroll attempts:', data)
  return null
}

/**
 * 元素未找到原因，变动的元素节点
 */

function elementNotFoundReason(data: ElementInfo) {
  const { checkType } = data
  if (!data.cssSelector && !data.xpath && checkType === 'customization') {
    return Utils.fail('元素信息不完整，无法定位元素', StatusCode.ELEMENT_NOT_FOUND)
  }
  if (data.pathDirs && data.pathDirs.length === 0 && checkType === 'visualization') {
    return Utils.fail('元素信息不完整，无法定位元素', StatusCode.ELEMENT_NOT_FOUND)
  }
  let message = '未找到元素'
  const result = elementChangeWatcher(data)
  if (!result.found) {
    message = `元素在第${result.notFoundIndex}节点${result.notFoundStep}处发生变动`
  }
  return Utils.fail(message, StatusCode.ELEMENT_NOT_FOUND)
}

/**
 * 统一的鼠标事件派发
 */
function dispatchMouseSequence(
  dom: HTMLElement,
  events: string[],
  coords?: { clientX?: number, clientY?: number },
) {
  const base: MouseEventInit = {
    bubbles: true,
    cancelable: true,
    view: window,
    clientX: coords?.clientX ?? 0,
    clientY: coords?.clientY ?? 0,
  }
  for (const type of events) {
    // 微任务后派发，避免同步链路里阻塞
    queueMicrotask(() => dom.dispatchEvent(new MouseEvent(type, base)))
  }
}

const ContentHandler = {
  version: '5.1.7',
  ele: {
    /**
     * 通过 元素的xpath，cssSelector，目录，查找元素
     */
    getElement: async (data: ElementInfo, isSelf = false, atomRun = false): Promise<null | HTMLElement[]> => {
      const { matchTypes } = data
      const isScrollFind = matchTypes && matchTypes.includes('scrollPosition') && !isSelf && !atomRun
      let tempEles: HTMLElement[] | null = getElementByElementInfo(data)
      if (!tempEles && isScrollFind) {
        tempEles = (await scrollFindElement(data)) as HTMLElement[]
      }
      return tempEles as HTMLElement[] // 多元素
    },
    // 获取单个dom
    getDom: async (data: ElementInfo): Promise<HTMLElement | null> => {
      const eles = await ContentHandler.ele.getElement(data)
      const result = eles ? eles[0] : null
      return result
    },
    // 校验元素位置
    checkElement: async (data: ElementInfo) => {
      let checkEles = null
      try {
        checkEles = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      frontCheckEnabled && checkEles && checkElements(checkEles)
      if (checkEles && checkEles.length === 1) {
        const elementPos = getBoundingClientRect(checkEles[0])
        return Utils.success({ rect: [elementPos] }) // 单元素
      }
      else if (checkEles && checkEles.length > 1) {
        const elementPosArr = checkEles.map((ele: HTMLElement) => {
          return getBoundingClientRect(ele)
        })
        return Utils.success({ rect: elementPosArr }) // 多元素
      }
      else {
        return elementNotFoundReason(data)
      }
    },
    // 获取到元素的位置信息
    getElementPos: async (data: ElementInfo) => {
      let checkEle = null
      try {
        checkEle = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (checkEle && checkEle[0]) {
        const elementPos = getBoundingClientRect(checkEle[0])
        return Utils.success({ rect: elementPos })
      }
      else {
        return elementNotFoundReason(data)
      }
    },
    // 滚动到可视区域
    scrollIntoView: async (data: ElementInfo) => {
      const { matchTypes } = data
      let scrollEle: HTMLElement[] | null
      try {
        scrollEle = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (scrollEle && scrollEle[0]) {
        scrollEle[0].scrollIntoView({
          behavior: 'instant', // 立即滚动
          block: 'center',
        })
        return Utils.success(true)
      }
      else {
        const isScrollFind = matchTypes && matchTypes.includes('scrollPosition')
        if (isScrollFind) {
          return elementNotFoundReason(data)
        }
        return elementNotFoundReason(data)
      }
    },
    // 获取元素信息
    elementFromSelect: async (data: ElementInfo) => {
      const { domain = location.origin, url = location.href, shadowRoot } = data
      let elements = null
      try {
        elements = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (elements && elements.length === 1) {
        const elementInfo = formatElementInfo(elements[0], document)
        return Utils.success([{ ...data, ...elementInfo, domain, shadowRoot, url }])
      }
      else if (elements && elements.length > 1) {
        const result = elements.map((ele: HTMLElement) => {
          const elementInfo = formatElementInfo(ele, document)
          return { ...data, ...elementInfo, domain, shadowRoot, url }
        })
        return Utils.success(result)
      }
      else {
        return elementNotFoundReason(data)
      }
    },
    // 元素是否存在
    elementIsRender: async (data: ElementInfo) => {
      let ele = null
      try {
        ele = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (ele) {
        return Utils.success(true)
      }
      else {
        return Utils.success(false)
      }
    },
    // 元素是否为表格
    elementIsTable: async (data: ElementInfo) => {
      let ele = null
      try {
        ele = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (ele && ele[0]) {
        const res = isTable(ele[0])
        return Utils.success(res)
      }
      else {
        return Utils.success(false)
      }
    },
    // 相似元素抓取
    similarBatch: (data: ElementInfo) => {
      try {
        const res = similarBatch(data)
        return Utils.success(res)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },
    // 表格数据抓取
    tableDataBatch: (data: ElementInfo) => {
      try {
        const res = tableDataBatch(data)
        return Utils.success(res)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },
    // 表格单列抓取
    tableColumnDataBatch: (data: ElementInfo) => {
      try {
        const res = tableColumnDataBatch(data)
        return Utils.success(res)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },

    // 表头抓取， 以相似元素模式抓取，仅抓取数据，不包含元素
    tableHeaderBatch: (data: ElementInfo) => {
      try {
        const res = tableHeaderBatch(data)
        return Utils.success(res)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },
    // 相似元素组抓取
    simalarListBatch: (data) => {
      try {
        const res = similarListBatch(data)
        return Utils.success(res)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },

    // 获取相似元素内容
    similarElement: async (data: ElementInfo) => {
      try {
        const eles = await ContentHandler.ele.getElement(data)
        return Utils.success({ similarCount: eles.length })
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },
    // 重塑相似元素，使用绝对路径
    reSimilarElement: async (data: ElementInfo) => {
      const preEles = await ContentHandler.ele.getElement(data.preData)
      const curEles = await ContentHandler.ele.getElement(data)
      if (preEles && curEles) {
        const preXpath = getXpath(preEles[0], true)
        const preSelector = getNthCssSelector(preEles[0], true)
        const prePathDirs = getElementDirectory(preEles[0], true)
        const preElementInfo = { ...data.preData, pathDirs: prePathDirs, xpath: preXpath, cssSelector: preSelector }
        const curXpath = getXpath(curEles[0], true)
        const curSelector = getNthCssSelector(curEles[0], true)
        const curPathDirs = getElementDirectory(curEles[0], true)
        const curElementInfo = { ...data, pathDirs: curPathDirs, xpath: curXpath, cssSelector: curSelector }
        return Utils.success({ ...curElementInfo, preData: preElementInfo })
      }
      else {
        return Utils.success(null)
      }
    },
    // 高亮 列
    highLightColumn: async (data: ElementInfo & { produceType: string, columnIndex: number }) => {
      if (highlightTime > 0)
        return Utils.success({ rect: [] }) // 防止重复高亮, 导致高亮框清除不掉
      highlightTime = HIGH_LIGHT_DURATION
      const { produceType, columnIndex } = data
      const highlightColor = Utils.generateColor(columnIndex ? columnIndex - 1 : 0)
      if (produceType === 'table') {
        const eles = await ContentHandler.ele.getElement(data)
        if (eles && eles.length > 0) {
          const ele = eles[0]
          const table = ele.closest('table')
          const rect = []
          const tds: { border: string, td: HTMLElement }[] = []
          const th = table.querySelector(`th:nth-child(${columnIndex})`) as HTMLElement | null
          const thborder = th?.style.border

          // 高亮表头
          if (th) {
            th.style.border = HIGH_LIGHT_BORDER
            th.style.borderColor = highlightColor
            rect.push(getBoundingClientRect(th))
          }

          // 高亮列单元格
          table.querySelectorAll('tr').forEach((tr) => {
            const td = tr.querySelector(`td:nth-child(${columnIndex})`) as HTMLElement | null
            if (td) {
              const border = td.style.border
              td.style.border = HIGH_LIGHT_BORDER
              td.style.borderColor = highlightColor
              tds.push({ border, td })
              rect.push(getBoundingClientRect(td))
            }
          })

          // 恢复
          setTimeout(() => {
            highlightTime = 0
            if (th)
              th.style.border = thborder
            tds.forEach(({ td, border }) => {
              td.style.border = border
            })
          }, HIGH_LIGHT_DURATION)

          return Utils.success({ rect })
        }
        else {
          highlightTime = 0
          return elementNotFoundReason(data)
        }
      }
      else {
        const eles = await ContentHandler.ele.getElement(data)
        if (eles && eles.length > 0) {
          const rect = []
          const simiEles = []
          eles.forEach((ele) => {
            const border = ele.style.border
            ele.style.border = HIGH_LIGHT_BORDER
            ele.style.borderColor = highlightColor
            simiEles.push({
              border,
              ele,
            })
            rect.push(getBoundingClientRect(ele))
          })
          setTimeout(() => {
            highlightTime = 0
            simiEles.forEach((simiItem) => {
              simiItem.ele.style.border = simiItem.border
            })
          }, HIGH_LIGHT_DURATION)
          return Utils.success({ rect })
        }
        else {
          highlightTime = 0
          return elementNotFoundReason(data)
        }
      }
    },
    scrollToTop: () => {
      window.scrollTo(0, 0)
      return true
    },
    // 获取关联元素
    getRelativeElement: async (data: ElementInfo) => {
      let ele: HTMLElement[]
      const options = data?.relativeOptions as Options
      // 获取当前元素
      try {
        ele = await ContentHandler.ele.getElement(data)
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (!ele) {
        return elementNotFoundReason(data)
      }
      if (ele.length > 1) {
        return Utils.fail('找到多个元素，无法唯一定位', StatusCode.EXECUTE_ERROR)
      }

      const { relativeType } = options
      // relativeType 为 child/parent/sibling
      let findEl
      try {
        if (relativeType === 'child') {
          findEl = getChildElementByType(ele[0], options)
        }
        if (relativeType === 'parent') {
          findEl = ele[0].parentElement
        }
        if (relativeType === 'sibling') {
          findEl = getSiblingElementByType(ele[0], options)
        }
        if (Array.isArray(findEl)) {
          const elsInfo = findEl.map((item) => {
            const info = formatElementInfo(item, document)
            const mergeInfo = { ...data, ...info }
            delete mergeInfo.rect
            delete mergeInfo.text
            delete mergeInfo.relativeOptions
            return mergeInfo
          })
          return Utils.success(elsInfo)
        }
        else if (findEl) {
          const info = formatElementInfo(findEl, document)
          const elInfo = { ...data, ...info }
          delete elInfo.rect
          delete elInfo.text
          delete elInfo.relativeOptions
          return Utils.success(elInfo)
        }
        else {
          return elementNotFoundReason(data)
        }
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
    },
    // 生成元素对象
    generateElement: (data: GenerateParamsT) => {
      const { type, value } = data
      let eles = null
      try {
        if (type === 'xpath') {
          eles = getElementsByXpath(value)
        }
        if (type === 'cssSelector') {
          eles = getElementBySelector(value)
        }
      }
      catch (error) {
        return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
      }
      if (eles && eles.length > 0) {
        const elementInfo = eles.map((item) => {
          const obj = formatElementInfo(item, document)
          const pureElementInfo = Utils.pureObject(obj, ['xpath', 'cssSelector', 'url', 'shadowRoot'])
          Object.assign(pureElementInfo, { checkType: 'customization', matchTypes: [] })
          return pureElementInfo
        })
        const result = elementInfo.length > 1 ? elementInfo : elementInfo[0]
        return Utils.success(result)
      }
      else {
        return Utils.fail('未找到元素', StatusCode.ELEMENT_NOT_FOUND)
      }
    },

    // ---v3 声明式原子能力
    // 点击元素
    clickElement: async (data: ElementInfo) => {
      const result = await ContentHandler.ele.getDom(data)
      const { buttonType } = data.atomConfig
      if (!result)
        return elementNotFoundReason(data)

      try {
        switch (buttonType) {
          case 'right':
            dispatchMouseSequence(result, ['mousedown', 'mouseup', 'contextmenu'])
            break
          case 'dbclick':
            dispatchMouseSequence(result, ['mousedown', 'mouseup', 'click', 'mousedown', 'mouseup', 'click', 'dblclick'])
            break
          case 'click':
          default:
            dispatchMouseSequence(result, ['mousedown', 'mouseup', 'click'])
        }
      }
      catch (e) {
        return Utils.fail(`点击元素失败: ${e}`, StatusCode.EXECUTE_ERROR)
      }
      return Utils.success(true)
    },

    // input元素输入文本
    inputElement: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data)) as HTMLInputElement | HTMLTextAreaElement
      const { inputText } = data.atomConfig
      if (result) {
        if (result.tagName !== 'INPUT' && result.tagName !== 'TEXTAREA') {
          return Utils.fail('该元素不是原生输入元素', StatusCode.EXECUTE_ERROR)
        }
        result.value = inputText
        return Utils.success(true)
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 获取元素的text
    getElementText: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data))
      if (result) {
        if (result.tagName === 'INPUT' || result.tagName === 'TEXTAREA') {
          return Utils.success((result as HTMLInputElement).value)
        }
        else {
          const text = getText(result)
          return Utils.success(text)
        }
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 获取元素的属性
    getElementAttrs: async (data: ElementInfo) => {
      const result = await ContentHandler.ele.getDom(data)
      const { operation, attrName } = data.atomConfig
      if (result) {
        let value = null
        switch (operation) {
          case '0':
            value = getText(result) // 获取元素文本内容
            break
          case '1':
            value = result.outerHTML // 获取元素源代码
            break
          case '2':
            value = (result as HTMLInputElement).value || result.getAttribute('value') // 获取元素值
            break
          case '3':
            value = (result as HTMLImageElement).src || (result as HTMLAnchorElement).href || '' // 获取元素链接地址
            break
          case '4':
            value = result.getAttribute(attrName) || '' // 获取元素属性
            break
          case '5':
            value = getBoundingClientRect(result) // 获取元素位置
            break
          case '6':
            if (result.tagName !== 'INPUT') {
              return Utils.fail('元素无选中属性', StatusCode.EXECUTE_ERROR)
            }
            value = (result as HTMLInputElement).checked // 获取选框选中状态?
            break
          default:
            break
        }
        return Utils.success(value)
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 移除元素的属性
    removeElementAttr: async (data: ElementInfo) => {
      const result = await ContentHandler.ele.getDom(data)
      const { attrName } = data.atomConfig
      if (result) {
        result.removeAttribute(attrName)
        return Utils.success(true)
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 设置元素的属性
    setElementAttr: async (data: ElementInfo) => {
      const result = await ContentHandler.ele.getDom(data)
      const { attrName, attrValue } = data.atomConfig
      if (result) {
        result.setAttribute(attrName, attrValue)
        return Utils.success(true)
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    //  获取checked 属性
    getElementChecked: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data)) as HTMLInputElement
      if (result) {
        if (result.type === 'checkbox' || result.type === 'radio') {
          return Utils.success(result.checked)
        }
        else {
          return Utils.fail('该元素不是原生选框元素', StatusCode.EXECUTE_ERROR)
        }
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 设置checked属性
    setElementChecked: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data)) as HTMLInputElement
      const { checked, reverse } = data.atomConfig
      if (result) {
        if (result.type === 'checkbox' || result.type === 'radio') {
          if (reverse) {
            result.click()
          }
          else {
            if (result.checked !== checked) {
              result.click()
            }
            result.checked = checked
          }
          return Utils.success(true)
        }
        else {
          return Utils.fail('该元素不是原生选框元素', StatusCode.EXECUTE_ERROR)
        }
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 获取select
    getElementSelected: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data)) as HTMLSelectElement
      const { option } = data.atomConfig
      if (result) {
        if (result.tagName !== 'SELECT') {
          return Utils.fail('该元素不是原生下拉框元素', StatusCode.EXECUTE_ERROR)
        }
        if (option === 'selected') {
          // 获取选中项
          const list = Array.from(result.selectedOptions).map((option) => {
            return {
              label: option.label || '',
              value: option.value || '',
            }
          })
          return Utils.success(list)
        }
        else {
          // 获取所有选项
          const list = Array.from(result.options).map((option) => {
            return {
              label: option.label || '',
              value: option.value || '',
            }
          })
          return Utils.success(list)
        }
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 设置select
    setElementSelected: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data)) as HTMLSelectElement
      const { value, pattern, indexValue } = data.atomConfig
      if (result) {
        if (result.tagName !== 'SELECT') {
          return Utils.fail('该元素不是原生下拉框元素', StatusCode.EXECUTE_ERROR)
        }
        const options = result.options
        for (let i = 0; i < options.length; i++) {
          // 模糊匹配
          if (pattern === 'contains' && options[i].label.includes(value)) {
            result.value = options[i].value
          }
          // 精确匹配
          if (pattern === 'equal' && options[i].label === value) {
            result.value = options[i].value
          }
          // indexValue 匹配
          if (pattern === 'index' && i + 1 === indexValue) {
            result.value = options[i].value
          }
          // 正则匹配 todo
        }
        result.dispatchEvent(new Event('change', { bubbles: true })) // 触发change事件
        return Utils.success(true)
      }
      else {
        return elementNotFoundReason(data)
      }
    },
    // 获取表格数据
    getTableData: async (data: ElementInfo) => {
      const result = (await ContentHandler.ele.getDom(data)) as HTMLTableElement
      if (result) {
        const res = tableDataFormatterProcure(result)
        return Utils.success(res)
      }
      else {
        return elementNotFoundReason(data)
      }
    },

    // 滚动
    scrollWindow: async (data: ElementInfo) => {
      let target: Window | HTMLElement = window
      if (data.xpath || data.cssSelector || data.pathDirs) {
        target = await ContentHandler.ele.getDom(data)
      }
      if (!target) {
        return elementNotFoundReason(data)
      }
      const { scrollTo, scrollAxis, scrollX = 0, scrollY = 0, scrollBehavior = 'instant' } = data.atomConfig
      if (scrollTo === 'top') {
        target.scrollTo({
          top: 0,
          behavior: scrollBehavior,
        })
      }
      if (scrollTo === 'left') {
        target.scrollTo({
          left: 0,
          behavior: scrollBehavior,
        })
      }
      if (scrollTo === 'bottom') {
        target.scrollTo({
          top: 99999,
          behavior: scrollBehavior,
        })
      }
      if (scrollTo === 'right') {
        target.scrollTo({
          left: 99999,
          behavior: scrollBehavior,
        })
      }
      if (scrollTo === 'custom' && scrollAxis === 'x') {
        target.scrollTo({
          left: scrollX,
          behavior: scrollBehavior,
        })
      }
      if (scrollTo === 'custom' && scrollAxis === 'y') {
        target.scrollTo({
          top: scrollY,
          behavior: scrollBehavior,
        })
      }
      return Utils.success(true)
    },
  },
  code: {
    runJS: (data: { code: string }) => {
      try {
        const { code } = data
        // eslint-disable-next-line no-new-func
        const res = new Function(code)()
        return Utils.success(res)
      }
      catch (e) {
        const errStr = `runJS ${e.toString()}`
        return Utils.fail(errStr, StatusCode.EXECUTE_ERROR)
      }
    },
  },
  frame: {
    getFrames: () => {
      const frames = getWindowFrames()
      return Utils.success(frames)
    },
    getFramePosition(data: { url: string, iframeXpath: string }) {
      const { url, iframeXpath } = data
      const frames = getWindowFrames()
      const frame = iframeXpath ? frames.find(item => item.xpath === iframeXpath) : frames.find(item => item.src.includes(url) || url.includes(item.src))
      if (frame) {
        return frame.rect
      }
      else {
        return { x: 0, y: 0, width: 0, height: 0, left: 0, top: 0, right: 0, bottom: 0 }
      }
    },
    getFrameInfo(data: { frameId: number }) {
      const { frameId } = data
      console.log(`rpa_debugger_on:${frameId}`) // !!! 请勿删除，依靠该代码确定 chrome.debugger 往哪个frame 注入
      tagFrame()
      currentFrameInfo.frameId = frameId
      return currentFrameInfo
    },
    /**
     * 通过坐标获取iframe元素，递进获取嵌套iframe
     */
    getIframeElement: (data: Point) => {
      const { x, y } = data
      const dpr = window.devicePixelRatio
      const realX = x / dpr
      const realY = y / dpr
      const iframeEle = document.elementFromPoint(realX, realY) as HTMLElement
      if (iframeEle) {
        const { left, top } = iframeEle.getBoundingClientRect()
        const borderLeft = Number.parseInt(window.getComputedStyle(iframeEle).borderLeftWidth)
        const borderTop = Number.parseInt(window.getComputedStyle(iframeEle).borderTopWidth)
        const paddingLeft = Number.parseInt(window.getComputedStyle(iframeEle).paddingLeft)
        const paddingTop = Number.parseInt(window.getComputedStyle(iframeEle).paddingTop)
        const nextPos = {
          x: (realX - left - borderLeft - paddingLeft) * dpr,
          y: (realY - top - borderTop - paddingTop) * dpr,
        }
        let iframeContentRect = null
        if (iframeEle.tagName === 'IFRAME' || iframeEle.tagName === 'FRAME') {
          iframeContentRect = {
            x: (left + borderLeft + paddingLeft) * dpr,
            y: (top + borderTop + paddingTop) * dpr,
          }
          tagFrame()
        }
        const iframeInfo = formatElementInfo(iframeEle, document)
        return { ...iframeInfo, nextPos, iframeContentRect }
      }
    },
    stopLoad() {
      window.stop()
      return true
    },
  },
  page: {
    /**
     *  from Mozilla Online
     */
    fullPageRect: () => {
      const rootScrollable = document.compatMode === 'BackCompat' ? document.body : document.documentElement
      const sizeLimit = 2 ** 13
      const zoomedSizeLimit = Math.floor(sizeLimit / window.devicePixelRatio)
      return {
        x: 0,
        y: 0,
        width: Math.min(rootScrollable.scrollWidth, zoomedSizeLimit),
        height: Math.min(rootScrollable.scrollHeight, zoomedSizeLimit),
      }
    },

    getDPR: () => {
      return { dpr: window.devicePixelRatio }
    },
  },
}

function executeHandler(key: string, data, isAsync: boolean = true) {
  if (ContentHandler.ele[key]) {
    return isAsync ? ContentHandler.ele[key](data) : ContentHandler.ele[key](data)
  }
  else if (ContentHandler.code[key]) {
    return ContentHandler.code[key](data)
  }
  else if (ContentHandler.frame[key]) {
    return ContentHandler.frame[key](data)
  }
  else if (ContentHandler.page[key]) {
    return ContentHandler.page[key](data)
  }
  else {
    return Utils.fail('暂不支持该功能')
  }
}
// 异步版本
async function handle(params) {
  const { key, data } = params
  return await executeHandler(key, data, true)
}
// 同步版本
function handleSync(params) {
  const { key, data } = params
  return executeHandler(key, data, false)
}
function RpaExtGetElement(data) {
  try {
    const eles = getElementByElementInfo(data)
    return eles ? eles[0] : null
  }
  catch (error) {
    throw new Error(error.toString())
  }
}

window.removeEventListener('message', messageHandler)
window.addEventListener('message', messageHandler)
// @ts-expect-error  挂载到 window 上
window.handle = handle
// @ts-expect-error  挂载到 window 上
window.handleSync = handleSync
// @ts-expect-error  挂载到 window 上
window.RpaExtGetElement = RpaExtGetElement
// @ts-expect-error  挂载到 window 上
window.currentFrameInfo = currentFrameInfo
tagFrame()
export { handle, moveListener }
