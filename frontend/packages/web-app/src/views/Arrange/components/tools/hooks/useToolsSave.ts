import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'

import { SAVE } from '@/constants/shortcuts'
import { useProcessStore } from '@/stores/useProcessStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsSave() {
  const processStore = useProcessStore()

  const save = throttle(async () => {
    try {
      await processStore.saveProject()
      message.success('保存成功')
    }
    catch {
      message.success('保存失败')
    }
  }, 1500, { leading: true, trailing: false })

  const item: ArrangeTools = {
    key: 'save',
    title: 'save',
    name: 'save',
    fontSize: '',
    icon: 'tools-save',
    action: '',
    loading: false,
    show: true,
    disable: ({ status }) => processStore.operationDisabled || ['debug', 'run'].includes(status),
    hotkey: SAVE,
    clickFn: save,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning('正在运行/调试, 不可保存')
      }

      return !disable
    },
  }

  return item
}
