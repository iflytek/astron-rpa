import { MAX_TEXT_LENGTH, SVG_NODETAGS } from './constant'
import { highLight, highLightRects } from './highlight'
import { Utils } from './utils'

/**
 * 计算 xpath 的元素个数
 */
export function xpathEvaluateCount(xpath: string) {
  return document.evaluate(`count(${xpath})`, document, null, XPathResult.ANY_TYPE, null).numberValue
}
/**
 * 获取支持的tag, 若tagName 是特殊字符，则返回*
 */
function getSupportTag(tagName: string) {
  if (Utils.isSpecialCharacter(tagName)) {
    return '*'
  }
  else {
    return tagName
  }
}
/**
 * 获取元素的内部文本，包括子节点等
 */
export function getText(element: HTMLElement) {
  if (element.tagName === 'INPUT') {
    return (element as HTMLInputElement).value || element.getAttribute('placeholder') || ''
  }
  else if (element.tagName === 'TEXTAREA') {
    return (element as HTMLTextAreaElement).value || element.getAttribute('placeholder') || ''
  }
  else if (element.tagName === 'SELECT') {
    return (element as HTMLSelectElement).value || element.getAttribute('placeholder') || ''
  }
  else if (element.tagName === 'IMG') {
    return element.getAttribute('alt') || ''
  }
  else {
    return element.textContent || element.innerText || ''
  }
}
/**
 * 获取当前节点的text , 不包括子节点，用于可视化编辑
 */
function getNodeText(element: HTMLElement) {
  const nodeText
    = Array.from(element.childNodes)
      .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent && node.textContent.trim())
      .map(node => node.textContent!.replace(/[\x00-\x1F\x7F]/g, '').trim())
      .find(text => text.length > 0) || ''
  return nodeText
}

export function textAttrFromElement(ele: HTMLElement) {
  const text = getText(ele).replace(/[\x00-\x1F\x7F]/g, '')
  const src = getAttr(ele, 'src')
  const href = getAttr(ele, 'href')
  const value: SimilarDataValueT = {
    text,
    attrs: {
      src,
      href,
      text,
    },
  }
  for (const key in value.attrs) {
    if (value.attrs[key] === null) {
      delete value.attrs[key]
    }
  }
  return value
}
/**
 * 获取元素属性
 */
export function getAttr(element: HTMLElement, attrName: string) {
  const attrMap = {
    id: element.getAttribute('id'),
    class: element.getAttribute('class'),
    name: element.getAttribute('name'),
    type: element.getAttribute('type'),
    value: (element as HTMLInputElement).value,
    href: (element as HTMLAnchorElement).href,
    src: (element as HTMLImageElement | HTMLSourceElement).src,
    title: element.title,
    text: getNodeText(element),
    readonly: String((element as HTMLInputElement).readOnly),
  }
  if (attrName in attrMap) {
    return attrMap[attrName] || ''
  }
  return element.getAttribute(attrName)
}
/**
 * 获取元素属性map
 */
export function getAttrs(element: Element) {
  const attrs = {}
  ;['src', 'href', 'id', 'class', 'title', 'name'].forEach((key) => {
    const attr = element.getAttribute(key)?.replace(/[\u0000-\u001F\u007F]/g, '')
    attr && (attrs[key] = attr)
  })
  return attrs
}

/**
 * 元素是否是table, 或者是table的子元素
 */
export function isTable(element: HTMLElement) {
  return element.tagName.toLowerCase() === 'table' || element.closest('table') !== null
}

/**
 * 获取相同元素Index
 */
function getElementIndex(element: HTMLElement) {
  return element.parentElement
    ? Array.from(element.parentElement.children)
      .filter(sibling => sibling.tagName.toLowerCase() === element.tagName.toLowerCase())
      .indexOf(element) + 1
    : 0
}
/**
 * 获取元素Index, 用于 * nth-child 选择器
 */
function getAllElementIndex(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).indexOf(element) + 1 : 0
}

/**
 * 获取元素css Selector nth 的index
 */
function getElementNthIndex(element: HTMLElement) {
  // 若元素存在相同兄弟元素，则返回元素的index
  if (hasSameTypeSiblings(element)) {
    return element.parentElement ? Array.from(element.parentElement.children).indexOf(element) + 1 : 0
  }
}

function getNodeNthIndex(element: HTMLElement) {
  // 若元素存在相同兄弟元素，则返回元素的index
  if (element.parentNode) {
    return Array.from(element.parentNode.children).indexOf(element) + 1
  }
}

/**
 * 获取元素是否有相同类型兄弟元素
 */
function hasSameTypeSiblings(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).filter(sibling => sibling.tagName.toLowerCase() === element.tagName.toLowerCase()).length > 1 : false
}

/**
 * 获取元素是否有兄弟元素
 */
function hasSiblings(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).length > 1 : false
}

/**
 * 获取相同类型兄弟节点上是否存在相同class
 */
function hasSameClassSiblings(element: HTMLElement, className: string) {
  const siblings = element.parentElement ? Array.from(element.parentElement.children).filter(sibling => sibling !== element) : []
  if (siblings) {
    const hasSameClass = siblings.some(sibling => sibling.classList.contains(className))
    return hasSameClass
  }
  else {
    return false
  }
}

/**
 * 选取元素的class, 优先返回不重复的class
 */
function pickClass(element: HTMLElement) {
  const classList = Array.from(element.classList)
  for (const cls of classList) {
    if (isLegalClass(cls) && !hasSameClassSiblings(element, cls)) {
      return cls
    }
  }
  return ''
}

// 获取鼠标位置的元素 x, y 是元素相对于document的坐标, 每个document 是iframe 的dcoument
export function elementFromPoint(x: number, y: number, docu: Document | ShadowRoot) {
  const element = docu.elementFromPoint(x, y)
  return element
}

function isUniqueIdFn(id: string) {
  return id && !Utils.isNumberString(id) && !Utils.isSpecialCharacter(id) && document.querySelectorAll(`#${id}`).length === 1
}

function isLegalClass(cls: string) {
  return cls && !Utils.isNumberString(cls) && !Utils.isSpecialCharacter(cls)
}
// 判断元素是否是SVG元素
function isSvgElement(element: Element): boolean {
  return element.namespaceURI === 'http://www.w3.org/2000/svg'
}
/**
 * 获取元素的xpath
 */
export function getXpath(element: HTMLElement, absolute = false) {
  if (!element)
    return ''
  let xpath = ''
  while (element) {
    const id = element.id
    const isUniqueId = isUniqueIdFn(id)
    let tagName = getSupportTag(element.tagName.toLowerCase())
    let index = getElementIndex(element)
    let hasSublings = hasSameTypeSiblings(element)
    // 如果是SVG元素，特殊处理
    const isSvg = isSvgElement(element)
    tagName = isSvg ? `*` : tagName
    index = isSvg ? getAllElementIndex(element) : index // SVG元素使用节点的nth-child索引
    hasSublings = isSvg ? hasSiblings(element) : hasSublings // SVG元素使用是否有兄弟元素
    if (!absolute && isUniqueId) {
      xpath = `//${tagName}[@id="${id}"]${xpath}`
      break
    }
    else if (index > 0 && hasSublings) {
      xpath = `/${tagName}[${index}]${xpath}`
    }
    else {
      xpath = `/${tagName}${xpath}`
    }

    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body' && !absolute) {
      // 如果是body元素，则返回目录
      xpath = `/${xpath}`
      break
    }
  }
  return xpath
}

/**
 * 获取元素的css selector
 */
export function getNthCssSelector(element: HTMLElement, isAbsolute = false): string {
  if (!element)
    return ''
  const selectors = []
  while (element) {
    const id = getAttr(element, 'id')
    const tagName = getSupportTag(element.tagName.toLowerCase())
    const isUniqueId = isUniqueIdFn(id)
    const index = getElementNthIndex(element)
    const hasSameSublings = hasSameTypeSiblings(element)
    const className = pickClass(element)
    if (tagName === 'html') {
      selectors.unshift(tagName)
      break
    }
    else if (!isAbsolute && isUniqueId) {
      selectors.unshift(`#${id}`)
      break
    }
    else if (!hasSameSublings) {
      selectors.unshift(tagName)
    }
    else if (className) {
      // 增加class 在css selector的权重
      selectors.unshift(`${tagName}.${className}`)
    }
    else {
      selectors.unshift(`${tagName}:nth-child(${index})`)
    }
    // const eles = getElementBySelector(selectors.join('>'));
    // if (eles && eles.length === 1 && eles[0] === element) {
    //   return selectors.join('>');
    // }
    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body' && !isAbsolute) {
      // 如果是body元素，则返回目录
      return selectors.join('>')
    }
  }
  return selectors.join('>')
}

/**
 * 仅匹配位置的xpath
 */
function onlyPositionXpath(xpath: string) {
  const pathArr = xpath.split('/')
  const positionArr = pathArr.map((item) => {
    // 匹配 [@position()=number] 格式
    const match2 = item.match(/\[@position\(\)=\d+\]/)
    // 匹配 [@position()=number and xxx] 格式 多个条件的
    if (item.includes('@position') && !match2) {
      // 只取 [@position()=number] 的条件,匹配出number
      // 匹配出div[@position()=1 and @id="app"] 种的 数字
      const match3 = item.match(/@position\(\)=\d+/)
      if (match3) {
        const num = match3[0].split('=')[1]
        // 去掉以 [ 开始， 以] 结束的所有字符串，替换成 [@position=number]
        return item.replace(/\[.*\]/, `[@position()=${num}]`)
      }
    }
    return item
  })
  const path = positionArr.join('/')
  return path
}

function svgPathResolver(xpath: string) {
  const pathArr = xpath.split('/')
  const newPathArr = pathArr.map((item) => {
    if (!item || item === '*')
      return item
    const tagMatch = item.match(/^([^[]+)/)
    const tag = tagMatch ? tagMatch[1] : ''
    const attrMatch = item.match(/\[(.+)\]/)
    const attr = attrMatch ? attrMatch[1] : ''
    if (tag && tag !== '*') {
      if (SVG_NODETAGS && SVG_NODETAGS.includes(tag)) {
        // SVG 元素
        if (attr) {
          // 判断是否 position()=number
          const posMatch = attr.match(/^position\(\)\s*=\s*(\d+)$/)
          if (posMatch) {
            return `*[local-name()="${tag}" and position()=${posMatch[1]}]`
          }
          else {
            return `*[local-name()="${tag}" and ${attr}]`
          }
        }
        else {
          return `*[local-name()="${tag}"]`
        }
      }
      else {
        return item
      }
    }
    return item
  })
  const svgPath = newPathArr.filter(Boolean).join('/')
  return svgPath
}

/**
 * 通过xpath获取元素
 */
export function getElementsByXpath(path: string, onlyPosition: boolean = false): HTMLElement[] | null {
  if (!path)
    return null
  if (onlyPosition) {
    path = onlyPositionXpath(path)
  }
  if (path.includes('/svg[') || path.includes('/svg/')) {
    path = svgPathResolver(path)
  }
  const result = document.evaluate(path, document, null, XPathResult.ANY_TYPE, null)
  let element = result.iterateNext() as HTMLElement
  const elements: HTMLElement[] = []
  while (element) {
    elements.push(element)
    element = result.iterateNext() as HTMLElement
  }
  return elements.length > 0 ? elements : null
}

/**
 * 获取单元素
 */
export function getElementByXPath(xpath: string): HTMLElement | null {
  const element = xpath ? document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue : null
  return element as HTMLElement
}

/**
 * 通过类名获取元素
 */
export function getElementsByClassName(className: string): HTMLElement[] {
  const elements = document.querySelectorAll(`.${className}`)
  return Array.from(elements) as HTMLElement[]
}

/**
 * 组合式选择器获取元素
 */
export function getElementsByComposition(searchString: string): HTMLElement[] | null {
  const all = document.querySelectorAll(searchString)
  return Array.from(all) as HTMLElement[]
}

/**
 * 通过 selector 获取元素
 */
export function getElementBySelector(selector: string, onlyPosition: boolean = false): HTMLElement[] | null {
  if (!selector)
    return null
  if (onlyPosition) {
    selector = onlyPositionSelector(selector)
  }
  // selector 存在 >$shadow$>，则使用 多级querySelector
  if (selector.includes('$shadow$')) {
    const sahdowElements = getShadowElementsBySelector(selector)
    return sahdowElements.length > 0 ? sahdowElements : null
  }
  else {
    const elements = Array.from(document.querySelectorAll(selector)) as HTMLElement[]
    return elements.length > 0 ? elements : null
  }
}
function onlyPositionSelector(selector: string) {
  const filteredSelector = selector
    .split('>')
    .map((part) => {
      if (part.includes(':nth-child')) {
        return part.substring(0, part.indexOf(':nth-child') + 13)
      }
      if (part.includes('.')) {
        return part.split('.')[0]
      }
      return part
    })
    .join('>')
  return filteredSelector
}

/**
 * 穿透多级 Shadow DOM 查询所有匹配元素
 */
function queryDeepShadow(selectorLevels: string[], currentHosts: [Document | ShadowRoot] = [document]) {
  if (selectorLevels.length === 0)
    return []

  // 取出当前层级的选择器
  const currentSelector = selectorLevels[0]
  const remainingSelectors = selectorLevels.slice(1)
  const isLastLevel = remainingSelectors.length === 0

  // 遍历当前宿主元素，查询匹配的子元素
  const matches = []
  for (const host of currentHosts) {
    const elements = host.querySelectorAll(currentSelector)
    if (elements.length === 0)
      continue

    // 如果是最后一层，直接收集结果
    if (isLastLevel) {
      matches.push(...elements)
      continue
    }

    // 否则进入下一层 Shadow DOM
    for (const el of elements) {
      if (el.shadowRoot) {
        // 递归处理下一层级
        const nestedMatches = queryDeepShadow(remainingSelectors, [el.shadowRoot])
        matches.push(...nestedMatches)
      }
    }
  }

  return matches
}
/**
 * 获取 shadowdom selector 对应的元素
 */
function getShadowElementsBySelector(selector: string) {
  const selectorLevels = selector.split('>$shadow$>')
  const allElements = queryDeepShadow(selectorLevels)
  return allElements
}

/**
 * 对attrs 中的每一项做权重处理
 */
function getWeightedAttrs(attrs: ElementAttrs[]) {
  /**
   * 遍历attrs 中的每一项
   * 规则：1，存在id 则该项选中， attr.checked = true, 其他项 attr.checked = false
   * 2，不存在id, 存在 text 则该项选中， attr.checked = true, 其他项 attr.checked = false
   * 3，不存在id, text, 存在 index, type 则该项选中， attr.checked = true, 其他项 attr.checked = false
   */
  const idAttr = attrs.find(attr => attr.name === 'id')
  const typeAttr = attrs.find(attr => attr.name === 'type')
  const indexAttr = attrs.find(attr => attr.name === 'index')
  const textAttr = attrs.find(attr => attr.name === 'text')
  const textValue = (textAttr && textAttr.value) || ''
  const classAttr = attrs.find(attr => attr.name === 'class')
  // 1，存在id 则该项选中， attr.checked = true, 其他项 attr.checked = false
  if (idAttr) {
    attrs.forEach(attr => (attr.checked = false))
    idAttr.checked = true
    return attrs
  }
  // 2，不存在id, 存在 src, href, text 则该项选中， attr.checked = true, 其他项 attr.checked = false
  if (textAttr && !Utils.isControlCharacter(String(textValue))) {
    textAttr.checked = true
    return attrs
  }
  // 3，存在class 且已经选中则选中class
  if (classAttr && classAttr.checked) {
    return attrs
  }
  // 如果不存在id, text, 则选中 index, type
  if (typeAttr) {
    typeAttr.checked = true
  }
  if (indexAttr && indexAttr.value) {
    indexAttr.checked = true
  }
  return attrs
}

/**
 * 获取元素目录
 */
export function getElementDirectory(element: HTMLElement, isAbsolute = false): ElementDirectory[] {
  if (!element)
    return []
  const elementDirectory = []
  while (element) {
    const id = getAttr(element, 'id')
    const isUniqueId = isUniqueIdFn(id)
    const className = pickClass(element)
    const type = getAttr(element, 'type')
    let tagName = getSupportTag(element.tagName.toLowerCase())
    let index = getElementIndex(element)
    let hasSubling = hasSameTypeSiblings(element)

    // 如果是SVG元素，特殊处理
    const isSvg = isSvgElement(element)
    tagName = isSvg ? `*` : tagName // SVG元素使用通配符 *
    index = isSvg ? getAllElementIndex(element) : index // SVG元素使用节点的nth-child索引
    hasSubling = isSvg ? hasSiblings(element) : hasSubling // SVG元素使用是否有兄弟元素

    let attrs = []
    //  id > local-name >  class,index > type > text
    if (isUniqueIdFn(id))
      attrs.push({ name: 'id', value: id, checked: false, type: 0 })
    if (isSvg)
      attrs.push({ name: 'local-name', value: element.tagName.toLowerCase(), checked: true, type: 0 })
    if (hasSubling && index)
      attrs.push({ name: 'index', value: index, checked: false, type: 0 })
    if (type)
      attrs.push({ name: 'type', value: type, checked: false, type: 0 })
    if (className)
      attrs.push({ name: 'class', value: className, checked: false, type: 1 })
    if (elementDirectory.length === 0) {
      // 节点 text 属性
      const text = getNodeText(element)
      if (text && text.length < MAX_TEXT_LENGTH && Utils.isEffectCharacter(text)) {
        attrs.push({ name: 'text', value: text, checked: false, type: 1 })
      }
    }

    attrs = getWeightedAttrs(attrs)
    const attributes = { tag: tagName, checked: true, value: tagName, attrs }
    elementDirectory.unshift(attributes)
    if (id && isUniqueId && !isAbsolute) {
      // 相对目录, 有id 就返回相对目录
      return elementDirectory
    }
    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body' && !isAbsolute) {
      return elementDirectory // 如果是body元素，则返回目录
    }
  }
  return elementDirectory
}
/**
 *  校验元素是否符合目录的正则规则，后处理
 */
function checkElementsByRegular(searchElements: HTMLElement[], elementDirectory: ElementDirectory[]) {
  const dirs = elementDirectory.filter(item => item.checked)
  const filterList = searchElements.filter((element) => {
    const allElements = [] // 当前元素及目录长度内的所有父元素
    let currentElement = element // 当前元素
    let dlength = dirs.length // 目录长度
    let flag = true // 默认符合
    while (dlength > 0) {
      allElements.unshift(currentElement) // 添加当前元素到数组开始，得到顺序相同的节点
      currentElement = currentElement.parentElement
      dlength--
    }
    dirs.forEach((item, index) => {
      const attrs = item.attrs
      const regAttr = attrs.find(attr => attr.type === 2 && attr.checked) // 存在正则校验
      if (regAttr) {
        const nodeValue = String(regAttr.value).trim() //
        if (nodeValue) {
          const node = allElements[index]
          if (node) {
            const value = getAttr(node, regAttr.name)
            try {
              const reg = new RegExp(nodeValue)
              if (!reg.test(value)) {
                flag = false
              }
            }
            catch (error) {
              console.error(`Invalid regular expression: ${nodeValue}`, error)
              flag = false
            }
          }
        }
      }
    })
    return flag
  })
  return filterList
}

/**
 * 通过 element 目录获取元素, 从底部向上查找,只要查到唯一一个元素即可停止
 */
export function directoryFindElement(elementDirectory: ElementDirectory[], onlyPosition: boolean = false) {
  // let searchPath = '';
  let searchElements: HTMLElement[] = []
  const xpath = generateXPath(elementDirectory, onlyPosition)
  console.log('directoryFindElement generateXPath xpath: ', xpath)
  searchElements = getElementsByXpath(xpath, onlyPosition)
  if (searchElements && searchElements.length > 0) {
    searchElements = checkElementsByRegular(searchElements, elementDirectory)
    return searchElements
  }
  else {
    return null
  }
}

// 处理xpath text()=xxx 中存在" 双引号问题
function textfn(val: string) {
  if (val.includes('"')) {
    return `text()=concat(${val
      .split('"')
      .map((part, index, arr) => (index < arr.length - 1 ? `"${part}", '"', ` : `"${part}"`))
      .join('')})`
  }
  return `text()="${val}"`
}

function conditionStr(attr: ElementAttrs) {
  attr.value = `${attr.value}`
  let condition: string
  if (attr.checked && attr.value) {
    switch (attr.name) {
      case 'index':
        // 索引
        condition = `position()=${attr.value}`
        break

      case 'innertext':
        // 文本内容
        condition
          = attr.type === 1
            ? `contains(., "${attr.value}")` // 通配，包含
            : textfn(attr.value) // 默认等于，处理双引号问题
        break
      case 'text':
        // 文本内容
        condition
          = attr.type === 1
            ? `contains(., "${attr.value}")` // 通配，包含
            : textfn(attr.value) // 默认等于，处理双引号问题
        break

      case 'local-name':
        // SVG 元素的 local-name 属性
        condition = `local-name()="${attr.value}"`
        break

      default:
        // 其他属性
        condition
          = attr.type === 1
            ? `contains(@${attr.name}, "${attr.value}")` // 通配，包含
            : `@${attr.name}="${attr.value}"` // 默认等于
        break
    }
  }

  return condition
}

/**
 * pathDirs 转成xpath
 */
export function generateXPath(dirs: ElementDirectory[], onlyPosition: boolean = false): string {
  if (dirs && dirs.length === 0) {
    return ''
  }
  if (onlyPosition) {
    // 仅匹配位置
    dirs.forEach((item) => {
      item.attrs.forEach((attr) => {
        const attrValue = `${attr.value}`.trim()
        if (attr.name === 'index' && attrValue !== '') {
          attr.checked = true
        }
        else if (attr.name === 'id' && attrValue !== '') {
          attr.checked = true
        }
        else {
          attr.checked = false
        }
      })
    })
  }
  const xpath = dirs
    .filter(dir => dir.checked)
    .map((dir) => {
      const attrs = dir.attrs
        .filter((attr) => {
          if (attr.type === 2 && attr.value && attr.checked) {
            // 正则表达式暂不处理， 正则表达式不支持前处理
            return false
          }
          else {
            return attr.checked
          }
        })
        .map((attr) => {
          const condition: string = conditionStr(attr)
          return condition
        })
        .join(' and ')
      return attrs ? `${dir.tag}[${attrs}]` : dir.tag
    })
    .join('/')
  if (xpath.startsWith('html')) {
    return `/${xpath}`
  }
  return `//${xpath}`
}

/**
 * 获取鼠标移动到的元素
 */
export function getMouseOverElement(document = window.document, position) {
  const { x, y } = position
  return document.elementFromPoint(x, y)
}

// 判断元素是否存在子元素
export function hasChildElement(element) {
  return element && element.children && element.children.length > 0
}

/**
 * 校验元素
 */
export function checkElements(elements: HTMLElement[]) {
  // 获取元素的位置信息
  if (elements.length > 1) {
    const rects = elements.map(element => element.getBoundingClientRect().toJSON())
    highLightRects(rects)
  }
  else {
    const rect = elements[0].getBoundingClientRect().toJSON() // getBoundingClientRect(element);
    highLight(rect)
  }
}

/**
 * 获取x,y 坐标下所有元素
 */
export function getElementsByPosition(x: number, y: number) {
  const elements = document.elementsFromPoint(x, y)
  const positions = elements.map((element) => {
    const rect = element.getBoundingClientRect()
    return {
      element,
      ...rect.toJSON(),
    }
  })
  return positions
}
/**
 *  获取 body 标签下所有可见元素，拿到元素位置和大小
 */
export function getAllElementsPositionInBody(body: HTMLElement | ShadowRoot = document.body): Array<ElementPosition> {
  const elements = Array.from(body.querySelectorAll('*')) as HTMLElement[]
  // 过滤掉元数据元素 <head>、<title>、<meta>、<script>、<style>
  const visibleElements = Array.from(elements).filter(
    element =>
      element.tagName.toLowerCase() !== 'head'
      && element.tagName.toLowerCase() !== 'title'
      && element.tagName.toLowerCase() !== 'meta'
      && element.tagName.toLowerCase() !== 'script'
      && element.tagName.toLowerCase() !== 'style'
      && element.tagName.toLowerCase() !== 'link'
      && element?.style.display !== 'none'
      && element?.style.visibility !== 'hidden',
  )
  // 过滤掉不可见元素
  const visibleElements2 = visibleElements.filter(element => element.getBoundingClientRect().width > 0 && element.getBoundingClientRect().height > 0)
  const positions = []
  let shadowPositions = []
  visibleElements2.forEach((element) => {
    const rect = element.getBoundingClientRect()
    if (element && element.shadowRoot) {
      const shadowRoot = element.shadowRoot
      shadowPositions = getAllElementsPositionInBody(shadowRoot)
    }
    positions.push({
      element,
      ...rect.toJSON(),
    })
  })
  // 合并 shadowPositions 到 positions 中
  positions.push(...shadowPositions)
  return positions
}
/**
 * 获取所有元素的位置和大小
 */
export function getAllElementsPosition() {
  const elements = getAllElements()
  const positions = []
  elements.forEach((element) => {
    const rect = element.getBoundingClientRect()
    positions.push({
      element,
      ...rect,
    })
  })
  return positions
}
/**
 * 获取 body 标签下所有元素
 */
export function getAllElements() {
  const elements = document.querySelectorAll('*')
  return Array.from(elements)
}

/**
 * all frame include iframe and frame
 */
export function getAllFrames() {
  const iframeList = document.querySelectorAll('iframe') || []
  const frameList = document.querySelectorAll('frame') || []
  const frames = Array.from(iframeList).concat(Array.from(frameList))
  return frames
}
/**
 * 获取当前 window 下的 iframe
 */
export function getWindowFrames() {
  const frames = getAllFrames()
  const framesList = Array.from(frames).map((frame) => {
    return {
      xpath: getXpath(frame),
      src: frame.src,
      rect: getFrameContentRect(frame),
    }
  })
  return framesList
}

/**
 * 获取当前 window 下的 iframe
 */
export function getIFramesElements() {
  const frames = getAllFrames()
  return frames
}

/**
 * 获取从a点{x,y}到b点{x,y}的所有像素点上的元素
 */
export function getElementsFromPoints(a: { x: number, y: number }, b: { x: number, y: number }) {
  const elements = []
  for (let x = a.x; x <= b.x; x++) {
    for (let y = a.y; y <= b.y; y++) {
      const element = document.elementFromPoint(x, y)
      // 如果数组已经包含该元素，则跳过
      if (elements.includes(element))
        continue
      if (element) {
        elements.push(element)
      }
    }
  }
  return elements
}

/**
 * 从所有元素中获取到符合位置的元素
 */
export function getElementFromAllElements(elements: Array<ElementPosition>, range: ElementRange): Promise<Array<ElementPosition>> {
  return new Promise((resolve, reject) => {
    try {
      const result = elements.filter((item) => {
        // item 的 x 不小于range.start.x 且  item 的 x 不大于 range.end.x
        const exp1 = item.x >= range.start.x && item.x <= range.end.x
        // item 的 y 不小于 range.start.y 且 item 的 y 不大于 range.end.y
        const exp2 = item.y >= range.start.y && item.y <= range.end.y
        // item 的 x + item.width 不大于 range.end.x
        const exp3 = item.x + item.width <= range.end.x
        // item 的 y + item.height 不大于 range.end.y
        const exp4 = item.y + item.height <= range.end.y

        return exp1 && exp2 && exp3 && exp4
      })
      resolve(result)
    }
    catch (error) {
      reject(error)
    }
  })
}

/**
 * 通过 point {x,y} 获取最小范围的元素
 */
export function getClosestElementByPoint(target: Point) {
  const ele = elementFromPoint(target.x, target.y, document)
  // 支持 document.elementsFromPoint 的浏览器 直接走elementsFromPoint ，不支持的再获取所有元素
  const eles = document.elementsFromPoint ? getElementsByPosition(target.x, target.y) : getAllElementsPositionInBody()
  if (!eles.length)
    return ele
  // 元素 left, top, right, bottom 能包含target {x,y} 的元素
  const pointEles = eles.filter((item) => {
    return item.left <= target.x && item.top <= target.y && item.right >= target.x && item.bottom >= target.y
  })
  if (!pointEles.length)
    return ele
  // 遍历pointEles 找到 left, top, right, bottom 距离 target (x, y) 最近的一项
  const closestElement = pointEles.reduce((prev, curr) => {
    // 左上角 和右下角 做位置计算, 元素位置大小通过 左上角和右下角就可以确定, 右上角和左下角可以无需计算
    const prevDistance = Math.hypot(prev.left - target.x, prev.top - target.y, prev.right - target.x, prev.bottom - target.y)
    const currDistance = Math.hypot(curr.left - target.x, curr.top - target.y, curr.right - target.x, curr.bottom - target.y)
    return prevDistance <= currDistance ? prev : curr
  })
  return closestElement.element
}

/**
 * 查找元素, 提供开关项来控制是否深度查找, 解决遮盖和iframe ,shadow dom问题
 */
export function findElementByPoint(target: Point, deep = false, docu: Document | ShadowRoot = document) {
  let ele = elementFromPoint(target.x, target.y, docu) as HTMLElement
  // 深度查找
  if (deep && docu instanceof Document) {
    ele = getClosestElementByPoint(target)
  }
  if (!ele)
    return null
  return ele
}

/**
 * 从 x, y 坐标获取元素, 若有 shadow dom, 则递归查找
 */
export function shadowRootElement(point: Point, shadowRoot: ShadowRoot, shadowPath: string = '', shadowDirs: ElementDirectory[] = []) {
  const { x, y } = point
  const ele = shadowRoot.elementFromPoint(x, y) as HTMLElement
  if (ele && ele.shadowRoot) {
    const shadowNth = `:nth-child(${getNodeNthIndex(ele)})`
    shadowPath = shadowPath ? `${shadowPath}>$shadow$>${getNthCssSelector(ele)}${shadowNth}` : `${getNthCssSelector(ele)}${shadowNth}`
    shadowDirs = shadowDirs.concat(getElementDirectory(ele))
    return shadowRootElement(point, ele.shadowRoot, shadowPath, shadowDirs) // 递归查找
  }
  else {
    return {
      element: ele,
      path: shadowPath,
      dirs: shadowDirs,
    }
  }
}

/**
 * 获取元素缩放比例
 */
export function getZoom(element: HTMLElement) {
  let zoom = 1
  while (element) {
    const currentZoom = Number(window.getComputedStyle(element).zoom || 1)
    zoom *= currentZoom
    element = element.parentElement
  }
  return zoom
}

/**
 *  获取元素padding
 */
export function getPadding(element: HTMLElement) {
  const dpr = window.devicePixelRatio
  const computedStyle = window.getComputedStyle(element)
  const paddingLeft = Number.parseInt(computedStyle.paddingLeft) || 0
  const paddingTop = Number.parseInt(computedStyle.paddingTop) || 0
  const paddingRight = Number.parseInt(computedStyle.paddingRight) || 0
  const paddingBottom = Number.parseInt(computedStyle.paddingBottom) || 0
  return { paddingLeft: paddingLeft * dpr, paddingTop: paddingTop * dpr, paddingRight: paddingRight * dpr, paddingBottom: paddingBottom * dpr }
}

export function getBorder(element: HTMLElement) {
  const dpr = window.devicePixelRatio
  const computedStyle = window.getComputedStyle(element)
  const borderLeft = Number.parseInt(computedStyle.borderLeftWidth) || 0
  const borderTop = Number.parseInt(computedStyle.borderTopWidth) || 0
  const borderRight = Number.parseInt(computedStyle.borderRightWidth) || 0
  const borderBottom = Number.parseInt(computedStyle.borderBottomWidth) || 0
  return { borderLeft: borderLeft * dpr, borderTop: borderTop * dpr, borderRight: borderRight * dpr, borderBottom: borderBottom * dpr }
}

// function getFramePosition(element: HTMLElement) {
//   const dpr = window.devicePixelRatio;
//   const posLeft = Number.parseInt(window.getComputedStyle(element).left) || 0;
//   const posTop = Number.parseInt(window.getComputedStyle(element).top) || 0;
//   return { left: posLeft * dpr, top: posTop * dpr };
// }

/**
 *  获取元素位置大小 ，经过缩放处理
 */
export function getBoundingClientRect(element: HTMLElement): DOMRectT {
  // @ts-expect-error  currentFrameInfo 在 window 上
  const iframeTransform = window.currentFrameInfo.iframeTransform
  const { scaleX = 1, scaleY = 1 } = iframeTransform
  const safeNum = 8
  const rect = element.getBoundingClientRect().toJSON()
  const dpr = window.devicePixelRatio
  const { left, top, width, height, right, bottom, x, y } = rect
  return {
    left: Math.round(left * scaleX * dpr),
    top: Math.round(top * scaleY * dpr),
    width: Math.round(width * scaleX * dpr) || safeNum, // 防止宽度为0
    height: Math.round(height * scaleY * dpr) || safeNum, // 防止高度为0
    right: Math.round(right * scaleX * dpr),
    bottom: Math.round(bottom * scaleY * dpr),
    x: Math.round(x * scaleX * dpr),
    y: Math.round(y * scaleY * dpr),
  }
}

export function getFrameContentRect(element: HTMLElement) {
  const frameRect = getBoundingClientRect(element)
  const padding = getPadding(element)
  const border = getBorder(element)
  // const position = getFramePosition(element)
  const frameContentRect = {
    left: frameRect.left + padding.paddingLeft + border.borderLeft,
    top: frameRect.top + padding.paddingTop + border.borderTop,
    width: frameRect.width - padding.paddingLeft - padding.paddingRight - border.borderLeft - border.borderRight,
    height: frameRect.height - padding.paddingTop - padding.paddingBottom - border.borderTop - border.borderBottom,
    right: frameRect.right - padding.paddingRight - border.borderRight,
    bottom: frameRect.bottom - padding.paddingBottom - border.borderBottom,
    x: frameRect.x + padding.paddingLeft + border.borderLeft,
    y: frameRect.y + padding.paddingTop + border.borderTop,
  }
  return frameContentRect
}

/**
 * 处理 iframe 上的缩放导致内部位置偏移的问题
 */
export function getIframeTransform(element: Element) {
  const style = window.getComputedStyle(element)
  const matrix = new DOMMatrix(style.transform)
  const scaleX = matrix.a
  const scaleY = matrix.d
  // 返回变化
  return {
    scaleX,
    scaleY,
  }
}
/**
 * 通过元素信息获取元素
 */
export function getElementByElementInfo(params: ElementInfo): HTMLElement[] | null {
  const { xpath, cssSelector, pathDirs, shadowRoot, checkType, matchTypes } = params
  const onlyPosition = matchTypes && matchTypes.includes('onlyPosition')
  if (shadowRoot) {
    return getElementBySelector(cssSelector, onlyPosition)
  }
  if (checkType === 'visualization') {
    return directoryFindElement(pathDirs, onlyPosition)
  }
  let eles = getElementsByXpath(xpath, onlyPosition)
  if (!eles || eles.length === 0) {
    eles = getElementBySelector(cssSelector, onlyPosition)
  }
  return eles
}

/**
 * 获取子元素
 */
export function getChildElementByType(element: HTMLElement, params: Options): HTMLElement[] | HTMLElement | null {
  const { elementGetType } = params
  if (elementGetType === 'index') {
    return element.children[params.index || 0] as HTMLElement
  }
  if (elementGetType === 'all') {
    return Array.from(element.children) as HTMLElement[]
  }
  if (elementGetType === 'xpath') {
    return document.evaluate(`.${params.xpath}`, element, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue as HTMLElement
  }
  if (elementGetType === 'last') {
    return element.lastElementChild as HTMLElement
  }
}

/**
 * 获取兄弟元素
 */
export function getSiblingElementByType(element: HTMLElement, params: Options): HTMLElement[] | HTMLElement | null {
  const { elementGetType } = params
  if (elementGetType === 'all') {
    return Array.from(element.parentElement.children) as HTMLElement[]
  }
  if (elementGetType === 'prev') {
    return element.previousElementSibling as HTMLElement
  }
  if (elementGetType === 'next') {
    return element.nextElementSibling as HTMLElement
  }
}
