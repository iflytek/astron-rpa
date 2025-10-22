export { isEmpty } from 'lodash-es'

/**
 * 正则简单模糊匹配
 * @param {string} input
 * @param {string} target
 */
export function simpleFuzzyMatch(input: string, target: string) {
  // 匹配所有正则特殊字符，并在前面加反斜杠转义
  const escapeRegExp = (str: string) => {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  const pattern = input
    .split('')
    .map(escapeRegExp)
    .join('.*') // 每个字符之间允许任意内容

  return new RegExp(pattern, 'i').test(target) // 忽略大小写
}

/**
 * 生成 uuid
 * @returns string
 */
export function generateUUID() {
  let d = Date.now()
  const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (d + Math.random() * 16) % 16 | Math.trunc(d / 16)
    d = Math.floor(d / 16)
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
  return uuid
}

/**
 *  base64 转 file
 */
export function base64ToFile(base64: string, fileName: string) {
  const arr = base64.split(',')
  const mime = arr[0].match(/:(.*?);/)[1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new File([u8arr], fileName, { type: mime })
}

/**
 * 图片地址转 base64
 * @param imgUrl 图片地址
 */
export function imgUrltoBase64(imgUrl: string) {
  return new Promise((resolve, reject) => {
    fetch(imgUrl).then(
      (res) => {
        res.blob().then((blob) => {
          const reader = new FileReader()
          reader.readAsDataURL(blob)
          reader.onloadend = () => {
            resolve(reader.result)
          }
        })
      },
      (err) => {
        reject(err)
      },
    )
  })
}

/**
 * 移除base64图片头, 非base64图片则返回原字符串
 * @param base64
 */
export function trimBase64Header(base64: string) {
  const base64Header = 'data:image/png;base64,'
  if (!base64.includes(base64Header))
    return base64
  return base64.replace(base64Header, '')
}

/**
 * 添加base64图片头
 */
export function addBase64Header(base64: string) {
  const base64Header = 'data:image/png;base64,'
  return base64Header + base64
}

/**
 * 是否是 base64 图片
 */
export function isBase64Image(base64: string) {
  const base64Header = 'data:image/png;base64,'
  return base64 && base64.includes(base64Header)
}

/**
 * base64 字符串转正常字符串
 */
export function base64ToString(base64: string) {
  return atob(base64)
}

/**
 * 插件更新提示，版本号a.b.c中 a,b 变化需要强制更新插件， c 变化则需要提示更新
 * @param {string} version1
 * @param {string} version2
 * @returns {enum} 1: 需要更新，2: 强制更新(暂时不用)，0/-1: 不需要更新
 */
export function compareVersion(version1, version2) {
  // version1>version2 则需要更新，若
  let res = 0
  const v1 = version1.split('.')
  const v2 = version2.split('.')
  const len = Math.max(v1.length, v2.length)
  while (v1.length < len) {
    v1.push('0')
  }
  while (v2.length < len) {
    v2.push('0')
  }
  for (let i = 0; i < len; i++) {
    const num1 = Number.parseInt(v1[i])
    const num2 = Number.parseInt(v2[i])
    // if (i < 2 && num1 > num2) {
    //   // 版本号a.b.c中 a,b 变化需要强制更新插件
    //   res = 2;
    //   break;
    // } else
    if (num1 > num2) {
      res = 1
      break
    }
    else if (num1 < num2) {
      res = -1
      break
    }
  }
  return res
}

// 获取文件名，不含后缀
export function getFileName(fileName: string) {
  return fileName.substring(0, fileName.lastIndexOf('.'))
}
/**
 * blob转text
 */
export function blob2Text<T>(blob: Blob) {
  return new Promise<T>((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      resolve(reader.result as T)
    }
    reader.onerror = reject
    reader.readAsText(blob)
  })
}

export function text2LogArray(text: string) {
  try {
    // 按行切割成数组
    let arr = text.split('\n')
    // 去掉空行
    for (let i = 0; i < arr.length; i++) {
      // 对每一行的最后的空格进行去除
      arr[i] = arr[i].replace(/\s+$/g, '')
    }
    arr = arr.filter(item => item)

    return arr.map((item) => {
      const itemObj = JSON.parse(item)
      return {
        event_time: itemObj.event_time,
        ...itemObj.data,
      }
    })
  }
  catch (error) {
    console.error('Error text2LogArray:', error)
    return []
  }
}
// 获取文件后缀
export function getFileExtension(filename: string) {
  const lastDotIndex = filename.lastIndexOf('.')
  if (lastDotIndex === -1) {
    return '' // 没有后缀
  }
  return filename.substring(lastDotIndex)
}

/**
 * 重试函数
 * @param operation
 * @param maxRetries 重试次数
 * @param interval 重试间隔时间
 */
export function retry<T>(operation: () => Promise<T>, maxRetries: number, interval: number): Promise<T> {
  return new Promise((resolve, reject) => {
    let retries = 0

    function attempt() {
      operation()
        .then(resolve)
        .catch((error) => {
          retries++
          if (retries >= maxRetries) {
            reject(error)
          }
          else {
            setTimeout(attempt, interval)
          }
        })
    }

    attempt()
  })
}

/**
 * 替换中间字符串为..., 显示字符串总长度为N
 * @returns string
 */
export function replaceMiddle(str: string, length: number = 16) {
  if (str.length <= length) {
    return str
  }
  const newStr = `${str.slice(0, length / 2)}...${str.slice(-length / 2)}`
  return newStr
}

/**
 * 生成列名 A-Z，AA-ZZ，AAA-ZZZ
 * @param num 列数 1+ 数字必须大于等于1
 * @returns A-Z，AA-ZZ，AAA-ZZZ ...
 */
export function generateColumnNames(num: number) {
  let result = ''
  while (num > 0) {
    const remainder = (num - 1) % 26
    const char = String.fromCharCode(65 + remainder)
    result = char + result
    num = Math.floor((num - 1) / 26)
  }
  return result
}
/**
 * 生成数据表格名称
 * @param allNames 数据表格名称列表
 * @returns 数据表格num
 */
export function generateSheetName(allNames: string[], locale = 'zh-CN') {
  const name = locale === 'zh-CN' ? '数据表格' : 'DataSheet'
  let index = 1
  let tempName = name + index
  while (allNames.includes(tempName)) {
    index++
    tempName = name + index
  }
  return tempName
}
/**
 * 获取url中的参数
 * @param field string
 * @param url string
 * @returns string
 */
export function getUrlQueryField(field: string, url?: string) {
  url = url || window.location.href
  const reg = new RegExp(`[?&]${field}=([^&#]*)`, 'i')
  const match = url.match(reg)
  return match ? decodeURIComponent(match[1]) : ''
}

/**
 * 设置 URL 中某个查询参数的值
 * @param field 查询参数的名称
 * @param val 查询参数的新值
 * @param url 原始 URL，默认为当前窗口的 URL
 * @returns 更新后的 URL
 */
export function setUrlQueryField(field: string, val: string, url?: string): string {
  url = url || window.location.href
  const encodedVal = encodeURIComponent(val)
  // 正则表达式：匹配指定的查询参数
  const reg = new RegExp(`([?&])${field}=.*?(?=&|$)`, 'i')
  // 检查 URL 中是否已经存在该查询参数
  if (url.match(reg)) {
    // 替换现有的查询参数值
    return url.replace(reg, `$1${field}=${encodedVal}`)
  }
  else {
    // 如果不存在，添加新的查询参数
    const separator = url.includes('?') ? '&' : '?'
    return `${url}${separator}${field}=${encodedVal}`
  }
}

export function replaceUrlDomain(url: string, newDomain: string) {
  let newUrl = ''
  try {
    const path = new URL(decodeURIComponent(url)).pathname
    newUrl = newDomain + path
  }
  catch (error) {
    console.error('Error URL:', error)
    newUrl = url
  }
  return encodeURIComponent(newUrl)
}

export function getUrlPath(url: string) {
  let origin = ''
  try {
    const uri = new URL(decodeURIComponent(url))
    origin = uri.origin + uri.pathname
  }
  catch (error) {
    console.error('Error URL:', error)
    origin = ''
  }
  return origin
}

export function getUrlDomain(url: string) {
  let origin = ''
  try {
    origin = new URL(decodeURIComponent(url)).origin
  }
  catch (error) {
    console.error('Error URL:', error)
    origin = ''
  }
  return encodeURIComponent(origin)
}

/**
 * 生成一个带有 resolve 和 reject 方法的 Promise 对象
 * Promise.withResolvers polyfill
 */
export function promiseWithResolvers<T>() {
  let resolve: (value: T | PromiseLike<T>) => void
  let reject: (reason?: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve: resolve!, reject: reject! }
}

/**
 * 将树形结构的原子能力列表拍平
 * @param treeData 树形结构的原子能力列表
 * @param widthParent 是否包含父节点
 * @returns 拍平后的原子能力列表
 */
export function flatAtomicTree(treeData: RPA.AtomTreeNode[], widthParent = true) {
  const flattenedArray: Array<RPA.AtomTreeNode & { parentKey: RPA.AtomTreeNode['key'] }> = []

  function traverse(nodes: RPA.AtomTreeNode[], parentKey: RPA.AtomTreeNode['key'] = '') {
    if (!nodes || !Array.isArray(nodes)) {
      return
    }

    for (const node of nodes) {
      if (widthParent || !node.atomics) {
        flattenedArray.push({ ...node, parentKey }) // 将当前节点添加到结果数组
      }

      if (node.atomics && Array.isArray(node.atomics)) {
        traverse(node.atomics, node.key) // 递归处理子节点
      }
    }
  }

  traverse(treeData)

  return flattenedArray
}

/**
 * 获取树形结构中的所有父节点，并返回父节点 key 组成的数组
 * @param treeData 原始树的根节点数组
 * @returns 父节点 key 组成的数组
 */
export function getParentNodes(treeData: RPA.AtomTreeNode[]): string[] {
  const parentNodes: string[] = []

  function traverse(nodes: RPA.AtomTreeNode[]) {
    for (const node of nodes) {
      if (node.atomics && node.atomics.length > 0) {
        parentNodes.push(node.uniqueId)
        traverse(node.atomics)
      }
    }
  }

  traverse(treeData)

  return parentNodes
}

/**
 * 比较两个数组，输出各自独有的项
 * @param arrOld 原数组
 * @param arrNew 新数组
 * @returns { deleteIds: string[], addIds: string[] } 删除的项和新增的项
 */
export function diffArrays<T>(arrOld: T[], arrNew: T[]): { deleteIds: T[], addIds: T[] } {
  const deleteIds = arrOld.filter(item => !arrNew.includes(item))
  const addIds = arrNew.filter(item => !arrOld.includes(item))
  return { deleteIds, addIds }
}

/**
 * 计算字符串的加权长度（英文1，中文2）
 * @param {string} str
 * @returns {number} 总长度
 */
export function getWeightedLength(str: string = ''): number {
  let len = 0
  str = str || ''
  for (let i = 0; i < str.length; i++) {
    // 检查字符是否为中文（Unicode范围参考）
    const charCode = str.charCodeAt(i)
    if (charCode >= 0x4E00 && charCode <= 0x9FA5) {
      len += 2 // 中文字符
    }
    else {
      len += 1 // 英文字符或其他
    }
  }
  return len
}

/**
 * 根据getWeightedLength 计算出的字符串返回32位以内的文本
 */
export function getWeightText(len: number = 32, text: string): string {
  let newText = ''
  let currentLength = 0
  for (let i = 0; i < text.length; i++) {
    const charCode = text.charCodeAt(i)
    const charLength = (charCode >= 0x4E00 && charCode <= 0x9FA5) ? 2 : 1 // 中文字符长度为2，其他字符长度为1
    if (currentLength + charLength > len) {
      break
    }
    newText += text[i]
    currentLength += charLength
  }
  return newText
}

/**
 * 计算antdesign table组件scrollY
 */
// 暂时设为常量，后续可以考虑使用从 antv tokens 中获取
const TABLE_HEADER_HEIGHT = 47 // 表头高度
const TABLE_CELL_HEIGHT = 49 // 表单项高度
export function getTableScrollY(tableMaxSize: number, rowLength: number) {
  const contentHeight = rowLength * TABLE_CELL_HEIGHT + TABLE_HEADER_HEIGHT
  // 判断 table 容器是否占满
  const isFull = tableMaxSize < contentHeight
  return isFull ? tableMaxSize - TABLE_HEADER_HEIGHT : undefined
}
