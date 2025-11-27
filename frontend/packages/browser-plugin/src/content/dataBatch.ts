import type { SimilarDataType } from '../types/data_batch'

/**
 * Data capture
 */
import { generateXPath, getElementByElementInfo, getElementBySelector, getElementDirectory, getNthCssSelector, textAttrFromElement } from './element'
import { Utils } from './utils'

function elementCountByXpath(xpath: string) {
  const similarResults = document.evaluate(`count(${xpath})`, document, null, XPathResult.NUMBER_TYPE, null)
  if (similarResults) {
    return similarResults.numberValue
  }
  else {
    return 0
  }
}

function elementCountByCssSelector(cssSelector: string) {
  return getElementBySelector(cssSelector).length
}

/**
 * Returns the column index of a table cell element specified by the given `ElementInfo` parameters.
 *
 * This function locates the DOM element using `getElementByElementInfo`, finds its closest parent `<tr>`,
 * and determines the cell's index within that row. If the element or row is not found, it returns -1.
 *
 * @param params - The information used to locate the target table cell element.
 * @returns The zero-based column index of the cell within its row, or -1 if not found.
 */
function getColumnIndex(params: ElementInfo) {
  const eles = getElementByElementInfo(params)
  const dom = eles ? (eles[0] as HTMLElement) : null
  if (!dom)
    return -1
  const tr = dom.closest('tr')
  let colIndex = -1
  if (tr) {
    Array.from(tr.cells).forEach((cell, idx) => {
      if (cell === dom) {
        colIndex = idx
      }
    })
  }
  return colIndex
}

/**
 * Generates a similar CSS selector by removing the `:nth-child` pseudo-class from the given selector.
 * Iterates through each part of the selector, and for every occurrence of `:nth-child`,
 * constructs a new selector without it and calculates the number of matching elements using `elementCountByCssSelector`.
 * Returns the selector that matches the most elements after removing `:nth-child`.
 *
 * @param cssSelector - The original CSS selector string, potentially containing `:nth-child` pseudo-classes.
 * @returns A similar CSS selector string with `:nth-child` removed, which matches the most elements.
 */
function similarCssSelectorByCssSelector(cssSelector: string) {
  let similarCssSelector = ''
  let similarCount = 0

  const cssSelectorArr = cssSelector.split('>')

  for (let i = cssSelectorArr.length - 1; i >= 0; i--) {
    if (cssSelectorArr[i].includes(':nth-child')) {
      const tag = cssSelectorArr[i].split(':')[0]
      let currentCssSelector = `${cssSelectorArr.slice(0, i).join('>')}>${tag}>${cssSelectorArr.slice(i + 1).join('>')}`

      currentCssSelector = currentCssSelector.trim()
      currentCssSelector = currentCssSelector.startsWith('>') ? currentCssSelector.slice(1) : currentCssSelector
      currentCssSelector = currentCssSelector.endsWith('>') ? currentCssSelector.slice(0, -1) : currentCssSelector
      const currentSimilatCount = elementCountByCssSelector(currentCssSelector)
      if (currentSimilatCount >= similarCount) {
        similarCount = currentSimilatCount
        similarCssSelector = currentCssSelector
      }
    }
  }
  return similarCssSelector
}

function similarPathDirs(pathDirs: ElementDirectory[]) {
  if (!pathDirs) {
    return []
  }
  pathDirs.forEach((dir) => {
    dir.attrs.forEach((attr, index) => {
      if (attr.name === 'id' && index !== 0) {
        attr.checked = false
      }
      if (attr.name === 'text' || attr.name === 'innertext') {
        attr.checked = false
      }
    })
  })
  let similarCount = 0
  let similarDirs = JSON.parse(JSON.stringify(pathDirs))
  for (let i = pathDirs.length - 1; i >= 0; i--) {
    const pathDir = pathDirs[i]
    const indexAttr = pathDir.attrs.find(item => item.name === 'index' && item.checked)
    if (indexAttr) {
      const checkedBackup = indexAttr.checked
      indexAttr.checked = false
      const newXpath = generateXPath(pathDirs)
      const curSimilarCount = elementCountByXpath(newXpath)
      if (curSimilarCount > similarCount) {
        similarCount = curSimilarCount
        similarDirs = JSON.parse(JSON.stringify(pathDirs))
      }
      indexAttr.checked = checkedBackup
    }
  }
  return similarDirs
}

/**
 * Generates a batch of similar element data based on the provided `ElementInfo` parameters.
 *
 * This function collects elements matching the given parameters, extracts their textual or attribute values,
 * and returns an object containing the batch data. If all elements lack text but have `src` or `href` attributes,
 * those attributes are used as the value and the `value_type` is updated accordingly.
 *
 * @param params - The information describing the target element(s), including attributes and value type.
 * @returns An object containing the batch of similar element data, including extracted values and updated value type.
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
 * Generates a batch of similar elements based on the provided `ElementInfo` parameters.
 *
 * This function attempts to find elements similar to the one described by `params`.
 * - If the XPath includes 'table', it delegates to `tableColumnDataBatch`.
 * - For shadow DOM elements, it computes a similar CSS selector.
 * - For non-shadow DOM elements, it computes similar XPath, CSS selector, and path directories.
 * - If XPath or CSS selector is missing, it computes them from the current element.
 * - Finally, it returns the result of `similarDataBatch` with the updated parameters.
 *
 * @param params - The information about the target element, including shadow root, XPath, CSS selector, and path directories.
 * @returns A batch of similar elements' data.
 */
export function similarBatch(params: ElementInfo) {
  let { shadowRoot, xpath, cssSelector, pathDirs } = params
  if (params.xpath.includes('table')) {
    return tableColumnDataBatch(params)
  }
  cssSelector = similarCssSelectorByCssSelector(params.cssSelector)
  if (!shadowRoot) {
    pathDirs = similarPathDirs(params.pathDirs)
    xpath = generateXPath(pathDirs)
  }
  if (!xpath) {
    const elements = getElementByElementInfo(params)
    const currentElement = elements[0]
    const absolutePathDirs = getElementDirectory(currentElement, true)
    pathDirs = similarPathDirs(absolutePathDirs)
    xpath = generateXPath(pathDirs)
  }
  if (!cssSelector) {
    const elements = getElementByElementInfo(params)
    const currentElement = elements[0]
    const absoluteCssSelector = getNthCssSelector(currentElement, true)
    cssSelector = similarCssSelectorByCssSelector(absoluteCssSelector)
  }

  const result = similarDataBatch({ ...params, pathDirs, xpath, cssSelector })
  return result
}

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

/**
 * Finds the table row (`<tr>`) within the specified section (`select`, defaults to `'tbody'`) of a given HTML table element
 * that contains the maximum number of columns, accounting for `colspan` attributes.
 *
 * If no rows are found in the specified section and `select` is `'tbody'`, it falls back to searching all `<tr>` elements in the table.
 *
 * @param tableDom - The HTML table element to search within.
 * @param select - The section of the table to search for rows (e.g., `'tbody'`, `'thead'`). Defaults to `'tbody'`.
 * @returns An object containing:
 *   - `maxNum`: The maximum number of columns found in a row.
 *   - `maxTr`: The table row element with the maximum number of columns, or `null` if no rows are found.
 */
function getTableMaxTr(tableDom: HTMLTableElement, select = 'tbody') {
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

function getTableHead(headTr: HTMLTableRowElement, maxHeadNum: number) {
  if (!headTr || !headTr.cells || headTr.cells.length === 0) {
    return Array.from({ length: maxHeadNum }, () => '')
  }
  const res = Array.from(headTr.cells).map((cell) => {
    const text = (cell.textContent || cell.innerText || '').replace(/[\u0000-\u001F\u007F]/g, '')
    return text
  })
  return res
}

/**
 * Formats and extracts table data from a given DOM element representing a table.
 *
 * This function processes the table's header and body, handling merged cells (rowSpan and colSpan),
 * and returns a structured representation of the table's header (`thead`) and body (`tbody`).
 * It ensures that the output arrays have consistent dimensions, filling in empty cells as needed.
 *
 * @param dom - The root HTMLElement containing the table to be processed.
 * @returns An object containing:
 * - `thead`: An array of strings representing the table header.
 * - `tbody`: A 2D array of strings representing the table body, with merged cells expanded appropriately.
 */
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
        while (tableData[rowIndex][columnIndex] !== null) {
          columnIndex++
        }

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
  const len = tableData ? tableData[0].length : thead.length
  if (thead.length < len) {
    thead.push(...Array.from({ length: len - thead.length }, () => ''))
  }
  return {
    thead,
    tbody: tableData,
  }
}

export function tableColumnDataBatch(params: ElementInfo) {
  const { cssSelector } = params
  const newSelector = tableColumnSelector(cssSelector)
  const newPathDirs = tableColumnPathDirs(params)
  const newXpath = generateXPath(newPathDirs)
  const result = similarDataBatch({ ...params, xpath: newXpath, cssSelector: newSelector, pathDirs: newPathDirs })
  return result
}

/**
 * Generates a modified array of path directory objects for table column selection.
 *
 * This function processes the `pathDirs` property from the given `ElementInfo` parameter,
 * updating tag names, values, and attributes based on the type of HTML element (e.g., `td`, `th`, `thead`, `tbody`, `tr`).
 * For table cells (`td` or `th`), it sets the tag and value to `*`, marks the `index` attribute as checked,
 * and assigns the column index value. For header and body sections (`thead`, `tbody`), it sets the tag and value to `*`
 * and unchecks all attributes. For table rows (`tr`), it unchecks all attributes. For other elements,
 * it checks the `index` attribute if present.
 *
 * @param params - The element information containing the path directories and other metadata.
 * @returns An array of modified path directory objects reflecting the column selection logic.
 */
function tableColumnPathDirs(params: ElementInfo) {
  const { pathDirs } = params
  const colIndex = getColumnIndex(params)

  return pathDirs.map((dir) => {
    const newDir = { ...dir, attrs: dir.attrs.map(attr => ({ ...attr })) }

    if (dir.tag === 'td' || dir.tag === 'th') {
      newDir.tag = '*'
      newDir.value = '*'
      newDir.attrs.forEach((attr) => {
        if (attr.name === 'index') {
          attr.checked = true
          attr.value = (colIndex + 1).toString()
        }
        else {
          attr.checked = false
        }
      })
    }
    else if (dir.tag === 'thead' || dir.tag === 'tbody') {
      newDir.tag = '*'
      newDir.value = '*'
      newDir.attrs.forEach((attr) => {
        attr.checked = false
      })
    }
    else if (dir.tag === 'tr') {
      newDir.attrs.forEach((attr) => {
        attr.checked = false
      })
    }
    else {
      newDir.attrs.forEach((attr) => {
        if (attr.name === 'index') {
          attr.checked = true
        }
      })
    }
    return newDir
  })
}

/**
 * Generates a simplified CSS selector for a table column based on the provided selector string.
 *
 * This function processes the input CSS selector by removing 'tbody' and 'thead' elements,
 * normalizing 'tr:nth-child' to 'tr', and converting 'td:nth-child' or 'th:nth-child' to
 * '*:nth-child' with the corresponding index. The resulting selector is constructed to
 * target table columns more generically.
 *
 * @param cssSelector - The original CSS selector string for a table column.
 * @returns A simplified CSS selector string suitable for column selection.
 */
function tableColumnSelector(cssSelector: string) {
  let selector = ''

  const selectorArray = cssSelector.split('>').filter(item => item !== 'tbody' && item !== 'thead')
  const newSelectorArray = selectorArray.map((item) => {
    if (item.includes('tr:nth-child(')) {
      return 'tr'
    }
    else if (item.includes('td:nth-child(') || item.includes('th:nth-child(')) {
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
      selector = `${selector} ${item}`
    }
    else {
      selector = `${selector}>${item}`
    }
  })
  return selector
}

/**
 * Extracts the header row values from a table element based on the provided `ElementInfo` parameters.
 *
 * This function attempts to locate the closest table to the given element, and then retrieves the header row values.
 * If a table is found, it first tries to get the header from the `<thead>` section. If no header is found, it falls back
 * to the nearest `<tr>` element. If no table is found, it attempts to retrieve similar batch values as a fallback.
 *
 * @param params - The information used to locate the target element and table.
 * @returns An array of strings representing the table header values.
 */
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
