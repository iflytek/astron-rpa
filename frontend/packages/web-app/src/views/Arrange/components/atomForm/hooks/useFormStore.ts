import { createInjectionState } from '@vueuse/core'
import { computed, onMounted, ref } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'
import BUS from '@/utils/eventBus'
import type { Step } from '@/components/ChainOfThought/utils'

const [useProvideFormStore, useFormStore] = createInjectionState(() => {
  const { canvasManager } = useProcessStore()

  const chainOfThoughtSteps = ref<Step[]>([])

  onMounted(() => {
    BUS.$on('cua-test-complete', (steps: string) => {
      chainOfThoughtSteps.value = JSON.parse(steps) as Step[]
    })
  })

  const nodeParameter = computed(() => canvasManager.activeTab?.nodeParameter)
  const atom = computed(() => nodeParameter.value?.activeAtom)
  const atomTab = computed<RPA.Process.AtomTabs[]>(() => nodeParameter.value?.formTabs.value ?? [])

  const formValues = computed(() => {
    const formItems = atomTab.value.flatMap(item => item.params).flatMap(i => i.formItems)
    return formItems.reduce((acc, curr) => {
      acc[curr.key] = curr.value
      return acc
    }, {} as Record<string, any>)
  })

  return { atom, chainOfThoughtSteps, nodeParameter, atomTab, formValues }
})

export { useProvideFormStore, useFormStore }
