<!-- 子流程选择组件 -->
<script setup lang="ts">
import { some, find, get, has, isArray, isEmpty, isEqual } from 'lodash-es'
import { computed, ref, toRaw, watch } from 'vue'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import { getConfigParams } from '@/api/atom'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore.ts'

import VarValueEditor from '@/views/Arrange/components/bottomTools/components/ConfigParameter/VarValueEditor.vue'
import { OTHER_IN_TYPE } from '@/constants/atom'

interface ParamItemValue {
  rpa: 'special'
  value: Array<any>
}

type ParamValues = Array<{ varId: string, varName: string, varValue: ParamItemValue }>

const props = defineProps<{ renderData: RPA.AtomDisplayItem }>()
const emits = defineEmits<{ refresh: [value: ParamValues] }>()

const gridData = ref<RPA.ConfigParamData[]>([])

const flowStore = useFlowStore()
const processStore = useProcessStore()

const gridOptions: VxeGridProps<RPA.ConfigParamData> = {
  height: 160,
  size: 'mini',
  scrollY: { enabled: true },
  border: true,
  showOverflow: true,
  keepSource: true,
  round: true,
  columns: [
    { field: 'varName', title: '参数名', width: 100 },
    { field: 'varValue', title: '参数值', slots: { default: 'value_default' } },
  ],
}

const linkageFormItem = computed(() => {
  // 获取联动的选择子流程/子模块 id
  const linkageKey = get(props.renderData, ['formType', 'params', 'linkage'])
  // 只从输入信息中查找联动
  return find(flowStore.activeAtom.inputList, { key: linkageKey })
})

const linkageKey = computed(() => linkageFormItem.value?.value)

function safeParse(str) {
  try {
    return JSON.parse(str)
  } catch {
    return str
  }
}

watch(linkageKey, async (newLinkageKey) => {
  if (!newLinkageKey) {
    gridData.value = []
    return
  }

  // 判断是子流程还是 python 子模块
  const processType = get(linkageFormItem.value, ['formType', 'params', 'filters'])
  const idParams = processType === 'PyModule' ? { moduleId: newLinkageKey } : { processId: newLinkageKey }
  const list = await getConfigParams({ robotId: processStore.project.id, ...idParams })

  const values = props.renderData.value as unknown as ParamValues
  // 当前保存的参数值
  const currentParamMap = new Map((isArray(values) && values.map(p => [p.varId, p.varValue.value])) || [])
  // 配置参数默认值
  const defaultParamMap = new Map(list.map(p => [p.id, p.varValue]))

  gridData.value = list.filter(item => item.varDirection === 0).map(item => {
    const _varValue = currentParamMap.get(item.id) || defaultParamMap.get(item.id)
    const varValue = safeParse(_varValue)
    const illegal = !isArray(varValue) || isEmpty(varValue) || some(varValue, item => !has(item, 'type') || !has(item, 'value'))

    return {
      ...item,
      varValue: illegal ? [{ type: OTHER_IN_TYPE, value: _varValue ?? '' }] : varValue
    }
  })
}, { immediate: true })

watch(() => gridData.value, (newGridData) => {
  const values: ParamValues = toRaw(newGridData).map(item => ({
    varId: item.id,
    varName: item.varName,
    varValue: {
      rpa: 'special',
      value: safeParse(item.varValue as unknown as string) as Array<any>,
    },
  }))

  if (isEqual(values, props.renderData.value)) {
    return
  }

  emits('refresh', values)
}, { deep: true })
</script>

<!-- 输入参数可支持普通文本模式、python模式和变量选择填入 -->
<template>
  <VxeGrid v-bind="gridOptions" class="params-table" :data="gridData">
    <template #value_default="{ row }">
      <VarValueEditor
        v-model:var-value="row.varValue"
        :var-type="row.varType"
        form-type="INPUT_VARIABLE_PYTHON"
        size="small"
      />
    </template>
  </VxeGrid>
</template>

<style lang="scss" scoped>
.params-table {
  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;

  overflow: hidden;
  width: 100%;
}
</style>
