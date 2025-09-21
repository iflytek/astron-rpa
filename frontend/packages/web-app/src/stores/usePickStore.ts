import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

import BUS from '@/utils/eventBus'
import $loading from '@/utils/globalLoading'

import { RpaPicker } from '@/api/pick'
import { windowManager } from '@/platform'
import { useElementsStore } from '@/stores/useElementsStore'
import type { PickParams } from '@/types/resource'
import { ElementPickModal } from '@/views/Arrange/components/pick'

import { useVariableStore } from './useVariableStore'

export const usePickStore = defineStore('pickStore', () => {
  const isPicking = ref(false) // 正在拾取
  const isChecking = ref(false) // 正在校验
  const isDataPicking = ref(false) // 正在数据抓取
  const pickerType = ref('')

  const variableStore = useVariableStore()
  const { t } = useTranslation()
  const useElements = useElementsStore()
  const elementPickModal = NiceModal.useModal(ElementPickModal)

  const pickTypeMap = {
    '': 'ELEMENT', // 普通拾取
    'ELEMENT': 'ELEMENT', // 普通拾取
    'WEBPICK': 'ELEMENT', // web拾取
    'WINPICK': 'ELEMENT', // win拾取
    'SIMILAR': 'SIMILAR', // 相似拾取
    'CV': 'CV',
    'WINDOW': 'WINDOW', // 窗口拾取
    'POINT': 'POINT', // 坐标点拾取
    'BATCH': 'BATCH', // 批量抓取
  }
  const validTypeMap = {
    '': 'ELEMENT', // 普通拾取
    'ELEMENT': 'ELEMENT', // 普通拾取
    'WEBPICK': 'ELEMENT', // web拾取
    'WINPICK': 'ELEMENT', // win拾取
    'SIMILAR': 'ELEMENT', // 相似拾取
    'CV': 'CV',
    'WINDOW': 'WINDOW', // 窗口拾取
    'POINT': 'POINT', // 坐标点拾取
  }
  // 拾取结束
  function finishPick() {
    isPicking.value = false
    RpaPicker.destroy()
    windowManager.maximizeWindow(true)
  }
  // 校验结束
  function finishCheck(finshType = 'maximize') {
    isChecking.value = false
    RpaPicker.destroy()
    finshType === 'maximize' ? windowManager.maximizeWindow(true) : windowManager.restoreWindow()
  }
  // 开始鼠标位置拾取
  const startMousePick = (callback: (params: { success: boolean, data: any }) => void) => {
    // 启动拾取
    RpaPicker.create(() => {
      const _pickType = pickTypeMap.POINT
      pickerType.value = _pickType
      setTimeout(() => {
        const sendParams: PickParams = {
          pick_sign: 'START',
          pick_type: _pickType,
          data: '',
        }
        RpaPicker.send(sendParams)
        windowManager.minimizeWindow()
      }, 500)
    })
    // 绑定消息
    RpaPicker.bindMessage((res) => {
      const { key, data, err_msg } = res || {} // key: 'success' | 'error' | 'ping'
      console.log('startPick res: ', res)
      if (key === 'success' && data) {
        const dataObj = JSON.parse(data)
        callback && callback({
          success: true,
          data: dataObj,
        })
        finishPick()
      }
      if (key === 'error') {
        const errorMsg = data || err_msg || t('rpaPickerUnavailable')
        message.error(errorMsg)
        finishPick()
      }
      if (key === 'cancel') {
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
    })
  }

  /**
   * 开始拾取
   * @param type  类型 '' 普通拾取， ''similar' 相似度拾取, 'cv' cv拾取
   * @param element  元素数据， 相似度拾取时，element不能为空
   * @param callback 成功/失败回调
   */
  const startPick = (type: string, element: any, callback: (params: { success: boolean, data: any }) => void) => {
    type = type.toUpperCase()
    isPicking.value = true
    // 启动拾取
    RpaPicker.create(() => {
      const _pickType = pickTypeMap[type] || 'ELEMENT'
      console.log('type: ', type)
      console.log('_pickType: ', _pickType)
      console.log('element: ', element)
      pickerType.value = _pickType
      const data = element ? JSON.stringify(element) : ''
      const ext_data = { global: variableStore.globalVariableList }
      setTimeout(() => {
        const sendParams: PickParams = {
          pick_sign: 'START',
          pick_type: _pickType,
          data,
        }
        if (_pickType === 'SIMILAR') { // 相似拾取 带上ext_data
          sendParams.ext_data = ext_data
        }
        RpaPicker.send(sendParams)
        windowManager.minimizeWindow()
      }, 500)
    })
    // 绑定消息
    RpaPicker.bindMessage((res) => {
      const { key, data, err_msg } = res || {} // key: 'success' | 'error' | 'ping'
      if (key === 'success' && data) {
        finishPick()
        const dataObj = JSON.parse(data)
        if (dataObj.app) {
          callback?.({ success: true, data: dataObj })
        }
      }
      if (key === 'error') {
        const errorMsg = data || err_msg || t('rpaPickerUnavailable')
        message.error(errorMsg)
        finishPick()
      }
      if (key === 'cancel') {
        finishPick()
      }
    })
    // 绑定关闭
    RpaPicker.bindClose(() => {
      callback?.({
        success: false,
        data: null,
      })
      finishPick()
    })
    // 绑定错误
    RpaPicker.bindError(() => {
      message.error(t('rpaPickerUnavailable'))
    })
  }
  // 开始校验
  const startCheck = (type: string, data: any, callback: (params: { success: boolean, data: any }) => void, finshType = 'maximize') => {
    // console.log('startCheck: ', data)
    type = type.toUpperCase()
    isChecking.value = true
    const ext_data = { global: variableStore.globalVariableList }
    // 启动校验
    RpaPicker.create(() => {
      windowManager.minimizeWindow()
      setTimeout(() => {
        const _pickType = validTypeMap[type] || 'ELEMENT'
        RpaPicker.send({ pick_sign: 'VALIDATE', pick_type: _pickType, data, ext_data })
        isChecking.value = false // 校验时，不显示loading
      }, 500)
    })
    // 绑定消息
    RpaPicker.bindMessage((res) => {
      console.log('startCheck res: ', res)
      if (res && res.key === 'success') {
        callback && callback({
          success: true,
          data: res,
        })
      }
      else {
        const { data, err_msg } = res || {}
        const errorMsg = data || err_msg || t('rpaPickerUnavailable')
        message.error(errorMsg)
        callback?.({
          success: false,
          data: null,
        })
      }
      finishCheck(finshType)
    })
    // 绑定关闭
    RpaPicker.bindClose(() => {
      callback?.({
        success: false,
        data: null,
      })
      finishCheck(finshType)
    })
    // 绑定错误
    RpaPicker.bindError(() => {
      message.error(t('rpaPickerUnavailable'))
    })
  }

  // 重新拾取
  const repick = (type: string, isModal: boolean = false, group: string, callback?: () => void) => {
    startPick(type, '', (res) => {
      // console.log('repick res: ', res)
      if (res.success) {
        useElements.setTempElement(res.data, 'repick', group)
      }
      isModal && elementPickModal.show()
      callback && callback()
    })
  }
  // 相似拾取
  const similarPick = (element: any, callback?: () => void) => {
    startPick('SIMILAR', element, (res) => {
      console.log('similarPick res: ', res)
      if (res.success) {
        useElements.setTempElement(res.data, 'similar')
      }
      callback && callback()
    })
  }
  // 新建拾取
  const newPick = (type: string, callback?: () => void) => {
    startPick(type, '', (res) => {
      if (res.success) {
        useElements.setTempElement(res.data)
        elementPickModal.show({ isContinue: true })
      }
      callback?.()
    })
  }

  // groupPick
  const groupPick = (type: string, group: string, callback?: () => void) => {
    startPick(type, '', (res) => {
      if (res.success) {
        useElements.setTempElement(res.data, 'new', group)
        elementPickModal.show()
        callback && callback()
      }
    })
  }
  // set isDataPicking
  const setDataPicking = (val: boolean) => {
    isDataPicking.value = val
    BUS.$once('batch-close', () => {
      isDataPicking.value = false
    })
  }

  watch(isDataPicking, (val) => {
    if (val) {
      $loading.open({ msg: '正在抓取，无法操作客户端', timeout: 100 * 60 })
    }
    else {
      $loading.close()
    }
  })

  return {
    isPicking,
    isChecking,
    isDataPicking,
    startMousePick,
    startPick,
    startCheck,
    repick,
    similarPick,
    newPick,
    groupPick,
    setDataPicking,
  }
})
