import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { RpaCvPicker } from '@/api/cvpick'
import { windowManager } from '@/platform'

export const useCvPickStore = defineStore('cvPickStore', () => {
  const isPicking = ref(false) // 正在拾取
  const isChecking = ref(false) // 正在校验

  const pickTypeMap = { // Cv拾取拾取类型传ELEMENT
    '': 'ELEMENT',
    'cv': 'ELEMENT',
    'CV': 'ELEMENT',
  }
  const pickerType = ref('')
  // 拾取结束
  function finishPick() {
    isPicking.value = false
    RpaCvPicker.destroy()
    windowManager.maximizeWindow(true)
    console.log('finishPick')
  }
  // 校验结束
  function finishCheck() {
    isChecking.value = false
    RpaCvPicker.destroy()
    windowManager.maximizeWindow(true)
  }
  // 开始拾取
  /**
   *
   * @param type  类型 '' 普通拾取， ''similar' 相似度拾取, 'cv' cv拾取
   * @param element  元素数据， 相似度拾取时，element不能为空
   * @param pickStep  pickStep 拾取步骤 'new' | 'repick' | 'anchor'
   * @param callback 成功/失败回调
   */
  const startCvPick = (type: string, element: any, pickStep = 'new', callback: (params: { success: boolean, data: any }) => void) => {
    isPicking.value = true
    // 启动拾取
    RpaCvPicker.create(() => {
      windowManager.minimizeWindow()
      const _pickType = pickTypeMap[type] || 'ELEMENT'
      pickerType.value = _pickType
      const pickParams = element ? JSON.stringify(element) : ''
      const sign = pickStep === 'anchor' ? 'DESIGNATE' : 'START'
      setTimeout(() => {
        RpaCvPicker.send({ pick_sign: sign, pick_type: _pickType, data: pickParams })
      }, 500)
    })
    // 绑定消息
    RpaCvPicker.bindMessage((res) => {
      const { key, data, err_msg } = res || {} // key: 'success' | 'error' | 'ping'
      console.log('bindMessage: ', res)
      if (key === 'success' && data) {
        const dataObj = JSON.parse(data)
        callback && callback({
          success: true,
          data: dataObj,
        })
        finishPick()
      }
      if (key === 'cancel') {
        message.error(err_msg || '已取消拾取')
        finishPick()
      }
      if (key === 'error') {
        message.error(err_msg || useTranslation().t('rpaPickerUnavailable'))
        finishPick()
      }
    })
    // 绑定关闭
    RpaCvPicker.bindClose(() => {
      callback
      && callback({
        success: false,
        data: null,
      })
      finishPick()
    })
    // 绑定错误
    RpaCvPicker.bindError(() => {
      message.error(useTranslation().t('rpaPickerUnavailable'))
    })
  }
  // 开始校验
  const startCvCheck = (type: string, data: any, callback: (params: { success: boolean, data: any }) => void) => {
    // console.log('startCheck: ', data)
    isChecking.value = true
    // 启动校验
    RpaCvPicker.create(() => {
      windowManager.minimizeWindow()
      setTimeout(() => {
        const _pickType = pickTypeMap[type] || 'ELEMENT'
        RpaCvPicker.send({ pick_sign: 'VALIDATE', pick_type: _pickType, data })
        isChecking.value = false // 校验时，不显示loading
      }, 500)
    })
    // 绑定消息
    RpaCvPicker.bindMessage((res) => {
      const { key, data, err_msg } = res || {} // key: 'success' | 'error' | 'ping'
      if (key === 'success' && data) {
        callback
        && callback({
          success: true,
          data: res,
        })
        finishPick()
      }
      if (key === 'cancel') {
        message.error(err_msg || '已取消拾取')
        finishPick()
      }
      if (key === 'error') {
        message.error(err_msg || useTranslation().t('rpaPickerUnavailable'))
        finishPick()
      }

      finishCheck()
    })
    // 绑定关闭
    RpaCvPicker.bindClose(() => {
      callback
      && callback({
        success: false,
        data: null,
      })
      finishCheck()
    })
    // 绑定错误
    RpaCvPicker.bindError(() => {
      message.error(useTranslation().t('rpaPickerUnavailable'))
    })
  }

  return {
    startCvPick,
    isPicking,
    isChecking,
    startCvCheck,
  }
})
