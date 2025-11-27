import { MAX_ATTRIBUTE_LENGTH, MAX_TEXT_LENGTH, SVG_NODETAGS } from './constant'
import { highLight, highLightRects } from './highlight'
import { Utils } from './utils'

function getSupportTag(tagName: string) {
  if (Utils.isSpecialCharacter(tagName)) {
    return '*'
  }
  else {
    return tagName
  }
}

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
    if (!value.attrs[key]) {
      delete value.attrs[key]
    }
  }
  return value
}

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

export function getAttrs(element: Element) {
  const attrs = {}
    ;['src', 'href', 'id', 'class', 'title', 'name'].forEach((key) => {
    const attr = element.getAttribute(key)?.replace(/[\u0000-\u001F\u007F]/g, '')
    attr && (attrs[key] = attr)
  })
  return attrs
}

export function isTable(element: HTMLElement) {
  return element.tagName.toLowerCase() === 'table' || element.closest('table') !== null
}

function getElementIndex(element: HTMLElement) {
  return element.parentElement
    ? Array.from(element.parentElement.children)
      .filter(sibling => sibling.tagName.toLowerCase() === element.tagName.toLowerCase())
      .indexOf(element) + 1
    : 0
}

function getAllElementIndex(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).indexOf(element) + 1 : 0
}

function getElementNthIndex(element: HTMLElement) {
  if (hasSameTypeSiblings(element)) {
    return element.parentElement ? Array.from(element.parentElement.children).indexOf(element) + 1 : 0
  }
}

function getNodeNthIndex(element: HTMLElement) {
  if (element.parentNode) {
    return Array.from(element.parentNode.children).indexOf(element) + 1
  }
}

function hasSameTypeSiblings(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).filter(sibling => sibling.tagName.toLowerCase() === element.tagName.toLowerCase()).length > 1 : false
}

function hasSiblings(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).length > 1 : false
}

function hasSameClassSiblings(element: HTMLElement, className: string) {
  const siblings = element.parentElement ? Array.from(element.parentElement.children).filter(sibling => sibling !== element) : []
  if (siblings && siblings.length > 0) {
    const hasSameClass = siblings.some(sibling => sibling.classList.contains(className))
    return hasSameClass
  }
  else {
    return false
  }
}

function pickClass(element: HTMLElement) {
  const classList = Array.from(element.classList)
  for (const cls of classList) {
    if (isLegalClass(cls) && !hasSameClassSiblings(element, cls)) {
      return cls
    }
  }
  return ''
}

function elementFromPoint(x: number, y: number, docu: Document | ShadowRoot) {
  const element = docu.elementFromPoint(x, y)
  return element
}

function isUniqueIdFn(id: string) {
  return id && !Utils.isNumberString(id) && !Utils.isSpecialCharacter(id) && document.querySelectorAll(`#${id}`).length === 1
}

function isLegalClass(cls: string) {
  return cls && !Utils.isNumberString(cls) && !Utils.isSpecialCharacter(cls) && !Utils.isDynamicAttribute('class', cls)
}
function isSvgElement(element: Element): boolean {
  return element.namespaceURI === 'http://www.w3.org/2000/svg'
}

/**
 * Filters an array of HTMLElements to include only those that are visible.
 *
 * An element is considered visible if:
 * - Its bounding rectangle has non-zero width and height.
 * - Its computed CSS `visibility` property is not `'hidden'` or `'collapse'`.
 *
 * @param elements - The array of HTMLElements to filter.
 * @returns A new array containing only the visible elements.
 */
export function filterVisibleElements(elements: HTMLElement[]) {
  if (elements && elements.length) {
    elements = elements.filter((ele) => {
      const rect = ele.getBoundingClientRect()
      if (rect.width === 0 || rect.height === 0)
        return false
      const style = window.getComputedStyle(ele)
      if (style.visibility === 'hidden' || style.visibility === 'collapse')
        return false
      return true
    })
  }
  return elements
}

/**
 * Generates an XPath expression for a given HTML element.
 *
 * The function traverses up the DOM tree from the specified element,
 * constructing an XPath that uniquely identifies the element. If the element
 * has a unique ID and `absolute` is `false`, the XPath will use the ID for
 * a shorter, more robust selector. Otherwise, it will use tag names and
 * indices to build the path. Special handling is included for SVG elements.
 *
 * @param element - The target HTML element for which to generate the XPath.
 * @param absolute - If `true`, always generates an absolute XPath from the root.
 *                   If `false`, uses unique IDs when available for a shorter XPath.
 *                   Defaults to `false`.
 * @returns The XPath string representing the element's location in the DOM.
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

    const isSvg = isSvgElement(element)
    tagName = isSvg ? `*` : tagName
    index = isSvg ? getAllElementIndex(element) : index
    hasSublings = isSvg ? hasSiblings(element) : hasSublings
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
    if (element && element.tagName.toLowerCase() === 'body') {
      xpath = `/${xpath}`
      break
    }
  }
  return xpath
}

/**
 * Generates a CSS selector string for the given HTML element, optionally as an absolute selector.
 *
 * The selector is constructed by traversing up the DOM tree from the provided element,
 * considering unique IDs, tag names, class names, and sibling indices to ensure specificity.
 * If a unique ID is found and `isAbsolute` is false, the selector will use the ID for brevity.
 * Otherwise, it builds a path using tag names, classes, and `:nth-child` pseudo-classes as needed.
 *
 * @param element - The target HTML element for which to generate the CSS selector.
 * @param isAbsolute - If `true`, generates an absolute selector from the root (`html`); otherwise, stops at a unique ID or `body`.
 * @returns The CSS selector string representing the element's position in the DOM, or an empty string if the element is invalid.
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
      selectors.unshift(`${tagName}.${className}`)
    }
    else {
      selectors.unshift(`${tagName}:nth-child(${index})`)
    }

    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body') {
      return selectors.join('>')
    }
  }
  return selectors.join('>')
}

function onlyPositionXpath(xpath: string) {
  const pathArr = xpath.split('/')
  const positionArr = pathArr.map((item) => {
    const match2 = item.match(/\[@position\(\)=\d+\]/)
    if (item.includes('@position') && !match2) {
      const match3 = item.match(/@position\(\)=\d+/)
      if (match3) {
        const num = match3[0].split('=')[1]
        return item.replace(/\[.*\]/, `[@position()=${num}]`)
      }
    }
    return item
  })
  const path = positionArr.join('/')
  return path
}

/**
 * Resolves an XPath string for SVG elements by transforming tag names into local-name() checks.
 *
 * This function splits the input XPath into segments, and for each segment that matches an SVG tag
 * (as defined by the global `SVG_NODETAGS` array), it replaces the tag name with a local-name() check.
 * If the segment contains an attribute or position predicate, it is included in the transformation.
 * Non-SVG tags and wildcard segments are left unchanged.
 *
 * @param xpath - The XPath string to resolve for SVG elements.
 * @returns The transformed XPath string with SVG tag names replaced by local-name() checks.
 */
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
        if (attr) {
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
  return elements.length > 0 ? filterVisibleElements(elements) : null
}

export function getElementByXPath(xpath: string): HTMLElement | null {
  const element = xpath ? document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue : null
  return element as HTMLElement
}

export function getElementBySelector(selector: string, onlyPosition: boolean = false): HTMLElement[] | null {
  if (!selector)
    return null
  if (onlyPosition) {
    selector = onlyPositionSelector(selector)
  }
  if (selector.includes('$shadow$')) {
    const sahdowElements = getShadowElementsBySelector(selector)
    return sahdowElements.length > 0 ? filterVisibleElements(sahdowElements) : null
  }
  else {
    const elements = Array.from(document.querySelectorAll(selector)) as HTMLElement[]
    return elements.length > 0 ? filterVisibleElements(elements) : null
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
 * Recursively queries elements across multiple levels of shadow DOM using a sequence of CSS selectors.
 *
 * @param selectorLevels - An array of CSS selectors, each representing a level in the DOM/shadow DOM hierarchy.
 * @param currentHosts - An array containing the current host roots to search within (defaults to the main document).
 * @returns An array of elements matching the full selector path across shadow DOM boundaries.
 *
 * @example
 * // To find an element inside nested shadow roots:
 * const elements = queryDeepShadow(['custom-element', '.inner-element', 'button']);
 */
function queryDeepShadow(selectorLevels: string[], currentHosts: [Document | ShadowRoot] = [document]) {
  if (selectorLevels.length === 0)
    return []

  const currentSelector = selectorLevels[0]
  const remainingSelectors = selectorLevels.slice(1)
  const isLastLevel = remainingSelectors.length === 0

  const matches = []
  for (const host of currentHosts) {
    const elements = host.querySelectorAll(currentSelector)
    if (elements.length === 0)
      continue

    if (isLastLevel) {
      matches.push(...elements)
      continue
    }

    for (const el of elements) {
      if (el.shadowRoot) {
        const nestedMatches = queryDeepShadow(remainingSelectors, [el.shadowRoot])
        matches.push(...nestedMatches)
      }
    }
  }

  return matches
}

function getShadowElementsBySelector(selector: string) {
  const selectorLevels = selector.split('>$shadow$>')
  const allElements = queryDeepShadow(selectorLevels)
  return filterVisibleElements(allElements)
}

/**
 * Selects and marks the most significant attribute from a list of element attributes.
 *
 * The function prioritizes the 'id' attribute, marking it as checked if present.
 * If 'id' is not found, it checks for the 'text' attribute and marks it as checked.
 * All other attributes are marked as unchecked.
 * If neither 'id' nor 'text' is present, the attributes remain unchanged.
 *
 * @param attrs - An array of `ElementAttrs` objects representing element attributes.
 * @returns The updated array of `ElementAttrs` with the most significant attribute marked as checked.
 */
function getWeightedAttrs(attrs: ElementAttrs[]) {
  const idAttr = attrs.find(attr => attr.name === 'id')
  const textAttr = attrs.find(attr => attr.name === 'text')
  if (idAttr) {
    attrs.forEach(attr => (attr.checked = false))
    idAttr.checked = true
    return attrs
  }
  if (textAttr) {
    attrs.forEach(attr => (attr.checked = false))
    textAttr.checked = true
    return attrs
  }
  return attrs
}

/**
 * Rebuilds the directory structure by re-evaluating the 'index' attribute of each node in the given directory list.
 * For each directory, it temporarily unchecks the 'index' attribute and generates an XPath from the current state.
 * If the XPath uniquely identifies the origin element, the 'index' remains unchecked; otherwise, it is checked again.
 *
 * @param originElement - The original HTML element to match against the generated XPath.
 * @param dirs - An array of `ElementDirectory` objects representing the directory structure and attributes.
 * @returns The updated array of `ElementDirectory` objects with potentially modified 'index' attribute states.
 */
function rebuildDirectory(originElement: HTMLElement, dirs: ElementDirectory[]) {
  // Re-weight dirs again, try to uncheck the index of each node
  for (let i = dirs.length - 1; i >= 0; i--) {
    const dir = dirs[i]
    const indexAttr = dir.attrs.find(attr => attr.name === 'index')
    if (indexAttr) {
      indexAttr.checked = false
      const xpath = generateXPath(dirs)
      const elements = getElementsByXpath(xpath)
      const ignoreIndex = elements && elements.length === 1 && elements[0] === originElement
      if (!ignoreIndex) {
        indexAttr.checked = true
      }
    }
  }
  return dirs
}

/**
 * Generates a directory of element descriptors for the given HTMLElement, representing its ancestry and key attributes.
 * The directory is built from the element up to the root or until a unique identifier is found.
 *
 * @param element - The target HTMLElement for which to generate the directory.
 * @param isAbsolute - If true, traverses up to the root element regardless of unique identifiers; otherwise, stops at a unique id or the body element.
 * @returns An array of `ElementDirectory` objects, each describing an ancestor element and its relevant attributes.
 */
export function getElementDirectory(element: HTMLElement, isAbsolute = false): ElementDirectory[] {
  if (!element)
    return []
  const originElement = element
  const elementDirectory = []
  while (element) {
    const id = getAttr(element, 'id')
    const isUniqueId = isUniqueIdFn(id)
    const className = pickClass(element)
    const type = getAttr(element, 'type')
    const title = getAttr(element, 'title')
    let tagName = getSupportTag(element.tagName.toLowerCase())
    let index = getElementIndex(element)
    let hasSubling = hasSameTypeSiblings(element)

    const isSvg = isSvgElement(element)
    tagName = isSvg ? `*` : tagName
    index = isSvg ? getAllElementIndex(element) : index
    hasSubling = isSvg ? hasSiblings(element) : hasSubling

    // assemble attrs with initial weights
    let attrs = []
    if (isUniqueIdFn(id))
      attrs.push({ name: 'id', value: id, checked: true, type: 0 })
    if (isSvg)
      attrs.push({ name: 'local-name', value: element.tagName.toLowerCase(), checked: true, type: 0 })
    if (hasSubling && index)
      attrs.push({ name: 'index', value: index, checked: true, type: 0 })
    if (type)
      attrs.push({ name: 'type', value: type, checked: true, type: 0 })
    if (className)
      attrs.push({ name: 'class', value: className, checked: true, type: 1 })
    if (title && title.length < MAX_ATTRIBUTE_LENGTH)
      attrs.push({ name: 'title', value: title, checked: false, type: 0 })
    // text attr only for target element
    if (elementDirectory.length === 0) {
      const text = getNodeText(element)
      if (text && text.length < MAX_TEXT_LENGTH && Utils.isEffectCharacter(text) && !Utils.isControlCharacter(text)) {
        attrs.push({ name: 'text', value: text, checked: true, type: 1 })
      }
    }

    // get weighted attrs
    attrs = getWeightedAttrs(attrs)
    const attributes = { tag: tagName, checked: true, value: tagName, attrs }
    elementDirectory.unshift(attributes)
    // id has highest weight, stop here
    if (id && isUniqueId && !isAbsolute) {
      return rebuildDirectory(originElement, elementDirectory)
    }
    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body') {
      return rebuildDirectory(originElement, elementDirectory)
    }
  }
  return rebuildDirectory(originElement, elementDirectory)
}

/**
 * Filters a list of HTML elements based on a directory of element attributes, using regular expressions.
 *
 * For each element in `searchElements`, this function traverses up the DOM tree according to the length of
 * the filtered `elementDirectory` (where `checked` is true), collecting ancestor elements. For each directory entry,
 * if an attribute of type 2 is checked, its value is used as a regular expression to test the corresponding attribute
 * value of the ancestor element. If all regular expressions match, the element is included in the result.
 *
 * @param searchElements - The list of HTML elements to filter.
 * @param elementDirectory - The directory describing which attributes and regular expressions to use for filtering.
 * @returns An array of HTML elements that match all checked regular expressions in the directory.
 */
function checkElementsByRegular(searchElements: HTMLElement[], elementDirectory: ElementDirectory[]) {
  const dirs = elementDirectory.filter(item => item.checked)
  const filterList = searchElements.filter((element) => {
    const allElements = []
    let currentElement = element
    let dlength = dirs.length
    let flag = true
    while (dlength > 0) {
      allElements.unshift(currentElement)
      currentElement = currentElement.parentElement
      dlength--
    }
    dirs.forEach((item, index) => {
      const attrs = item.attrs
      const regAttr = attrs.find(attr => attr.type === 2 && attr.checked)
      if (regAttr) {
        const nodeValue = String(regAttr.value).trim()
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

function directoryFindElement(elementDirectory: ElementDirectory[], onlyPosition: boolean = false) {
  let searchElements: HTMLElement[] = []
  const xpath = generateXPath(elementDirectory, onlyPosition)
  // console.log('directoryFindElement generateXPath xpath: ', xpath)
  searchElements = getElementsByXpath(xpath, onlyPosition)
  if (searchElements && searchElements.length > 0) {
    searchElements = checkElementsByRegular(searchElements, elementDirectory)
    return searchElements
  }
  else {
    return null
  }
}

function textfn(val: string) {
  if (val.includes('"')) {
    return `text()=concat(${val
      .split('"')
      .map((part, index, arr) => (index < arr.length - 1 ? `"${part}", '"', ` : `"${part}"`))
      .join('')})`
  }
  return `text()="${val}"`
}

/**
 * Generates an XPath condition string based on the provided element attributes.
 *
 * The function inspects the `attr` parameter and constructs a condition string
 * suitable for use in XPath queries. The condition depends on the attribute's
 * name, value, type, and checked status:
 * - For `index`, returns a position-based condition.
 * - For `innertext` and `text`, returns a condition using `contains` or a custom text function.
 * - For `local-name`, matches the element's local name.
 * - For other attributes, uses either `contains` or direct equality based on the type.
 *
 * @param attr - The element attributes used to generate the condition.
 * @returns The XPath condition string, or `undefined` if no condition is generated.
 */
function conditionStr(attr: ElementAttrs) {
  attr.value = `${attr.value}`
  let condition: string
  if (attr.checked && attr.value) {
    switch (attr.name) {
      case 'index':
        condition = `position()=${attr.value}`
        break

      case 'innertext':
        condition
          = attr.type === 1
            ? `contains(., "${attr.value}")`
            : textfn(attr.value)
        break
      case 'text':
        condition
          = attr.type === 1
            ? `contains(., "${attr.value}")`
            : textfn(attr.value)
        break

      case 'local-name':
        condition = `local-name()="${attr.value}"`
        break

      default:
        condition
          = attr.type === 1
            ? `contains(@${attr.name}, "${attr.value}")`
            : `@${attr.name}="${attr.value}"`
        break
    }
  }

  return condition
}

/**
 * Generates an XPath string based on a list of element directories and their attributes.
 *
 * @param dirs - An array of `ElementDirectory` objects representing the hierarchy of elements and their attributes.
 * @param onlyPosition - If `true`, only position-related attributes (such as `index` and `id`) are considered for XPath generation.
 * @returns The generated XPath string representing the element hierarchy and attribute conditions.
 */
export function generateXPath(dirs: ElementDirectory[], onlyPosition: boolean = false): string {
  if (dirs && dirs.length === 0) {
    return ''
  }
  if (onlyPosition) {
    dirs = JSON.parse(JSON.stringify(dirs)) // deep copy avoid modifying original dirs
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

export function hasChildElement(element) {
  return element && element.children && element.children.length > 0
}

export function highlightElements(elements: HTMLElement[]) {
  if (elements.length > 1) {
    const rects = elements.map(element => element.getBoundingClientRect().toJSON())
    highLightRects(rects)
  }
  else {
    const rect = elements[0].getBoundingClientRect().toJSON() // getBoundingClientRect(element);
    highLight(rect)
  }
}

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
 * Retrieves the positions and bounding rectangles of all visible elements within a given HTML body or ShadowRoot.
 *
 * This function filters out non-visual elements (such as `<head>`, `<title>`, `<meta>`, `<script>`, `<style>`, and `<link>`)
 * and elements that are hidden via CSS (`display: none` or `visibility: hidden`). It further excludes elements with zero width or height.
 * For elements containing a shadow root, the function recursively collects positions of elements within the shadow DOM.
 *
 * @param body - The root element to search within. Defaults to `document.body` if not provided. Can be an `HTMLElement` or a `ShadowRoot`.
 * @returns An array of `ElementPosition` objects, each containing the element reference and its bounding rectangle properties.
 */
export function getAllElementsPositionInBody(body: HTMLElement | ShadowRoot = document.body): Array<ElementPosition> {
  const elements = Array.from(body.querySelectorAll('*')) as HTMLElement[]
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
  positions.push(...shadowPositions)
  return positions
}

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

export function getAllElements() {
  const elements = document.body.querySelectorAll('*:not(script):not(style):not(noscript)')
  return Array.from(elements)
}

/**
 * Retrieves all `<iframe>` and `<frame>` elements from the current document.
 *
 * @returns {Element[]} An array containing all iframe and frame elements found in the document.
 */
function getAllFrames() {
  const iframeList = document.querySelectorAll('iframe') || []
  const frameList = document.querySelectorAll('frame') || []
  const frames = Array.from(iframeList).concat(Array.from(frameList))
  return frames
}

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

export function getIFramesElements() {
  const frames = getAllFrames()
  return frames
}

export function getElementsFromPoints(a: { x: number, y: number }, b: { x: number, y: number }) {
  const elements = []
  for (let x = a.x; x <= b.x; x++) {
    for (let y = a.y; y <= b.y; y++) {
      const element = document.elementFromPoint(x, y)
      if (elements.includes(element))
        continue
      if (element) {
        elements.push(element)
      }
    }
  }
  return elements
}

export function getElementFromAllElements(elements: Array<ElementPosition>, range: ElementRange): Promise<Array<ElementPosition>> {
  return new Promise((resolve, reject) => {
    try {
      const result = elements.filter((item) => {
        const exp1 = item.x >= range.start.x && item.x <= range.end.x
        const exp2 = item.y >= range.start.y && item.y <= range.end.y
        const exp3 = item.x + item.width <= range.end.x
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
 * Returns the closest DOM element to a given point on the page.
 *
 * This function first attempts to find the topmost element at the specified coordinates.
 * If multiple elements are present at the point, it filters those whose bounding rectangles
 * contain the point and then selects the one whose bounding rectangle is closest to the point.
 *
 * @param target - The point with `x` and `y` coordinates to search for the closest element.
 * @returns The closest DOM element to the specified point, or the topmost element if no bounding rectangles contain the point.
 */
export function getClosestElementByPoint(target: Point) {
  const ele = elementFromPoint(target.x, target.y, document)
  const eles = document.elementsFromPoint ? getElementsByPosition(target.x, target.y) : getAllElementsPositionInBody()
  if (!eles.length)
    return ele
  const pointEles = eles.filter((item) => {
    return item.left <= target.x && item.top <= target.y && item.right >= target.x && item.bottom >= target.y
  })
  if (!pointEles.length)
    return ele
  const closestElement = pointEles.reduce((prev, curr) => {
    const prevDistance = Math.hypot(prev.left - target.x, prev.top - target.y, prev.right - target.x, prev.bottom - target.y)
    const currDistance = Math.hypot(curr.left - target.x, curr.top - target.y, curr.right - target.x, curr.bottom - target.y)
    return prevDistance <= currDistance ? prev : curr
  })
  return closestElement.element
}

export function findElementByPoint(target: Point, deep = false, docu: Document | ShadowRoot = document) {
  let ele = elementFromPoint(target.x, target.y, docu) as HTMLElement
  if (deep && docu instanceof Document) {
    ele = getClosestElementByPoint(target)
  }
  if (!ele)
    return null
  return ele
}

/**
 * Recursively finds the deepest element at the given point within nested shadow roots,
 * constructing a CSS selector path and collecting element directory information along the way.
 *
 * @param point - The coordinates `{ x, y }` at which to search for the element.
 * @param shadowRoot - The root `ShadowRoot` to start the search from.
 * @param shadowPath - (Optional) The accumulated CSS selector path for shadow DOM traversal.
 * @param shadowDirs - (Optional) The accumulated array of `ElementDirectory` objects for each traversed element.
 * @returns An object containing:
 *   - `element`: The deepest `HTMLElement` found at the given point.
 *   - `path`: The constructed CSS selector path through shadow DOMs.
 *   - `dirs`: The array of `ElementDirectory` objects for each traversed element.
 */
export function shadowRootElement(point: Point, shadowRoot: ShadowRoot, shadowPath: string = '', shadowDirs: ElementDirectory[] = []) {
  const { x, y } = point
  const ele = shadowRoot.elementFromPoint(x, y) as HTMLElement
  if (ele && ele.shadowRoot) {
    const shadowNth = `:nth-child(${getNodeNthIndex(ele)})`
    shadowPath = shadowPath ? `${shadowPath}>$shadow$>${getNthCssSelector(ele)}${shadowNth}` : `${getNthCssSelector(ele)}${shadowNth}`
    shadowDirs = shadowDirs.concat(getElementDirectory(ele))
    return shadowRootElement(point, ele.shadowRoot, shadowPath, shadowDirs)
  }
  else {
    return {
      element: ele,
      path: shadowPath,
      dirs: shadowDirs,
    }
  }
}

function getPadding(element: HTMLElement) {
  const dpr = window.devicePixelRatio
  const computedStyle = window.getComputedStyle(element)
  const paddingLeft = Number.parseInt(computedStyle.paddingLeft) || 0
  const paddingTop = Number.parseInt(computedStyle.paddingTop) || 0
  const paddingRight = Number.parseInt(computedStyle.paddingRight) || 0
  const paddingBottom = Number.parseInt(computedStyle.paddingBottom) || 0
  return { paddingLeft: paddingLeft * dpr, paddingTop: paddingTop * dpr, paddingRight: paddingRight * dpr, paddingBottom: paddingBottom * dpr }
}

function getBorder(element: HTMLElement) {
  const dpr = window.devicePixelRatio
  const computedStyle = window.getComputedStyle(element)
  const borderLeft = Number.parseInt(computedStyle.borderLeftWidth) || 0
  const borderTop = Number.parseInt(computedStyle.borderTopWidth) || 0
  const borderRight = Number.parseInt(computedStyle.borderRightWidth) || 0
  const borderBottom = Number.parseInt(computedStyle.borderBottomWidth) || 0
  return { borderLeft: borderLeft * dpr, borderTop: borderTop * dpr, borderRight: borderRight * dpr, borderBottom: borderBottom * dpr }
}

export function getBoundingClientRect(element: HTMLElement): DOMRectT {
  // @ts-expect-error  currentFrameInfo in window
  const iframeTransform = window.currentFrameInfo.iframeTransform
  const { scaleX = 1, scaleY = 1 } = iframeTransform
  const safeNum = 8
  const rect = element.getBoundingClientRect().toJSON()
  const dpr = window.devicePixelRatio
  const { left, top, width, height, right, bottom, x, y } = rect
  return {
    left: Math.round(left * scaleX * dpr),
    top: Math.round(top * scaleY * dpr),
    width: Math.round(width * scaleX * dpr) || safeNum,
    height: Math.round(height * scaleY * dpr) || safeNum,
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

export function getIframeTransform(element: Element) {
  const style = window.getComputedStyle(element)
  const matrix = new DOMMatrix(style.transform)
  const scaleX = matrix.a
  const scaleY = matrix.d
  return {
    scaleX,
    scaleY,
  }
}

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
