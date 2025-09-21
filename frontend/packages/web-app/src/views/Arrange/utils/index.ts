import { useEventBus } from '@vueuse/core'
import { difference, includes } from 'lodash-es'
import { SnowflakeIdv1 } from 'simple-flakeid'

import { atomScrollIntoViewKey } from '@/constants/eventBusKey'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { Catch, CONVERT_MAP, CvImageExist, Else, ElseIf, FileExist, Finally, FolderExist, ForDict, ForEnd, ForList, ForStep, Group, GroupEnd, If, IfEnd, Module, Process, Try, TryEnd, While, WindowExist } from '@/views/Arrange/config/atomKeyMap'

import { defaultValueText, elementTag } from '../config/flow'

/**
 * 富文本转后端所需数据
 * @param {Any} params 富文本字符串
 * @param {boolean} isView 是否是视图展示
 * @returns 解析后的后端所需数据格式
 */
export function varHtmlToStr(params, isView = true) {
  const str = replaceInconformity(params)
  // 防止用户的文案中带有data-value以及data-type 会进入变量的逻辑处理
  const isVariable = str.includes('<ifly')
  const arr = str.split('<ifly')
  const result = []
  arr.forEach((item) => {
    const ends = item.split('</ifly>')
    result.push(...ends.filter(end => end))
  })
  return result.map((item) => {
    let res
    if (item.includes('data-value') && isVariable) {
      const valueType = item.match(/data-type="(\S*)"/)[1]
      const val = item.match(/data-value="(\S*)"/)[1]
      // 元素需要的格式 e["val"] 变量格式 val or g.val
      res = {
        value: valueType === elementTag && !isView ? `e["${val}"]` : `${val}`,
        type: valueType === elementTag ? 'ele' : 'other',
      }
    }
    else {
      const v = item.replace(/<p\b[^>]*>(.*?)<\/p>/gi, '$1')
      res = { value: v, type: 'string' }
    }
    return res
  })
}

/**
 * 富文本转后端所需数据, 替换不符合规则的输入格式
 * @param {Any} params 富文本字符串
 */
export function replaceInconformity(params) {
  let str = String(params)
    .replaceAll(defaultValueText, '')
    .replaceAll('<br>', '')
    .replaceAll(/&nbsp;/gi, ' ') // 过滤<p><br></p>
  str = str.replaceAll('<p></p>', '')
  return str // 过滤<p><br></p>
}

/**
 * 解析特殊字符
 */
export function decodeHtml(text) {
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
 * @param array 数组
 * @param prefix 前缀字符
 * @param splitStr 分割字符
 * @returns 数字后缀自增的名称
 */
export function generateName(array, prefix, splitStr = '_') {
  let selfNum = 1
  const existCheckNum = []
  const defaultCheckNum = []
  let diffCheckNum = []
  array.forEach((v) => {
    if (v) {
      const lastIndex = v.lastIndexOf(prefix + splitStr)
      const checkName = v.substring(0, lastIndex + (prefix + splitStr).length) // 需要检查的字符串
      const checkNum = v.substring(checkName.length, v.length) // 自增数字
      if (prefix + splitStr === checkName) {
        existCheckNum.push(checkNum)
        defaultCheckNum.push(`${selfNum++}`)
      }
    }
  })

  diffCheckNum = difference(defaultCheckNum, existCheckNum)
  diffCheckNum && diffCheckNum.length && (selfNum = diffCheckNum[0])
  const randomName = prefix + splitStr + selfNum // 生成名称
  return randomName
}

const levelPos = {}

export function setLevelPos(key: string, level: number, pos: number) {
  levelPos[pos] = `${level}-${key}`
}

export function generateAtomLevel(curAtomKey: string, curAtomIdx: number, preKey: string, preLevel: number) {
  const arr = Object.keys(levelPos)
  let res = -1
  arr.some((pos, i) => {
    if (Number(pos) > curAtomIdx) {
      res = i - 2
      return true
    }
    return false
  })
  let curLevel = 1
  const parent = res > -1 ? levelPos[arr[res]] : null
  const cur = CONVERT_MAP[curAtomKey]
  if (!cur) {
    return [If, Else, ElseIf, Try, Catch, Finally, ForStep, ForDict, ForList, While, Group, CvImageExist, FileExist, FolderExist, WindowExist].includes(preKey) ? preLevel + 1 : preLevel
  }
  if (parent) {
    const [parentLevel, parentKey] = parent.split('-')
    if ([ElseIf, Else].includes(cur.key)) {
      curLevel = [If, CvImageExist, FileExist, FolderExist, WindowExist].includes(parentKey) ? Number(parentLevel) : Number(parentLevel) + 1
    }
    else if ([Catch, Finally].includes(cur.key)) {
      curLevel = parentKey !== Try ? Number(parentLevel) + 1 : Number(parentLevel)
    }
    else if ([IfEnd, TryEnd, ForEnd, GroupEnd].includes(parentKey)) {
      curLevel = Number(parentLevel)
    }
    else {
      curLevel = Number(parentLevel) + 1
    }
  }
  return curLevel
}

let timer = null
export function setRoll(type: 'left' | 'right' | 'top', id: string, step = 150) {
  // 滚动的数值  或者  +- = 值  就是相应位置
  timer && clearTimeout(timer)
  timer = setTimeout(() => {
    const scrollDom = document.getElementById(id)
    switch (type) {
      case 'left':
        scrollDom.scrollLeft += step
        break
      case 'right':
        scrollDom.scrollLeft -= step
        break
      case 'top':
        scrollDom.scrollTop += step
        break
      default:
        scrollDom.scrollTop -= step
        break
    }
    clearTimeout(timer)
    timer = null
  }, 0)
}

// 将原子能力滚动到可视区域内
export function atomScrollIntoView(atomId: string) {
  const bus = useEventBus(atomScrollIntoViewKey)
  bus.emit(atomId)
}

/**
 * 挑选出当前流程可选的子流程流程和模块列表
 * @param item
 */
export function pickProcessAndModuleOptions(item: RPA.AtomDisplayItem) {
  const processStore = useProcessStore()
  const formTypeParams = item?.formType?.params?.filters

  if (includes(formTypeParams, 'Process')) { // 判断是否是选择子流程
    // 挑选出所有的流程
    const flowList = processStore.processList.filter(item => item.resourceCategory === 'process')
    // 过滤掉自己和主流程
    const filterFlow = flowList.filter(item => item.resourceId !== processStore.activeProcessId && !item.isMain)
    // 把流程节点转换为表单选项
    return filterFlow.map(item => ({
      label: item.name,
      value: item.resourceId,
    }))
  }

  if (includes(formTypeParams, 'PyModule')) { // 判断是否是选择py模块
    // 挑选出所有 py 模块
    const pyModuleList = processStore.processList.filter(item => item.resourceCategory === 'module')
    return pyModuleList.map(item => ({
      label: item.name,
      value: item.resourceId,
    }))
  }

  return item?.options
}

/**
 * 查询子流程引用
 * @param processId
 */
export function querySubProcessQuote(processId: string) {
  // console.time('useSearchSubProcess')
  const processStore = useProcessStore()
  const processList = processStore.processList
  const result = []
  processList.forEach((pItem: any) => {
    const searchProcessItem = useProjectDocStore().userFlowNode(pItem.resourceId).reduce((acc, item, index) => {
      if ([Process, Module].includes(item.key) && item.inputList.find(i => i.value === processId)) {
        acc.push({
          id: item.id, // 运行子流程节点id
          alias: item.alias, // 运行子流程节点名称
          row: index + 1, // 运行子流程节点所在的行
        })
      }
      return acc
    }, [])

    searchProcessItem.length > 0 && result.push({
      processId: pItem.resourceId, // 流程id
      processName: pItem.name, // 流程名称
      nodes: searchProcessItem, // 运行子流程节点列表
    })
  })
  // console.timeEnd('useSearchSubProcess')
  return result
}

// 删除子流程引用
export function delectSubProcessQuote(processId: string) {
  const processStore = useProcessStore()
  const flowStore = useFlowStore()
  const processList = processStore.processList
  processList.forEach((pItem: any) => {
    useProjectDocStore().userFlowNode(pItem.resourceId).forEach((item, index) => {
      const findIdx = item.inputList.findIndex(i => i.value === processId)
      if ([Process, Module].includes(item.key) && findIdx > -1) {
        item.inputList[findIdx].value = ''
        if (processStore.activeProcessId === pItem.resourceId) {
          const uiData = flowStore.simpleFlowUIData[index]
          uiData.inputList[findIdx].value = ''
          flowStore.setSimpleFlowUIDataByType({ ...uiData }, index, true)
        }
      }
    })
  })
}
