import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { isArray, isNil, last } from 'lodash-es'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { WINDOW_NAME } from '@/constants'
import type { RecordActionType } from '@/constants/record'
import { RECORD_EVENT } from '@/constants/record'
import { useHistory } from '@/hooks/useHistory'
import { utilsManager } from '@/platform'
import type { PickElementType } from '@/types/resource'

import { emitToRecordMenu, RecordEvent } from './utils'

interface W2WType {
  from: WINDOW_NAME // 来源窗口
  target: WINDOW_NAME // 目标窗口
  type: RECORD_EVENT // 类型
  data?: any // 数据
}

interface RecordData {
  action: RecordActionType
  pickInfo?: string // 拾取信息
  name?: string // 元素名称
}

export const useRecordStore = defineStore('record', () => {
  const { t } = useTranslation()
  const isRecording = ref(false)
  const { state: list, perform, undo, redo, canUndo, canRedo } = useHistory<RecordData[]>([])

  const recordEvent = new RecordEvent(
    res => handleMessage(res),
    () => message.error(t('rpaPickerUnavailable')),
  )

  utilsManager.listenEvent('w2w', ({ from, target, type, data }: W2WType) => {
    if (from !== WINDOW_NAME.RECORD_MENU || target !== WINDOW_NAME.RECORD)
      return

    if (type === RECORD_EVENT.PAUSE_PICK) {
      recordEvent.pausePick()
    }
    else if (type === RECORD_EVENT.RESUME_PICK) {
      recordEvent.resumePick()
    }
    else if (type === RECORD_EVENT.CLICK_ACTION) {
      setPickInfo(data)
    }
  })

  // 停止录制
  const stopRecord = () => {
    recordEvent.stopPick()
    recordEvent.destroy()
  }

  const toggleRecord = async () => {
    isRecording.value ? recordEvent.pauseRecord() : recordEvent.startRecord()
    isRecording.value = !isRecording.value
  }

  // 处理 message
  const handleMessage = (res: { data: string, key: string }) => {
    const { data, key } = res

    console.log('handleMessage', res)

    switch (key) {
      // 鼠标悬停两秒元素 - 告知前端弹出红框，用户鼠标移动到此可弹出原子能力选择窗口
      case 'record_automic_start':
        notifyMenuShow(data)
        break

      case 'record_automic_draw_end':
        notifyMenuHide()
        break

      // 开始录制
      case 'record_start':
        isRecording.value = true
        break

      // 暂停录制
      case 'record_pause':
        isRecording.value = false
        notifyMenuHide()
        break

      // 获取拾取信息成功
      case 'record_success':
      case 'success':
        data && recordEvent.pickInfoCallback(data)
        break

      default:
        break
    }
  }

  // 通知 menu 窗口显示
  const notifyMenuShow = (data: string) => {
    const { mouse_x, mouse_y, domain = 'web' } = JSON.parse(data)

    if (isNil(mouse_x) || isNil(mouse_y))
      return

    const isWeb = domain === 'web'
    emitToRecordMenu(RECORD_EVENT.SHOW_MENU, { x: mouse_x, y: mouse_y, isWeb })
  }

  // 通知 menu 窗口隐藏
  const notifyMenuHide = () => {
    emitToRecordMenu(RECORD_EVENT.HIDE_MENU)
  }

  const setPickInfo = async (data: string) => {
    const itemData: RecordData = { action: data as RecordActionType }
    // 获取当前的拾取信息
    const pickInfo = await recordEvent.getPickInfo()

    try {
      const info = JSON.parse(pickInfo) as PickElementType
      const tagName = (isArray(info.path) ? last(info.path).tag_name : info.path.tag) || '未知标签'
      itemData.name = tagName
      itemData.pickInfo = pickInfo
    }
    catch (error) {
      console.error(error)
    }

    perform((draft) => {
      draft.push(itemData)
    })
  }

  function clearAll() {
    perform(() => ([]))
  }

  function clear(index: number) {
    perform((draft) => {
      draft.splice(index, 1)
    })
  }

  return { isRecording, list, undo, redo, canUndo, canRedo, stopRecord, toggleRecord, clearAll, clear }
})
