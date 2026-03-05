import { InputTypeMap, TagMap } from '../content/tag'
import { t } from '../i18n/index'

import { StatusCode } from './constant'

export const Utils = {
  // Background utilities
  getNavigatorUserAgent() {
    const isChorme = /Chrome/.test(navigator.userAgent)
    const isFirefox = /Firefox/.test(navigator.userAgent)
    const isEdge = /Edg/.test(navigator.userAgent)

    if (isFirefox)
      return '$firefox$'
    if (isEdge)
      return '$edge$'
    if (isChorme)
      return '$chrome$'
    return '$unknown$'
  },

  async wait(seconds: number) {
    return new Promise((resolve) => {
      setTimeout(resolve, seconds * 1000)
    })
  },

  removeUrlParams(url: string) {
    return url.replace(/\?.*$/, '')
  },

  isEndWithSlash(url: string) {
    if (url.endsWith) {
      return url.endsWith('/')
    }
    else {
      return url.substr(-1) === '/'
    }
  },

  stringToRegex(inputString: string) {
    let body = inputString
    let flags = ''
    const lastSlashIndex = inputString.lastIndexOf('/')

    if (inputString.startsWith('/') && lastSlashIndex > 0) {
      body = inputString.slice(1, lastSlashIndex)
      if (body.startsWith('^') && body.endsWith('$')) {
        body = body.slice(1, -1)
      }
      if (
        body.includes('\\d')
        || body.includes('\\w')
        || body.includes('\\s')
        || body.includes('\\b')
        || body.includes('\\.')
        || body.includes('\\*')
        || body.includes('\\?')
        || body.includes('\\+')
        || body.includes('\\{')
        || body.includes('\\}')
        || body.includes('\\[')
        || body.includes('\\]')
      ) {
        body = body.replace(/\\/g, '\\')
      }
      flags = inputString.slice(lastSlashIndex + 1)
    }
    try {
      const regex = new RegExp(body, flags)
      return regex
    }
    catch {
      throw new Error('Invalid regular expression pattern')
    }
  },

  isSupportProtocal(url: string) {
    if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('ftp://') || url.startsWith('file://')) {
      return true
    }
    else {
      return false
    }
  },

  // Content utilities
  isSupportUrl(str: string) {
    return /^(http|https|ftp|file):\/\/.+$/.test(str)
  },

  getTag(element: HTMLElement) {
    const tag = element.tagName.toLowerCase()
    if (tag === 'input') {
      const type = element.getAttribute('type')
      if (InputTypeMap[type])
        return InputTypeMap[type]
      else return t('inputTypes.text')
    }
    else if (TagMap[tag]) {
      return TagMap[tag]
    }
    else {
      return t('tags.other')
    }
  },

  isDynamicAttribute(attrName: string, attrValue: string) {
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    const longRandomPattern = /^[\w-]{20,}$/
    const dynamicKeywords = ['temp-', 'dynamic-', 'random-', 'unique-', 'session-', 'token-', 'uuid-', 'id-', 'key-', 'rand-', 'hover-', 'active-', 'focus-', 'selected-', '-open', '-active', '-hover', '-focus', '-selected', 'show', 'hide', 'hidden']
    const lowerValue = attrValue.toLowerCase()

    if (attrName === 'id') {
      return uuidPattern.test(attrValue) || longRandomPattern.test(attrValue) || dynamicKeywords.some(kw => lowerValue.includes(kw))
    }
    return dynamicKeywords.some(kw => lowerValue.includes(kw))
  },

  isControlCharacter(str: string) {
    return /[\x00-\x1F\x7F]/.test(str)
  },

  isEffectCharacter(str: string) {
    return /[0-9a-z\u4E00-\u9FA5]/i.test(str)
  },

  isSpaceCharacter(str: string) {
    return /^\s.*|\s$/.test(str)
  },

  pureText(str: string) {
    str.replaceAll(/[\x00-\x1F\x7F]/g, '')
    if (str.startsWith(' ')) {
      str = str.replace(/^\s+/, '')
    }
    if (str.endsWith(' ')) {
      str = str.replace(/\s+$/, '')
    }
    return str
  },

  generateColumnNames(num: number) {
    let result = ''
    while (num > 0) {
      const remainder = (num - 1) % 26
      const char = String.fromCharCode(65 + remainder)
      result = char + result
      num = Math.floor((num - 1) / 26)
    }
    return result
  },

  generateColor(index: number) {
    const colors = [
      '#FF5733',
      '#33FF57',
      '#3357FF',
      '#FF33A1',
      '#A133FF',
      '#33FFF5',
      '#F5FF33',
      '#FF3333',
      '#33FFA1',
      '#8A33FF',
    ]
    return colors[index % colors.length]
  },

  generateRandomColor() {
    const r = Math.floor(Math.random() * 256)
    const g = Math.floor(Math.random() * 151) + 50
    const b = Math.floor(Math.random() * 256)
    return `rgb(${r},${g},${b})`
  },

  pureObject(obj: object, keys = []) {
    for (const key in obj) {
      if (!keys.includes(key)) {
        delete obj[key]
      }
    }
    return obj
  },

  // Shared utilities
  isNumberStartString(str: string) {
    return /^\d/.test(str)
  },

  isNumberString(str: string) {
    return /\d/.test(str)
  },

  isSpecialCharacter(str: string) {
    if (this.isNumberStartString(str))
      return true
    if (/[·~`!@#$%^&*()+\-={}\\[\]|:;"'<>,.?/（）￥！、；：【】《》，。？—]/.test(str))
      return true
    return false
  },

  success(data, msg = 'success') {
    return {
      code: StatusCode.SUCCESS,
      data,
      msg,
    }
  },

  fail(msg = 'failed', code = StatusCode.UNKNOWN_ERROR) {
    return {
      data: null,
      code,
      msg,
    }
  },

  result(data, msg = 'success', code = StatusCode.SUCCESS) {
    return {
      code,
      data,
      msg,
    }
  },

  textfn(val: string) {
    if (val.includes('"')) {
      return `text()=concat(${val
        .split('"')
        .map((part, index, arr) => (index < arr.length - 1 ? `"${part}", '"', ` : `"${part}"`))
        .join('')})`
    }
    return `text()="${val}"`
  },

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
  conditionStr(attr: ElementAttrs) {
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
              : Utils.textfn(attr.value)
          break
        case 'text':
          condition
            = attr.type === 1
              ? `contains(., "${attr.value}")`
              : Utils.textfn(attr.value)
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
  },

  /**
   * Generates an XPath string based on a list of element directories and their attributes.
   *
   * @param dirs - An array of `ElementDirectory` objects representing the hierarchy of elements and their attributes.
   * @param onlyPosition - If `true`, only position-related attributes (such as `index` and `id`) are considered for XPath generation.
   * @returns The generated XPath string representing the element hierarchy and attribute conditions.
   */
  generateXPath(dirs: ElementDirectory[], onlyPosition: boolean = false): string {
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
    let xpath = ''
    let checkedDirIndex = 0
    for (let i = 0; i < dirs.length; i++) {
      const dir = dirs[i]
      if (dir.checked) {
        const attrs = dir.attrs
          .filter((attr) => {
            // exclude type 2 (regex) attrs
            if (attr.type === 2 && attr.checked) {
              return false
            }
            else {
              return attr.checked
            }
          })
          .map((attr) => {
            const condition: string = Utils.conditionStr(attr)
            return condition
          })
          .join(' and ')
        const segment = attrs ? `${dir.tag}[${attrs}]` : dir.tag
        let prefix = '/'
        if (i === 0) {
          prefix = dir.tag === 'html' ? '/' : '//'
        }
        if (Math.abs(i - checkedDirIndex) > 1) {
          prefix = '//'
        }
        xpath += `${prefix}${segment}`
        checkedDirIndex = i
      }
    }
    return xpath
  },
}
