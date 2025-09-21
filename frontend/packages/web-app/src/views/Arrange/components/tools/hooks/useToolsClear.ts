import { message, Modal } from 'ant-design-vue'

import { isPyModel, useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsClear() {
  const handleClear = () => {
    Modal.confirm({
      title: '提示',
      zIndex: 100,
      content: '编辑区所有数据将被清空无法恢复，是否确定？',
      okText: '确定',
      cancelText: '取消',
      onOk: () => {
        useProjectDocStore().clear()
      },
      centered: true,
      keyboard: false,
    })
  }
  const item: ArrangeTools = {
    key: 'clear',
    title: 'clear',
    name: '',
    fontSize: '',
    icon: 'tools-clear',
    action: '',
    loading: false,
    show: true,
    disable: ({ status }) => ['debug', 'run'].includes(status) || isPyModel(useProcessStore().activeProcess?.resourceCategory),
    clickFn: handleClear,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning('正在运行/调试, 不可清空')
        return false
      }
      return true
    },
  }
  return item
}
