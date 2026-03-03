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
}
