import { createInjectionState, reactiveComputed, useToggle } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { find, isEmpty } from 'lodash-es'
import { ref, shallowRef, computed, markRaw } from 'vue'

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
  const management = computed(() => processStore.canvasManager.activeTab?.configParameter)

  // 是组件且是主流程
  const isMainProcess = computed(() => processStore.canvasManager.activeTab.state?.isMain)
  const isComponent = computed(() => processStore.isComponent)
  const isComponentAndMainProcess = computed(() => isComponent.value && isMainProcess.value)

  let findQuotedRow: RPA.ConfigParamData | null = null

  const configParamsTabConfig = reactiveComputed<TabConfig>(() => ({
    text: isComponentAndMainProcess.value ? 'components.componentAttribute' : 'configParameters',
    key: 'config-params',
    icon: isComponentAndMainProcess.value ? 'bottom-menu-component-attribute-manage' : 'bottom-menu-config-param-manage',
    component: markRaw(Manager),
    rightExtra: markRaw(RightExtra),
  }))

  // watch(() => processStore.activeProcessId, () => {
  //   toggleQuoted(false)
  // })

  const findQuoted = (row?: RPA.ConfigParamData) => {
    // findQuotedRow = row || findQuotedRow
    // const processData = useFlowStore().simpleFlowUIData
    // const list = processData.reduce((acc, node, index) => {
    //   const formItems = [...node?.inputList, ...node?.outputList, ...node?.advanced]
    //   const findItem = formItems.find(item => Array.isArray(item.value) && find(item.value, { type: 'p_var', value: findQuotedRow.varName }))
    //   if (findItem) {
    //     acc.push({
    //       ...node,
    //       index: index + 1,
    //       level: 1,
    //     })
    //   }
    //   return acc
    // }, [])
    // const items = isEmpty(list)
    //   ? []
    //   : [{
    //       processId: processStore.activeProcess.resourceId,
    //       processName: processStore.activeProcess.name,
    //       atoms: list,
    //     }]

    // quotedData.value = { name: findQuotedRow.varName, items }
    // if (!row) {
    //   message.success('刷新成功')
    // }
    // toggleQuoted(true)
  }

  return {
    quotedData,
    configParamsTabConfig,
    management,
    isComponent,
    isMainProcess,
    isComponentAndMainProcess,
    searchText,
    isQuoted,
    toggleQuoted,
    findQuoted,
  }
})

export { useProvideConfigParameter, useConfigParameter }
