import { message } from 'ant-design-vue'

import { usePickStore } from '@/stores/usePickStore'
import { addDataBatchAtomData } from '@/views/Arrange/components/flow/hooks/useFlow'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsDataPick() {
  const handleOpenBatchPick = async () => {
    await useCreateWindow().openDataPickWindow()
    addDataBatchAtomData()
  }

  const item: ArrangeTools = {
    key: 'dataCrawling',
    title: 'dataScraping',
    name: 'dataScraping',
    fontSize: '',
    icon: 'tools-data-pick',
    action: 'design_dataPick',
    loading: false,
    clickFn: handleOpenBatchPick,
    show: true,
    disable: ({ status }) => ['debug', 'run'].includes(status) || usePickStore().isDataPicking,
    validateFn: ({ disable }) => {
      if (disable) {
        message.warning('正在运行/调试, 请先停止')
        return false
      }
      return true
    },
  }

  return item
}
