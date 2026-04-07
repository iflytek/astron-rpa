import { useEventBus } from '@vueuse/core'
import { includes } from 'lodash-es'
import { SnowflakeIdv1 } from 'simple-flakeid'

import { atomScrollIntoViewKey } from '@/constants/eventBusKey'
import { useProcessStore } from '@/stores/useProcessStore'

import { defaultValueText, elementTag } from '../config/flow'

/**
 * 解析富文本中的变量和文本内容
 * @param params 富文本字符串
 * @param isView 是否是视图展示（默认 true）
 * @returns 解析后的数据数组，每个元素包含 value 和 type
 */
export function varHtmlToStr(params: any, isView = true): Array<{ value: string; type: string }> {
  const str = replaceInconformity(params)
  
  // 提取纯文本的辅助函数（移除 <p> 标签）
  const extractText = (text: string): string => {
    return text.replace(/<p\b[^>]*>(.*?)<\/p>/gi, '$1').trim()
  }

  // 如果没有变量标签，直接返回纯文本
  if (!str.includes('<ifly')) {
    const text = extractText(str)
    return text ? [{ value: text, type: 'string' }] : []
  }

  const result: Array<{ value: string; type: string }> = []
  const variablePattern = /<ifly([^>]*)>(.*?)<\/ifly>/g
  let lastIndex = 0
  let match: RegExpExecArray | null

  variablePattern.lastIndex = 0

  while ((match = variablePattern.exec(str)) !== null) {
    // 添加变量标签前的文本
    if (match.index > lastIndex) {
      const textBefore = extractText(str.slice(lastIndex, match.index))
      if (textBefore) {
        result.push({ value: textBefore, type: 'string' })
      }
    }

    // 处理变量标签：提取 data-type 和 data-value 属性
    const attributes = match[1]
    const dataTypeMatch = attributes.match(/data-type="([^"]*)"/)
    const dataValueMatch = attributes.match(/data-value="([^"]*)"/)
    
    if (dataTypeMatch && dataValueMatch) {
      const valueType = dataTypeMatch[1]
      const val = dataValueMatch[1]
      const isElement = valueType === elementTag
      
      result.push({
        value: isElement && !isView ? `e["${val}"]` : val,
        type: isElement ? 'ele' : 'other',
      })
    }

    lastIndex = variablePattern.lastIndex
  }

  // 添加最后剩余的文本
  if (lastIndex < str.length) {
    const textAfter = extractText(str.slice(lastIndex))
    if (textAfter) {
      result.push({ value: textAfter, type: 'string' })
    }
  }

  return result
}

/**
 * 富文本转后端所需数据, 替换不符合规则的输入格式
 * @param {Any} params 富文本字符串
 */
export function replaceInconformity(params) {
  const str = String(params)
    .replaceAll(defaultValueText, '')
    .replaceAll('<br>', '')
    .replaceAll(/&nbsp;/gi, ' ')
    .replaceAll('<p></p>', '')

  return str
}

/**
 * 解析特殊字符
 */
export function decodeHtml(text: string) {
  let resultText = text
  if (typeof text === 'string') {
    resultText = text
      .replaceAll('&amp;', '&')
      .replaceAll('&lt;', '<')
      .replaceAll('&gt;', '>')
      .replaceAll('&quot;', '"')
      .replaceAll('&#x27;', '\'')
      .replaceAll('\\r\\n', '\r\n')
  }
  return resultText
}

/**
 * 生成唯一id
 */
const genId = new SnowflakeIdv1({ workerId: 1 })
export function genNonDuplicateID(head: string = ''): string {
  const headStr = head || 'bh'
  return `${headStr}${genId.NextId()}`
}

/**
 * 自动生成名称，数字后缀自增
 * @param existNames 已存在的名称数组
 * @param prefix 前缀字符
 * @param splitStr 分割字符
 * @returns 数字后缀自增的名称
 */
export function generateName(existNames: string[], prefix: string, splitStr = '_') {
  let num = 1
  let name = `${prefix}${splitStr}${num}`
  
  while (existNames.includes(name)) {
    num++
    name = `${prefix}${splitStr}${num}`
  }
  
  return name
}

// 将原子能力滚动到可视区域内
export function atomScrollIntoView(atomId: string) {
  const bus = useEventBus(atomScrollIntoViewKey)
  bus.emit(atomId)
}

/**
 * 查询子流程引用
 * @param processId
 */
export function querySubProcessQuote(processId: string) {
  // console.time('useSearchSubProcess')
  const processStore = useProcessStore()
  // const processList = processStore.processList.filter(item => item.resourceCategory !== 'module')
  const result = []
  // processList.forEach((pItem: any) => {
  //   const searchProcessItem = useProjectDocStore().userFlowNode(pItem.resourceId).reduce((acc, item, index) => {
  //     if ([Process, ProcessOld, Module].includes(item.key) && item.inputList.find(i => i.value === processId)) {
  //       acc.push({
  //         id: item.id, // 运行子流程节点id
  //         alias: item.alias, // 运行子流程节点名称
  //         row: index + 1, // 运行子流程节点所在的行
  //       })
  //     }
  //     return acc
  //   }, [])

  //   searchProcessItem.length > 0 && result.push({
  //     processId: pItem.resourceId, // 流程id
  //     processName: pItem.name, // 流程名称
  //     nodes: searchProcessItem, // 运行子流程节点列表
  //   })
  // })
  // console.timeEnd('useSearchSubProcess')
  return result
}

// 删除子流程引用
export function delectSubProcessQuote(processId: string) {
  const processStore = useProcessStore()
  // const flowStore = useFlowStore()
  // const processList = processStore.processList.filter(item => item.resourceCategory !== 'module')
  // processList.forEach((pItem: any) => {
  //   useProjectDocStore().userFlowNode(pItem.resourceId).forEach((item, index) => {
  //     const findIdx = item.inputList.findIndex(i => i.value === processId)
  //     if ([Process, ProcessOld, Module].includes(item.key) && findIdx > -1) {
  //       item.inputList[findIdx].value = ''
  //       if (processStore.activeProcessId === pItem.resourceId) {
  //         const uiData = flowStore.simpleFlowUIData[index]
  //         uiData.inputList[findIdx].value = ''
  //         flowStore.setSimpleFlowUIDataByType({ ...uiData }, index, true)
  //       }
  //     }
  //   })
  // })
}
