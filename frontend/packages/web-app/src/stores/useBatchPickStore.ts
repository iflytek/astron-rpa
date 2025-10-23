import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { RpaPicker } from '@/api/pick'
import { windowManager } from '@/platform'
import type { PickParams } from '@/types/resource'

import { useVariableStore } from './useVariableStore'

export const useBatchPickStore = defineStore('batchPick', () => {
  const isPicking = ref(false)
  const pickerType = ref('')
  const variableStore = useVariableStore()
  let isHighlight = false // 是否高亮元素

  const { t } = useTranslation()

  const pickTypeMap = {
    BATCH: 'BATCH', // 批量抓取
    HIGHLIGHT: 'HIGHLIGHT', // 高亮
    GRAB: 'GRAB', // 抓取
    ELEMENT: 'ELEMENT',
  }

  // 拾取结束
  function finishPick() {
    isPicking.value = false
    RpaPicker.destroy()
    windowManager.restoreWindow()
  }
  function finishCheck() {
    isPicking.value = false
    RpaPicker.destroy()
  }
  /**
   * 启动数据抓取
   */
  const startBatchPick = (type: string, batchParams: object, callback: (params: { success: boolean, data: any }) => void) => {
    console.log('startBatchPick: ', batchParams)
    type = type.toUpperCase()
    isPicking.value = true

    // 启动拾取
    RpaPicker.create(() => {
      const _pickType = pickTypeMap[type] || 'BATCH'
      pickerType.value = _pickType
      const data = batchParams ? JSON.stringify(batchParams) : ''
      const ext_data = { global: variableStore.globalVariableList }
      setTimeout(() => {
        const sendParams: PickParams = {
          pick_sign: 'START',
          pick_type: _pickType,
          data,
          ext_data,
        }
        RpaPicker.send(sendParams)
      }, 500)
    })
    // 绑定消息
    RpaPicker.bindMessage((res) => {
      const { key, data, err_msg } = res || {} // key: 'success' | 'error' | 'ping' | 'interaction'
      if (key === 'success' && data) {
        const dataObj = JSON.parse(data)
        if (dataObj.app) {
          callback && callback({
            success: true,
            data: dataObj,
          })
        }
      }
      if (key === 'error') {
        message.error(err_msg || t('rpaPickerUnavailable'))
        callback && callback({
          success: false,
          data: null,
        })
        finishPick()
      }
      if (key === 'cancel') {
        callback && callback({
          success: false,
          data: null,
        })
        finishPick()
      }
    })
    // 绑定关闭
    RpaPicker.bindClose(() => {
      callback
      && callback({
        success: false,
        data: null,
      })
      finishPick()
    })
    // 绑定错误
    RpaPicker.bindError(() => {
      message.error(t('rpaPickerUnavailable'))
      isPicking.value = false
    })
  }

  /**
   * 发送消息
   */
  const sendMessage = (params: object) => {
    RpaPicker.send(params)
  }
  /**
   * 获取元素数据，类似于拾取校验，和执行原子能力
   */
  const getBatchData = (type: string, data: string, callback: (params: { success: boolean, data: any }) => void) => {
    type = type.toUpperCase()
    isPicking.value = true
    const ext_data = { global: variableStore.globalVariableList }
    // 启动校验
    RpaPicker.create(() => {
      setTimeout(() => {
        const _pickType = pickTypeMap[type]
        RpaPicker.send({ pick_sign: 'GAIN', pick_type: _pickType, data, ext_data })
        isPicking.value = false
      }, 500)
    })
    // 绑定消息
    RpaPicker.bindMessage((res) => {
      if (res.key === 'success' && res.data) {
        const dataObj = JSON.parse(res.data)
        callback && callback({
          success: true,
          data: dataObj,
        })
      }
    })
    // 绑定关闭
    RpaPicker.bindClose(() => {
      callback
      && callback({
        success: false,
        data: null,
      })
      finishCheck()
    })
    // 绑定错误
    RpaPicker.bindError(() => {
      message.error(t('rpaPickerUnavailable'))
    })
  }
  /**
   * 高亮元素
   */
  const highLight = (data: string, callback?: (params: { success: boolean, data: any }) => void) => {
    if (isHighlight)
      return
    const ext_data = { global: variableStore.globalVariableList }
    RpaPicker.create(() => {
      isHighlight = true
      setTimeout(() => {
        RpaPicker.send({
          pick_sign: 'HIGHLIGHT',
          pick_type: pickTypeMap.ELEMENT,
          data,
          ext_data,
        })
      }, 500)
    })
    RpaPicker.bindClose(() => {
      RpaPicker.destroy()
      isHighlight = false
    })
    RpaPicker.bindError(() => {
      message.error(t('rpaPickerUnavailable'))
      isHighlight = false
    })
    RpaPicker.bindMessage((res) => {
      callback && callback({
        success: true,
        data: res,
      })
    })
  }

  return {
    isPicking,
    startBatchPick,
    sendMessage,
    getBatchData,
    highLight,
    finishCheck,
  }
})
