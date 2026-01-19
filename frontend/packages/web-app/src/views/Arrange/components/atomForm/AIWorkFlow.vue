<script lang="ts" setup>
import { useAsyncState } from '@vueuse/core'
import { cloneDeep, isEmpty, isEqual } from 'lodash-es'
import { computed, ref, toRaw, watch } from 'vue'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import { getWorkflowList } from '@/api/robot'

import AtomConfig from './AtomConfig.vue'

interface VarValue {
  rpa: 'special'
  value: any
}

interface AgentInputParam {
  name: string
  type: string
  authId: number
  form: RPA.AtomDisplayItem
}

interface ParamValues {
  agentId: string
  authId: number
  inputs: Array<{
    key: string
    value: VarValue
    type: string
  }>
}

const props = defineProps<{ params: RPA.AtomDisplayItem }>()
const emits = defineEmits<{ refresh: [value: ParamValues] }>()
const STRING_FORM_ITEM: Partial<RPA.AtomDisplayItem> = {
  types: 'Any',
  formType: {
    type: 'INPUT_VARIABLE_PYTHON',
  },
}
const FILE_FORM_ITEM: Partial<RPA.AtomDisplayItem> = {
  types: 'PATH',
  formType: {
    type: 'INPUT_VARIABLE_PYTHON_FILE',
    params: { filters: [], file_type: 'file' },
  },
}

const { state: workflowList } = useAsyncState(getWorkflowList, [])

const selectedAgent = ref((props.params.value as unknown as ParamValues)?.agentId ?? '')
const gridData = ref<Array<AgentInputParam>>([])

const agentOptions = computed(() => {
  return workflowList.value?.map(item => ({
    label: item.name,
    value: item.flowId,
  }))
})

const gridOptions: VxeGridProps<AgentInputParam> = {
  height: 160,
  size: 'mini',
  scrollY: { enabled: true },
  border: true,
  showOverflow: true,
  keepSource: true,
  round: true,
  columns: [
    { field: 'name', title: '参数名', width: 60 },
    { field: 'type', title: '类型', width: 60, slots: { default: 'type_default' } },
    { field: 'form', title: '参数值', slots: { default: 'value_default' } },
  ],
}

const handleDataChange = (newData: Array<AgentInputParam> = gridData.value) => {
  const agent = workflowList.value?.find(item => item.flowId === selectedAgent.value)

  const values = toRaw(newData).map(item => ({
    key: item.name,
    value: {
      rpa: 'special' as const,
      value: toRaw(item.form.value),
    },
    type: item.type,
  }))

  const agentValue: ParamValues = {
    agentId: selectedAgent.value,
    authId: agent?.authId ?? 0,
    inputs: values,
  }

  if (!isEqual(agentValue, toRaw(props.params.value))) {
    emits('refresh', agentValue)
  }
}

watch(() => gridData.value, handleDataChange, { deep: true })

watch([selectedAgent, workflowList], ([agentId, list]) => {
  const agent = list?.find(item => item.flowId === agentId)

  if (!isEmpty(agent?.inputs)) {
    const preValues = (props.params.value as unknown as ParamValues)?.inputs ?? []

    gridData.value = agent.inputs.map((item) => {
      const preValue = preValues.find(it => it.key === item.name)
      return {
        name: item.name,
        type: item.fileType ?? 'string',
        authId: agent.authId,
        form: {
          ...(item.fileType === 'file' ? FILE_FORM_ITEM : STRING_FORM_ITEM),
          key: item.name,
          value: cloneDeep(preValue?.value?.value),
        },
      }
    })
  }
  else {
    gridData.value = []
  }
})
</script>

<template>
  <div class="w-full">
    <a-select
      v-model:value="selectedAgent"
      class="bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] rounded-[8px] w-full"
      :options="agentOptions"
    />
    <div class="text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65] text-[12px] mt-2.5">
      输入参数
    </div>
    <VxeGrid v-bind="gridOptions" class="params-table mt-2" :data="gridData">
      <template #value_default="{ row }">
        <AtomConfig
          :key="row.name"
          :form-item="row.form"
          size="small"
          @update="handleDataChange()"
        />
      </template>
      <template #type_default="{ row }">
        {{ row.type === 'file' ? '文件' : '字符串' }}
      </template>
    </VxeGrid>
  </div>
</template>

<style lang="scss" scoped>
.params-table {
  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;

  overflow: hidden;
  width: 100%;
}
</style>
