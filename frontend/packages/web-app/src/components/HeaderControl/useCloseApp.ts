import { ExclamationCircleOutlined } from '@ant-design/icons-vue'
import { App } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { createVNode } from 'vue'
import { useRoute } from 'vue-router'

import { useRouteBack } from '@/hooks/useCommonRoute'
import { windowManager } from '@/platform'
import useUserSettingStore from '@/stores/useUserSetting.ts'

import CloseTip from './CloseTip.vue'

export function useCloseApp() {
  const { message, modal } = App.useApp()
  const { t } = useTranslation()
  const route = useRoute()
  let modalInstance = null
  let timeoutModal = null

  const closeWindow = () => {
    windowManager.closeWindow()
  }

  const minimizeWindowTray = () => {
    windowManager.hideWindow()
  }

  const modalCloseApp = () => {
    if (modalInstance)
      return

    modalInstance = modal.confirm({
      title: t('closeConfirmExit'),
      icon: createVNode(ExclamationCircleOutlined),
      content: createVNode(CloseTip),
      okText: t('confirm'),
      cancelText: t('cancel'),
      onOk() {
        useUserSettingStore().userSetting.commonSetting.closeMainPage ? minimizeWindowTray() : closeWindow()
        modalInstance = null
      },
      onCancel() {
        modalInstance = null
      },
      centered: true,
      keyboard: false,
    })
  }
  // 网络超时，提示
  const modalSaveTimeout = () => {
    if (timeoutModal)
      return
    timeoutModal = modal.confirm({
      title: t('networkError'),
      content: t('saveErrorAndQuit'),
      okText: t('confirm'),
      cancelText: t('cancel'),
      onOk() {
        useRouteBack()
        timeoutModal = null
      },
      onCancel() {
        timeoutModal = null
      },
      centered: true,
      keyboard: false,
    })
  }

  return { closeApp: modalCloseApp }
}
