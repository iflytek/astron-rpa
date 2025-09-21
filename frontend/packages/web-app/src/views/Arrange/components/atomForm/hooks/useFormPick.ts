import type { Ref } from 'vue'

import BUS from '@/utils/eventBus'

import { useElementsStore } from '@/stores/useElementsStore'
import { usePickStore } from '@/stores/usePickStore'
import { useCreateWindow } from '@/views/Arrange/hook/useCreateWindow'

function useFormPick(type: string = '', status?: Ref<boolean>, elementPickModal?: () => void) {
  const { openDataPickWindow } = useCreateWindow()
  const usePick = usePickStore()
  const useElements = useElementsStore()

  if (type === 'BATCH') { // 数据抓取开启另外的窗口
    openDataPickWindow()
    return
  }

  if (type === 'POINT') {
    usePick.startMousePick((res) => {
      BUS.$emit('pick-done', { data: res.data?.point, value: res.data, picker_type: res.data?.picker_type })
    })
    return
  }

  status.value = true
  usePick.startPick(type, '', (res) => {
    status.value = false
    if (!res.success)
      return

    useElements.setTempElement(res.data)
    elementPickModal?.()
  })
}

export default useFormPick
