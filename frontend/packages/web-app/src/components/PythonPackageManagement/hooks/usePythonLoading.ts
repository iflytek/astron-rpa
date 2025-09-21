import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { isString } from 'lodash-es'
import { watch } from 'vue'

import { usePythonPackageStore } from '@/stores/usePythonPackageStore'

import { pythonLoadingMap } from '../config'
import { useManagePython } from '../hooks/useManagePython'
import { PythonLoadingModal } from '../modals'

export function usePythonLoading() {
  const pythonLoadingModal = NiceModal.useModal(PythonLoadingModal)
  const pythonPackageStore = usePythonPackageStore()

  const clearInstance = async () => {
    if (pythonLoadingModal.visible) {
      pythonPackageStore.setPyLoadingType('')
      pythonLoadingModal.hide()
    }
  }

  watch(() => pythonPackageStore.pyLoadingType, async () => {
    const pyLoadingType = pythonPackageStore.pyLoadingType
    clearInstance()

    if (!pyLoadingType)
      return

    const loadingConfig = { pyLoadingType, ...pythonLoadingMap[pyLoadingType] }
    if (loadingConfig.showMsg) {
      loadingConfig.loadingText.includes('成功') ? message.success(loadingConfig.loadingText) : message.error(loadingConfig.loadingText)
      return
    }

    pythonLoadingModal.show({
      loadingConfig,
      onConfirm: () => {
        isString(loadingConfig.okFn) && useManagePython()[loadingConfig.okFn]?.()
      },
    })
  })
}
