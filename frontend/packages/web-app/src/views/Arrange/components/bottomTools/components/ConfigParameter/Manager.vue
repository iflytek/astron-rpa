<script lang="ts" setup>
import { useTheme } from '@rpa/components'
import { computedWithControl } from '@vueuse/core'
import { Button, Input, message, Select } from 'ant-design-vue'
import { debounce, isArray, isEmpty } from 'lodash-es'
import { computed } from 'vue'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import ElementUseFlowList from '@/components/ElementUseFlowList/Index.vue'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { OTHER_IN_TYPE, PARAMETER_VAR_IN_TYPE } from '@/constants/atom'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore.ts'
import AtomConfig from '@/views/Arrange/components/atomForm/AtomConfig.vue'

import { getChildProcessParameterOption, getMainProcessParameterOption, usageOptions } from './constant.ts'
import { useConfigParameter } from './useConfigParameter.ts'

interface LocalConfigParamData extends RPA.ConfigParamData {
  perVarName: string
  formItem?: RPA.AtomDisplayItem
}

const props = defineProps<{ height?: number }>()

const { colorTheme } = useTheme()
const flowStore = useFlowStore()
const processStore = useProcessStore()
const { searchText, isQuoted, quotedData, findQuoted } = useConfigParameter()
const [messageApi, contextHolder] = message.useMessage()

const gridOptions: VxeGridProps<RPA.ConfigParamData> = {
  size: 'small',
  scrollY: { enabled: true, gt: 0 },
  border: 'default',
  showOverflow: true,
  keepSource: true,
  rowConfig: { isHover: true },
  columns: [
    { field: 'varName', title: '参数名称', slots: { default: 'name_default' } },
    { field: 'varDirection', title: '输入/输出', slots: { default: 'usage_default' } },
    { field: 'varType', title: '参数类型', slots: { default: 'type_default' } },
    { field: 'varValue', title: '默认值', slots: { default: 'default_default' } },
    { field: 'varDescribe', title: '参数描述', slots: { default: 'desc_default' } },
    { field: 'operation', title: '操作', width: 120, slots: { default: 'operation_default' } },
  ],
}

// 由 String 转换成 Array
function convertVarValueToArray(varValue: unknown): RPA.AtomFormItemResult[] {
  if (isArray(varValue) && !isEmpty(varValue)) {
    return varValue
  }

  if (typeof varValue === 'string') {
    try {
      const parsed = JSON.parse(varValue)
      return isArray(parsed) ? parsed : [{ type: OTHER_IN_TYPE, value: varValue }]
    }
    catch {
      return [{ type: OTHER_IN_TYPE, value: varValue }]
    }
  }

  return [{ type: OTHER_IN_TYPE, value: '' }]
}

// 由 Array 转换成 String
function convertArrayToVarValue(value: RPA.AtomFormItemResult[]): string {
  if (!isArray(value) || value.length === 0) {
    return ''
  }
  return JSON.stringify(value)
}

// 创建 formItem
function createFormItem(item: RPA.ConfigParamData): RPA.AtomDisplayItem {
  const varValueArray = convertVarValueToArray(item.varValue)
  return {
    types: item.varType || 'Any',
    name: item.id,
    key: item.id,
    title: item.varName,
    value: varValueArray,
    formType: {
      type: 'INPUT_PYTHON',
    },
  } as RPA.AtomDisplayItem
}

const searchedData = computedWithControl(() => processStore.parameters.length, () => {
  let list = processStore.parameters

  // 根据参数名称查询
  if (searchText.value) {
    list = processStore.parameters.filter(item => item.varName.includes(searchText.value))
  }

  return list.map(item => ({
    ...item,
    perVarName: item.varName,
    formItem: createFormItem(item),
  }))
})

const emptyText = computed(() => searchText.value ? '未搜索到配置参数' : undefined)

const varTypeOptions = computed(() => {
  // 主进程和子进程可选择的类型不一样
  if (processStore.activeProcess.isMain && !processStore.isComponent) {
    return getMainProcessParameterOption()
  }

  return getChildProcessParameterOption()
})

// 删除事件
function deleteEvent(row: RPA.ConfigParamData) {
  const deleteFn = async () => {
    await processStore.deleteParameter(row)

    flowStore.flowVariableUpdate({
      varName: row.varName,
      varType: PARAMETER_VAR_IN_TYPE,
      type: 'delete',
      processId: processStore.activeProcessId,
    })
  }
  GlobalModal.confirm({
    title: '删除',
    content: '删除后所有引用了该参数的操作都将失效。删除后无法恢复，请确认。',
    onOk: deleteFn,
    centered: true,
    keyboard: false,
  })
}

async function handleBlur(row: LocalConfigParamData) {
  // 检查是否存在重名的参数
  const index = processStore.parameters.findIndex(item => item.varName === row.varName && item.id !== row.id)
  if (index !== -1) {
    messageApi.warning('参数名称已存在')
    row.varName = row.perVarName
    return
  }

  await handleChange(row)

  flowStore.flowVariableUpdate({
    varName: row.perVarName,
    varType: PARAMETER_VAR_IN_TYPE,
    newVarName: row.varName,
    type: 'rename',
    processId: processStore.activeProcessId,
  })

  row.perVarName = row.varName
}

// 同步 formItem.value 到 varValue
function syncVarValueFromFormItem(row: LocalConfigParamData) {
  if (isArray(row.formItem?.value)) {
    row.varValue = convertArrayToVarValue(row.formItem.value)
  }
}

const handleChange = debounce((row: RPA.ConfigParamData) => processStore.updateParameter(row), 300, { leading: true })

function handleFormItemBlur(event: FocusEvent, row: LocalConfigParamData) {
  // 检查焦点是否还在容器内（relatedTarget 是获得焦点的元素）
  const currentTarget = event.currentTarget as HTMLElement
  const relatedTarget = event.relatedTarget as HTMLElement | null

  // 焦点移到了容器外则触发保存
  if (!currentTarget.contains(relatedTarget)) {
    syncVarValueFromFormItem(row)
    processStore.updateParameter(row)
  }
}
</script>

<template>
  <context-holder />
  <VxeGrid
    v-show="!isQuoted"
    v-bind="gridOptions"
    class="params-table w-full overflow-hidden"
    :class="[colorTheme]"
    :height="props.height"
    :data="searchedData"
    :empty-text="emptyText"
  >
    <template #name_default="{ row }">
      <Input v-model:value="row.varName" :bordered="false" class="text-xs text-inherit" @blur="handleBlur(row)" />
    </template>
    <template #usage_default="{ row }">
      <Select v-model:value="row.varDirection" :options="usageOptions" class="w-full" size="small" :bordered="false" @change="handleChange(row)" />
    </template>
    <template #type_default="{ row }">
      <Select v-model:value="row.varType" :options="varTypeOptions" class="w-full" size="small" :bordered="false" @change="handleChange(row)" />
    </template>
    <template #default_default="{ row }">
      <div v-if="row.formItem" @focusout="(e) => handleFormItemBlur(e, row)">
        <AtomConfig :form-item="row.formItem" size="small" />
      </div>
    </template>
    <template #desc_default="{ row }">
      <Input v-model:value="row.varDescribe" :bordered="false" class="text-xs text-inherit" @blur="handleChange(row)" />
    </template>
    <template #operation_default="{ row }">
      <Button type="link" size="small" class="!text-xs" @click="findQuoted(row)">
        查找引用
      </Button>
      <Button type="link" size="small" class="!text-xs" @click="deleteEvent(row)">
        删除
      </Button>
    </template>
  </VxeGrid>
  <div v-show="isQuoted" class="p-2 overflow-y-auto" :style="{ height: `${props.height}px` }">
    <ElementUseFlowList
      v-if="quotedData && quotedData.items.length > 0"
      :use-name="quotedData.name"
      :use-flow-items="quotedData.items"
    />
    <a-empty v-else description="暂无引用" />
  </div>
</template>

  <style lang="scss" scoped>
  .params-table {
  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;
  --vxe-ui-font-color: rgba(0, 0, 0, 0.85);
  --vxe-ui-table-header-font-color: rgba(0, 0, 0, 0.45);
  --vxe-ui-table-header-font-weight: 400;
  --vxe-ui-table-border-color: rgba(0, 0, 0, 0.08);

  // 抵消tabpanel的padding影响
  width: calc(100% + 16px);
  margin-left: -8px;
  margin-top: -8px;

  &.dark {
    --vxe-ui-font-color: rgba(255, 255, 255, 0.85);
    --vxe-ui-table-header-font-color: rgba(255, 255, 255, 0.45);
    --vxe-ui-table-border-color: rgba(255, 255, 255, 0.08);
  }

  :deep(.vxe-table--body) {
    --vxe-ui-table-cell-padding-left: 0;
    --vxe-ui-table-cell-padding-right: 0;
  }

  :deep(.vxe-table--border-line) {
    border-top: none;
    border-left: none;
    border-right: none;
  }

  :deep(.ant-select) {
    color: inherit;
  }

  :deep(.ant-select .ant-select-selector) {
    font-size: 12px;
    color: inherit;
  }
  :deep(.ant-select-selection-item),
  :deep(.ant-select-arrow),
  :deep(.ant-btn-link) {
    color: $color-primary;
  }
}
</style>
