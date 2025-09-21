import type { SimilarDataType } from '../types/data_grab.d'

/**
 * 数据抓取
 */
import { getElementByElementInfo, getElementBySelector, getElementDirectory, getNthCssSelector, getXpath, textAttrFromElement } from './element'
import { Utils } from './utils'

/**
 * 通过xpath 计算元素个数
 */
function elementCountByXpath(xpath: string) {
  const similarResults = document.evaluate(`count(${xpath})`, document, null, XPathResult.NUMBER_TYPE, null)
  if (similarResults) {
    return similarResults.numberValue
  }
  else {
    return 0
  }
}
/**
 * 通过 cssSelector 计算元素个数
 */
function elementCountByCssSelector(cssSelector: string) {
  return getElementBySelector(cssSelector).length
}
/**
 * 通过xpath 探测出相似元素xpath
 */
function similarXpathByXpath(xpath: string) {
  let similarXpath = '' // 相似元素路径
  let similarCount = 0 // 相似元素数量
  // //*[@id="app"]/div/div/div[1]/div/div/section/ul/li[3]/ul/li[1]/span/a
  // 对xpath进行拆分
  const xpathArr = xpath.split('/')
  // 每个节点都进行相似度计算，记录相似度最高的节点， 该路径即为相似元素路径，并记录元素信息
  // 对存在[number]的节点进行去掉 [number]处理
  for (let i = xpathArr.length - 1; i >= 0; i--) {
    const tagValue = xpathArr[i].substring(xpathArr[i].indexOf('[') + 1, xpathArr[i].indexOf(']'))
    // 正则检验是数字
    if (/^\d+$/.test(tagValue)) {
      // 存在[number]
      const tag = xpathArr[i].split('[')[0]
      const prePath = xpathArr.slice(0, i).join('/')
      const nextPath = xpathArr.slice(i + 1).join('/')
      let currentXpath = `${prePath}/${tag}/${nextPath}`
      currentXpath = currentXpath.endsWith('/') ? currentXpath.slice(0, -1) : currentXpath
      const currentSimilatCount = elementCountByXpath(currentXpath)

      if (currentSimilatCount >= similarCount) {
        similarCount = currentSimilatCount
        similarXpath = currentXpath // 记录相似元素路径
      }
    }
  }
  return similarXpath
}
/**
 * 通过cssSelector 探测出相似元素cssSelector
 */
function similarCssSelectorByCssSelector(cssSelector: string) {
  let similarCssSelector = '' // 相似元素路径
  let similarCount = 0 // 相似元素数量
  // div > div > div > div > div > section > ul > li:nth-child(3) > ul > li:nth-child(1) > span > a
  // 对cssSelector进行拆分
  const cssSelectorArr = cssSelector.split('>')
  // 每个节点都进行相似度计算，记录相似度最高的节点， 该路径即为相似元素路径，并记录元素信息
  // 对存在:nth-child(number)的节点进行去掉 nth-child(number)处理
  for (let i = cssSelectorArr.length - 1; i >= 0; i--) {
    if (cssSelectorArr[i].includes(':nth-child')) {
      // 存在:nth-child(number)
      const tag = cssSelectorArr[i].split(':')[0]
      let currentCssSelector = `${cssSelectorArr.slice(0, i).join('>')}>${tag}>${cssSelectorArr.slice(i + 1).join('>')}`
      // currentCssSelector = currentCssSelector.endsWith('>') ? currentCssSelector.slice(0, -1) : currentCssSelector;
      currentCssSelector = currentCssSelector.trim() // 去掉空格
      // 去掉前后可能存在的 >
      currentCssSelector = currentCssSelector.startsWith('>') ? currentCssSelector.slice(1) : currentCssSelector
      currentCssSelector = currentCssSelector.endsWith('>') ? currentCssSelector.slice(0, -1) : currentCssSelector
      const currentSimilatCount = elementCountByCssSelector(currentCssSelector)
      if (currentSimilatCount >= similarCount) {
        similarCount = currentSimilatCount
        similarCssSelector = currentCssSelector // 记录相似元素路径
      }
    }
  }
  return similarCssSelector
}
/**
 * 通过 similarXpath 校验出 相似元素 pathDirs
 */
function similarPathDirsByXpath(pathDirs: ElementDirectory[], similarXpath?: string) {
  let similarXpathArr = similarXpath ? similarXpath.split('/') : []
  similarXpathArr = similarXpathArr.filter(item => item) // 过滤空字符串
  // 预处理 id, index text 属性
  const similarDirs = pathDirs.map((item, index) => {
    return {
      ...item,
      attrs: item.attrs.map((attr) => {
        if (attr.name === 'id' && index !== 0) {
          attr.checked = false
        }
        if (attr.name === 'text' || attr.name === 'innertext') {
          attr.checked = false
        }
        return attr
      }),
    }
  })
  similarDirs.forEach((item, index) => {
    // 获取similarXpathArr[index] 中的 [number] 或者 [position()=number] 或者 [@id=value]
    const xpathItem = similarXpathArr[index]
    const num = xpathItem ? xpathItem.match(/\[(\d+)\]/)?.[1] : null
    item.attrs.forEach((attr) => {
      if (attr.name === 'index') {
        attr.checked = !!num
        attr.value = num || ''
      }
    })
  })
  return similarDirs
}

/**
 * 根据xpath 修改 pathDirs， 忽略掉无用的属性，保留有用的属性
 */
function pathDirsByXpath(pathDirs: ElementDirectory[], xpath: string) {
  const xpathArr = xpath.split('/').reverse() // 逆序 ,方便从子节点开始修改
  const pathDirsArr = pathDirs.reverse() //  逆序
  let index = 0
  while (index < pathDirsArr.length) {
    const xpathItem = xpathArr[index]
    pathDirsArr[index].attrs.forEach((attr) => {
      attr.checked = false
    })
    // 如果xpathItem 中有 [number] 属性
    const number = xpathItem.match(/\[(\d+)\]/)?.[1]
    const tag = xpathItem.split('[')[0]
    if (tag === '*') {
      pathDirsArr[index].tag = '*'
      pathDirsArr[index].value = '*'
    }
    // 如果xpathItem 中有 [position()=number] 属性,取出 number
    const positionNumber = xpathItem.match(/position\(\)=\d+/)?.[0].match(/\d+/)?.[0]
    if (number || positionNumber) {
      pathDirsArr[index].attrs.forEach((attr) => {
        if (attr.name === 'index') {
          attr.checked = true
          attr.value = number || positionNumber
        }
      })
    }
    // 如果xpathItem 中有 [@id=value] 属性,取出value
    const id = xpathItem.match(/@id=['"](.*)['"]/)?.[1]
    if (id) {
      pathDirsArr[index].attrs.forEach((attr) => {
        if (attr.name === 'id') {
          attr.checked = true
          attr.value = id
        }
      })
    }
    index += 1
  }
  return pathDirsArr.reverse()
}
/**
 * 相似元素抓取数据
 */
function similarDataBatch(params: ElementInfo) {
  const value: SimilarDataValueT[] = []
  const similarElementData = { ...params, value, value_type: params.value_type || 'text' }
  similarElementData.rect && delete similarElementData.rect
  similarElementData.tag && delete similarElementData.tag
  similarElementData.text && delete similarElementData.text
  const eles = getElementByElementInfo(params)
  const elements = eles ? Array.from(eles) : null
  if (!elements) {
    return similarElementData
  }
  else {
    let node = null

    let index = 0
    while (index <= elements.length - 1) {
      node = elements[index]
      index += 1
      const textItem = textAttrFromElement(node as HTMLElement)
      value.push(textItem)
    }
    // 处理一下 value 如果text 都为空，则取attrs中都存在值的那一个，修改value_type为attrs的key
    if (value.every(item => !item.text)) {
      if (value.every(i => i.attrs.src)) {
        value.forEach((val) => {
          val.text = val.attrs.src
        })
        similarElementData.value_type = 'src'
      }
      if (value.every(i => i.attrs.href)) {
        value.forEach((val) => {
          val.text = val.attrs.href
        })
        similarElementData.value_type = 'href'
      }
    }
    similarElementData.value = value
    return similarElementData
  }
}

/**
 * 相似元素开始抓取
 */
export function similarBatch(params: ElementInfo) {
  let { shadowRoot, xpath, cssSelector, pathDirs } = params
  const elements = getElementByElementInfo(params)
  const currentElement = elements[0]

  if (params.xpath.includes('table')) {
    // 若是table，则使用table单列抓取
    return tableColumnDataBatch(params)
  }
  if (shadowRoot) {
    cssSelector = similarCssSelectorByCssSelector(params.cssSelector)
  }
  else {
    xpath = similarXpathByXpath(params.xpath)
    cssSelector = similarCssSelectorByCssSelector(params.cssSelector)
    pathDirs = similarPathDirsByXpath(params.pathDirs, xpath)
  }

  if (!xpath) {
    const absoluteXpath = getXpath(currentElement, true)
    const absolutePathDirs = getElementDirectory(currentElement, true)
    xpath = similarXpathByXpath(absoluteXpath)
    pathDirs = similarPathDirsByXpath(absolutePathDirs, xpath)
  }
  if (!cssSelector) {
    const absoluteCssSelector = getNthCssSelector(currentElement, true)
    cssSelector = similarCssSelectorByCssSelector(absoluteCssSelector)
  }

  const result = similarDataBatch({ ...params, pathDirs, xpath, cssSelector })
  return result
}

/**
 * 从相似元素组中获取相似元素
 */
export function similarListBatch(data: SimilarDataType) {
  const { values } = data
  const result = values.map((item, index) => {
    const data = similarDataBatch(item)
    return {
      ...data,
      title: item.title || Utils.generateColumnNames(index + 1),
    }
  })
  return { values: result }
}

/**
 * table 抓取
 */
export function tableDataBatch(params: ElementInfo) {
  const eles = getElementByElementInfo(params)
  const dom = eles ? (eles[0] as HTMLElement) : null
  const result = tableDataFormatterProcure(dom)
  const tableValues = tableValuesFormat(result)
  const tableData = { ...params, values: tableValues }
  tableData.rect && delete tableData.rect
  tableData.tag && delete tableData.tag
  tableData.text && delete tableData.text
  return tableData
}

function getClosestTable(dom: HTMLElement) {
  return dom.closest('table')
}

function getTableDom(dom: HTMLElement) {
  let tableDom: HTMLElement | null = null
  let parentDom = dom
  while (!tableDom && parentDom.parentElement) {
    if (parentDom?.tagName?.toLowerCase() === 'table') {
      tableDom = parentDom
      break
    }
    parentDom = parentDom.parentElement
  }
  return tableDom as HTMLTableElement
}

export function getTableMaxTr(tableDom: HTMLTableElement, select = 'tbody') {
  let maxTr: HTMLTableRowElement = null
  let maxNum = 0
  let rows = tableDom.querySelectorAll(`${select} > tr`)
  if ((!rows || rows?.length === 0) && select === 'tbody') {
    rows = tableDom.querySelectorAll(`tr`)
  }
  Array.from(rows).forEach((row) => {
    let tempColNum = 0
    row.querySelectorAll('th, td').forEach((cell) => {
      const colSpan = cell.getAttribute('colspan')
      if (colSpan) {
        tempColNum += Number(colSpan)
      }
      else {
        tempColNum++
      }
    })
    if (tempColNum > maxNum) {
      maxNum = tempColNum
      maxTr = row as HTMLTableRowElement
    }
  })
  return {
    maxNum,
    maxTr,
  }
}

export function getTableHead(headTr: HTMLTableRowElement, maxHeadNum: number) {
  if (!headTr || !headTr.cells || headTr.cells.length === 0) {
    return Array.from({ length: maxHeadNum }, () => '')
  }
  const res = Array.from(headTr.cells).map((cell) => {
    const text = (cell.textContent || cell.innerText || '').replace(/[\u0000-\u001F\u007F]/g, '')
    return text
  })
  return res
}

export function tableDataFormatterProcure(dom: HTMLElement) {
  const tableDom = getTableDom(dom)
  const { maxNum: maxColNum } = getTableMaxTr(tableDom, 'tbody')
  const { maxTr: maxHeadTr, maxNum: maxHeadNum } = getTableMaxTr(tableDom, 'thead')
  const thead = getTableHead(maxHeadTr, maxHeadNum)
  let rows = tableDom.querySelectorAll('tbody > tr')
  if (!rows || rows.length === 0) {
    rows = tableDom.querySelectorAll('tr')
  }
  let tableData: string[][] = Array.from({ length: rows.length }, () => Array.from({ length: maxColNum }, () => null))
  if (rows) {
    Array.from(rows).forEach((row: HTMLTableRowElement, rowIndex) => {
      let columnIndex = 0
      Array.from(row.cells).forEach((cell) => {
        // 找到下一个空列
        while (tableData[rowIndex][columnIndex] !== null) {
          columnIndex++
        }
        // 将数据填入，并处理rowspan/colspan
        for (let i = 0; i < cell.rowSpan; i++) {
          for (let j = 0; j < cell.colSpan; j++) {
            if (tableData[rowIndex + i]) {
              tableData[rowIndex + i][columnIndex + j] = (cell.innerText || cell.textContent || '').replace(/[\u0000-\u001F\u007F]/g, '')
            }
          }
        }
        columnIndex += cell.colSpan
      })
    })
  }
  tableData = tableData.map((tr) => {
    return tr.map((i) => {
      if (typeof i === 'object') {
        i = ''
      }
      return i
    })
  })
  // 对thead和tableData进行校准，保证thead的长度和tableData一致，并且thead的长度大于tableData的长度
  const len = tableData ? tableData[0].length : thead.length
  if (thead.length < len) {
    thead.push(...Array.from({ length: len - thead.length }, () => ''))
  }
  return {
    thead,
    tbody: tableData,
  }
}

/**
 * table 单列抓取, 类似于相似元素
 */
export function tableColumnDataBatch(params: ElementInfo) {
  const { xpath, cssSelector, pathDirs } = params
  const newXpath = tableColumnXpath(xpath)
  const newSelector = tableColumnSelector(cssSelector)
  const newPathDirs = pathDirsByXpath(pathDirs, newXpath)
  const result = similarDataBatch({ ...params, xpath: newXpath, cssSelector: newSelector, pathDirs: newPathDirs })
  return result
}

/**
 * 单列表格xpath
 */
function tableColumnXpath(xpath: string) {
  const xpathArray = xpath.split('/')
  const newXPathArray = xpathArray.map((item) => {
    if (item.includes('tbody')) {
      // 替换tbody 为 *
      return '*'
    }
    else if (item.includes('tr[')) {
      // 替换tr[1]为tr
      return 'tr'
    }
    else if (item.includes('td[') || item.includes('th[')) {
      // 替换td[1], th[1]为*[1]
      // 获取td[1]或th[1]的数字
      const num = item.match(/\d+/)?.[0]
      return `*[${num}]`
    }
    else {
      return item
    }
  })
  return newXPathArray.join('/')
}

/**
 * 单列表格cssSelector
 */
function tableColumnSelector(cssSelector: string) {
  let selector = ''
  // 过滤掉 tbody 或者 thead 的节点
  const selectorArray = cssSelector.split('>').filter(item => item !== 'tbody' && item !== 'thead')
  const newSelectorArray = selectorArray.map((item) => {
    if (item.includes('tr:nth-child(')) {
      // 替换tr:nth-child(1)为tr
      return 'tr'
    }
    else if (item.includes('td:nth-child(') || item.includes('th:nth-child(')) {
      // 替换td:nth-child(1), th:nth-child(1)为*:nth-child(1)
      // 获取td:nth-child(1)或th:nth-child(1)的数字
      const num = item.match(/\d+/)?.[0]
      return `*:nth-child(${num})`
    }
    else {
      return item
    }
  })
  newSelectorArray.forEach((item, index) => {
    if (index === 0) {
      selector = item
    }
    else if (item.includes('tr')) {
      // table > tr 变成 table tr 选择器
      selector = `${selector} ${item}`
    }
    else {
      selector = `${selector}>${item}`
    }
  })
  return selector
}

export function tableHeaderBatch(params: ElementInfo) {
  const eles = getElementByElementInfo(params)
  const dom = eles ? (eles[0] as HTMLElement) : null
  let thead: string[] = []
  const tableDom = getClosestTable(dom)
  if (tableDom) {
    const { maxTr: maxHeadTr, maxNum: maxHeadNum } = getTableMaxTr(tableDom, 'thead')
    if (maxHeadTr) {
      thead = getTableHead(maxHeadTr, maxHeadNum)
    }
    if (!thead.length) {
      const nearTr = dom.closest('tr')
      thead = getTableHead(nearTr, nearTr.cells.length)
    }
  }
  else {
    const { value } = similarBatch(params)
    if (value && value.length) {
      thead = value.map((item) => {
        const { text = '' } = item
        return text
      })
    }
  }
  return thead
}

function tableValuesFormat(values: { thead: string[], tbody: string[][] }) {
  const tableValues = []
  values.thead.forEach((item, index) => {
    const col = {
      title: item || Utils.generateColumnNames(index + 1),
      value: [],
    }
    values.tbody.forEach((item2) => {
      const colval = item2[index] ? item2[index] : ''
      col.value.push(colval)
    })
    tableValues.push(col)
  })
  return tableValues
}
