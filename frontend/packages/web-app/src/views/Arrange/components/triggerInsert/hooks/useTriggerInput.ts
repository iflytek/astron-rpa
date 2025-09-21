import { uniqBy } from 'lodash-es'
import { ref } from 'vue'

import { getRecentAtomUsage } from '@/utils/atomHistory'
import { simpleFuzzyMatch } from '@/utils/common'

import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'

let triggerPreId = ''
const inputPos = ref('')
export function setTriggerPreId(id: string) {
  if (id === triggerPreId)
    return
  const findIndex = useFlowStore().simpleFlowUIData.findIndex(i => i.id === triggerPreId)
  if (findIndex > -1) {
    const curItem = useFlowStore().simpleFlowUIData[findIndex]
    useFlowStore().setSimpleFlowUIDataByType({ ...curItem, showInput: false }, findIndex, true)
  }
  triggerPreId = id
  const curIndex = useFlowStore().simpleFlowUIData.findIndex(i => i.id === id)
  if (curIndex > -1) {
    const curItem = useFlowStore().simpleFlowUIData[curIndex]
    useFlowStore().setSimpleFlowUIDataByType({ ...curItem, showInput: true }, findIndex, true)
  }
}
export function getTriggerPreId() {
  return triggerPreId
}

export function setInputPos(pos: string) {
  inputPos.value = pos
}

export function getInputPos() {
  return inputPos
}

// 触发式插入，原子能力搜索及推荐
export function useSearch(emits) {
  const processStore = useProcessStore()
  // const allAtomList = ref([]) // 所有原子能力列表数据
  const searchResult = ref<RPA.AtomTreeNode[]>([]) // 下拉菜单数据
  const defaultRecommend = ref<RPA.AtomTreeNode[]>([]) // 原子能力推荐列表
  const searchValue = ref('') // 搜索框的值

  // 生成原子能力推荐列表（最近5条使用的原子能力）
  const generateRecommend = () => {
    const recentUsage = getRecentAtomUsage(5)
    if (recentUsage.length > 0) {
      defaultRecommend.value = recentUsage.map(record => ({
        key: record.key,
        title: record.title,
        icon: record.icon,
        parentKey: record.parentKey,
      }))
    }
    else {
      defaultRecommend.value = []
    }
  }

  // 获取搜索结果的文本内容 数组形式
  const getTitleTexts = (title: string) => {
    return title?.split('').map((text, index) => {
      return {
        text,
        active: searchValue.value.includes(text) ? index === title.indexOf(text) : false,
      }
    })
  }

  // 搜索
  const search = (value: string) => {
    searchValue.value = value

    if (value) {
      searchResult.value = uniqBy(processStore.atomicTreeDataFlat.filter(i => simpleFuzzyMatch(searchValue.value, i.title)), 'key')
      return
    }
    // 没有搜索值，展示推荐的原子能力列表
    searchResult.value = defaultRecommend.value
  }

  // 聚焦时显示最近使用的原子能力
  const onFocus = () => {
    generateRecommend()
    searchResult.value = defaultRecommend.value
  }

  // 选中
  const select = (value: string) => emits('select', value)

  return {
    searchValue,
    search,
    searchResult,
    select,
    getTitleTexts,
    onFocus,
  }
}

// 触发式插入，语音输入  TODO - 接入星火大模型
export function useRecord() {
  const inputRef = ref(null) // 输入框对象
  const recoder = ref(null) // 录音对象
  const originText = ref('') // 输入框原始文本
  const aiQuestion = ref('') // 语音识别后的文本， 原始文本 + 语音识别文本拼接
  const status = ref('') // 状态 '' 默认  answering  正在回答  recoding 正在录音

  // 创建录音对象  TODO - 接入星火大模型
  const creatRecordr = () => {

  }

  //  TODO - 接入星火大模型
  // const recodeFn = (text: string) => {
  //   aiQuestion.value = (originText.value || '') + text;
  //   aiQuestionChange();
  // }

  // 开始录音
  const startRecoding = (e: Event) => {
    if (status.value === 'answering')
      return false
    e.preventDefault()
    status.value === 'recoding'
    recoder.value.recStart()
    // 录音前，保存当前输入框的文本
    const tempText = aiQuestion.value
    const originVal = tempText.trim()
    if (originVal) {
      const endsStr = originVal[originVal.length - 1]
      if (![',', '.', '。', '，'].includes(endsStr)) {
        aiQuestion.value += '，'
      }
    }
    originText.value = aiQuestion.value
  }

  // 停止录音
  const stopRecoding = (e) => {
    e.preventDefault()
    status.value === ''
    recoder.value.recStop()
    originText.value = aiQuestion.value
  }

  // 文本内容变化
  const aiQuestionChange = () => {
    if (inputRef.value) {
      inputRef.value.scrollLeft = inputRef.value.scrollWidth
    }
  }

  // 发送问题给星火大模型
  const sendQuestion = (e, isEnter = false) => {
    if (isEnter) {
      if (e.keyCode === 13 && !e.shiftKey) {
        e.stopPropagation()
        e.preventDefault()
        sendToXinghuo()
      }
      return
    }
    sendToXinghuo()
  }

  // 发送给星火大模型
  const sendToXinghuo = () => {
    console.log('sendQuestion', aiQuestion.value)
  }

  return {
    inputRef,
    status,
    aiQuestion,
    aiQuestionChange,
    creatRecordr,
    startRecoding,
    stopRecoding,
    sendQuestion,
  }
}
