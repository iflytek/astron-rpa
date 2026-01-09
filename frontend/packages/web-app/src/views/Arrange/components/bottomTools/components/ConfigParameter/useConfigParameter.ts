import { createInjectionState, reactiveComputed, useToggle } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { find, isEmpty } from 'lodash-es'
import { ref, shallowRef, watch } from 'vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import type { PickUseItemType } from '@/types/resource.d'

import type { TabConfig } from '../../types.ts'

import Manager from './Manager.vue'
import RightExtra from './RightExtra.vue'

const [useProvideConfigParameter, useConfigParameter] = createInjectionState(() => {
  const processStore = useProcessStore()
  const searchText = ref('')

  const [isQuoted, toggleQuoted] = useToggle(false) // 是否开启查找引用
  const quotedData = shallowRef<{ name: string, items: Array<PickUseItemType> }>()

  let findQuotedRow: RPA.ConfigParamData | null = null

  const config: TabConfig = reactiveComputed(() => ({
    text: processStore.isComponent && processStore.activeProcess?.isMain ? 'components.componentAttribute' : 'configParameters',
    key: 'config-params',
    icon: processStore.isComponent && processStore.activeProcess?.isMain ? 'bottom-menu-component-attribute-manage' : 'bottom-menu-config-param-manage',
    component: Manager,
    rightExtra: RightExtra,
  }))

  watch(() => processStore.activeProcessId, () => {
    toggleQuoted(false)
  })

  const findQuoted = (row?: RPA.ConfigParamData) => {
    findQuotedRow = row || findQuotedRow
    const processData = useFlowStore().simpleFlowUIData

    const list = processData.reduce((acc, node, index) => {
      const formItems = [...node?.inputList, ...node?.outputList, ...node?.advanced]
      const findItem = formItems.find(item => Array.isArray(item.value) && find(item.value, { type: 'p_var', value: findQuotedRow.varName }))
      if (findItem) {
        acc.push({
          ...node,
          index: index + 1,
          level: 1,
        })
      }
      return acc
    }, [])

    const items = isEmpty(list)
      ? []
      : [{
          processId: processStore.activeProcess.resourceId,
          processName: processStore.activeProcess.name,
          atoms: list,
        }]

    quotedData.value = { name: findQuotedRow.varName, items }
    if (!row) {
      message.success('刷新成功')
    }
    toggleQuoted(true)
  }

  return {
    quotedData,
    config,
    searchText,
    isQuoted,
    toggleQuoted,
    findQuoted,
  }
})

export { useConfigParameter, useProvideConfigParameter }
