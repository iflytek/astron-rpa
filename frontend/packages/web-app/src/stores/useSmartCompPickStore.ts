import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { RpaPicker } from '@/api/pick'
import { useSmartCompPickWindow } from '@/components/SmartComponent/hooks'
import { WINDOW_NAME } from '@/constants'
import { SMART_COMP_PICK_EVENT } from '@/constants/smartCompPick'
import { utilsManager, windowManager } from '@/platform'

import { useVariableStore } from './useVariableStore'

export const useSmartCompPickStore = defineStore('smartCompPickStore', () => {
  const isPicking = ref(false) // 正在拾取
  const pickData = ref() // 拾取数据
  let currentCallback: ((params: { success: boolean, data: any }) => void) | null = null // 当前拾取的回调函数

  const variableStore = useVariableStore()
  const { t } = useTranslation()
  const { open: openPickMenuWindow } = useSmartCompPickWindow()

  utilsManager.listenEvent('w2w', ({ from, target, type: eventType }: any) => {
    if (!isPicking.value || from !== WINDOW_NAME.SMART_COMP_PICK_MENU || target !== WINDOW_NAME.MAIN) {
      return
    }

    if (eventType === SMART_COMP_PICK_EVENT.ZOOM_IN) {
      // 放大选区
      startPickAction('SMART_COMPONENT_PREVIOUS')
    }
    else if (eventType === SMART_COMP_PICK_EVENT.ZOOM_OUT) {
      // 缩小选区
      startPickAction('SMART_COMPONENT_NEXT')
    }
    else if (eventType === SMART_COMP_PICK_EVENT.CONFIRM) {
      // 确认
      startPickAction('SMART_COMPONENT_END', () => {
        finishPick()
        currentCallback && currentCallback({ success: true, data: pickData.value })
      })
    }
    else if (eventType === SMART_COMP_PICK_EVENT.CANCEL) {
      // 取消
      startPickAction('SMART_COMPONENT_CANCEL', () => {
        finishPick()
        currentCallback && currentCallback({ success: false, data: null })
      })
    }
    else if (eventType === SMART_COMP_PICK_EVENT.ERROR_DIALOG_CONFIRM) {
      // 如果是已达最大/最小层级，通过 pickData 计算位置并恢复操作区显示
      // 如果是其他错误（如非网页元素），重新开始拾取
      const menuPosition = calculateMenuPosition(pickData.value)
      if (menuPosition) {
        notifyMenuShow(menuPosition)
      }
      else {
        RpaPicker.destroy()
        startPickAction('SMART_COMPONENT_START')
      }
    }
  })

  // 通知悬浮窗显示
  const notifyMenuShow = (data: { x: number, y: number }) => {
    windowManager.emitTo({
      type: SMART_COMP_PICK_EVENT.SHOW_MENU,
      target: WINDOW_NAME.SMART_COMP_PICK_MENU,
      from: WINDOW_NAME.MAIN,
      data,
    })
  }

  // 通知显示错误对话框
  const notifyErrorDialog = (errorMsg?: string) => {
    windowManager.emitTo({
      type: SMART_COMP_PICK_EVENT.SHOW_ERROR_DIALOG,
      target: WINDOW_NAME.SMART_COMP_PICK_MENU,
      from: WINDOW_NAME.MAIN,
      data: { errorMsg },
    })
  }

  // 通知悬浮窗隐藏
  const notifyMenuHide = () => {
    windowManager.emitTo({
      type: SMART_COMP_PICK_EVENT.HIDE_MENU,
      target: WINDOW_NAME.SMART_COMP_PICK_MENU,
      from: WINDOW_NAME.MAIN,
    })
  }

  // 根据 pickData 计算菜单位置
  const calculateMenuPosition = (data: any): { x: number, y: number } | null => {
    if (!data)
      return null

    const rect = data.path?.rect
    const win_rect = data.path?.win_rect
    if (!rect || !win_rect)
      return null

    const devicePixelRatio = window.devicePixelRatio || 1
    const menuWidth = 160 * devicePixelRatio
    const menuHeight = 40 * devicePixelRatio

    const winWidth = win_rect.right
    const winHeight = win_rect.bottom

    const rightBottomX = rect.right
    const rightBottomY = rect.bottom

    // 检查元素右下角是否在窗口范围内
    const isRightBottomInWindow = rightBottomX >= 0
      && rightBottomX <= winWidth
      && rightBottomY >= 0
      && rightBottomY <= winHeight

    // 检查元素右下角位置是否能完整显示菜单（考虑菜单宽度和高度）
    const canShowAtRightBottom = rightBottomX - menuWidth >= 0
      && rightBottomY + menuHeight <= winHeight

    let x = 0
    let y = 0

    if (isRightBottomInWindow && canShowAtRightBottom) {
      // 显示在右下角
      x = rightBottomX - menuWidth
      y = rightBottomY
    }
    else {
      // 显示在右上角（rect 上方）
      x = rightBottomX - menuWidth
      y = rect.y - menuHeight

      // 如果右上角也超出窗口范围，则调整到窗口内
      if (x < 0) {
        x = 0
      }
      if (y < 0) {
        // 如果上方空间不够，则显示在 rect 下方（但仍在窗口内）
        y = rect.bottom
      }
      // 确保菜单不会超出窗口右边界和下边界
      if (x + menuWidth > winWidth) {
        x = winWidth - menuWidth
      }
      if (y + menuHeight > winHeight) {
        y = winHeight - menuHeight
      }
    }

    return { x, y }
  }

  // 拾取结束
  function finishPick() {
    isPicking.value = false
    notifyMenuHide()
    RpaPicker.destroy()
    windowManager.maximizeWindow(true)
  }

  /**
   * 开始拾取
   * @param callback 成功/失败回调
   */
  const startPick = (callback: (params: { success: boolean, data: any }) => void) => {
    isPicking.value = true
    pickData.value = null
    currentCallback = callback // 保存当前回调

    // 打开悬浮窗
    openPickMenuWindow()

    startPickAction('SMART_COMPONENT_START')
  }

  /**
   * 开始校验
   */
  const startCheck = (data: any, callback: (params: { success: boolean, data: any }) => void) => {
    const ext_data = { global: variableStore.globalVariableList }
    // 启动校验
    RpaPicker.create(() => {
      windowManager.minimizeWindow()
      setTimeout(() => {
        RpaPicker.send({ pick_sign: 'VALIDATE', pick_type: 'ELEMENT', data, ext_data })
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
      finishPick()
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

  const startPickAction = (action: string, ofterSendCb?: () => void) => {
    // 启动拾取
    RpaPicker.create(() => {
      setTimeout(() => {
        const sendParams = {
          pick_sign: 'SMART_COMPONENT',
          pick_type: 'ELEMENT',
          data: JSON.stringify(pickData.value),
          smart_component_action: action,
        }
        RpaPicker.send(sendParams)
        ofterSendCb && ofterSendCb()
        if (action === 'SMART_COMPONENT_START') {
          windowManager.minimizeWindow()
        }
      }, 500)
    })

    // 绑定消息
    RpaPicker.bindMessage((res) => {
      const { key, data, err_msg } = res || {} // key: 'success' | 'error' | 'ping'
      console.log('smartCompPick bindMessage: ', res)

      if (key === 'success' && data) {
        pickData.value = JSON.parse(data)
        const menuPosition = calculateMenuPosition(pickData.value)

        if (!menuPosition) {
          // 当拾取元素非网页元素时，rect 和 win_rect 不存在，显示错误对话框
          RpaPicker.destroy()
          notifyErrorDialog('当前仅支持网页自动化')
          return
        }

        notifyMenuShow(menuPosition)
        RpaPicker.destroy()
      }
      if (key === 'error') {
        const errorMsg = data || err_msg || t('rpaPickerUnavailable')
        console.error(errorMsg)
        if (action === 'SMART_COMPONENT_PREVIOUS') {
          RpaPicker.destroy()
          notifyErrorDialog('已达最大层级')
        }
        else if (action === 'SMART_COMPONENT_NEXT') {
          RpaPicker.destroy()
          notifyErrorDialog('已达最小层级')
        }
        else {
          message.error(errorMsg)
          finishPick()
        }
      }
      if (key === 'cancel') {
        finishPick()
      }
    })

    // 绑定关闭
    RpaPicker.bindClose(() => {
      RpaPicker.destroy()
    })

    // 绑定错误
    RpaPicker.bindError(() => {
      message.error(t('rpaPickerUnavailable'))
    })
  }

  const resetPick = () => {
    if (isPicking.value) {
      startPickAction('SMART_COMPONENT_CANCEL', () => {
        finishPick()
      })
    }
  }

  return {
    isPicking,
    startPick,
    startCheck,
    resetPick,
  }
})
