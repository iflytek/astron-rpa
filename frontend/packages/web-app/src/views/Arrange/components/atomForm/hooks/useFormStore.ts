import { createInjectionState } from '@vueuse/core'
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

const [useProvideFormStore, useFormStore] = createInjectionState(() => {
  const { canvasManager } = useProcessStore()

  const nodeParameter = computed(() => canvasManager.activeTab?.nodeParameter)
  const atomTab = computed<RPA.Process.AtomTabs[]>(() => nodeParameter.value?.formTabs.value ?? [])

  const formattedTabs = computed(() => {
    return atomTab.value.map((item, index) => ({
      title: item.name,
      value: index,
    }))
  })

  const formValues = computed(() => {
    const formItems = atomTab.value.flatMap(item => item.params).flatMap(i => i.formItems)
    return formItems.reduce((acc, curr) => {
      acc[curr.key] = curr.value
      return acc
    }, {} as Record<string, any>)
  })

  return { nodeParameter, atomTab, formattedTabs, formValues }
})

export { useProvideFormStore, useFormStore }
