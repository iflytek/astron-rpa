<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { nanoid } from 'nanoid'
import { ref, shallowRef, watch } from 'vue'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import AtomConfig from './AtomConfig.vue'

interface PARAM_MAP {
  id: string
  varName: string
  perVarName?: string
  varValue: string
}

const props = defineProps<{ height?: number, params: RPA.AtomDisplayItem }>()
const emit = defineEmits(['refresh'])

const gird = shallowRef()
const paramsData = ref(tranformToFront(JSON.parse(props?.params?.value as string || '[]')))
// console.log('paramsData', paramsData.value)

const gridOptions: VxeGridProps<PARAM_MAP> = {
  size: 'mini',
  scrollY: { enabled: true },
  border: true,
  showOverflow: true,
  keepSource: true,
  rowConfig: { isHover: true },
  columnConfig: { resizable: true },
  columns: [
    { field: 'varName', title: '参数名称', width: 80, slots: { default: 'name_default' } },
    { field: 'varValue', title: '参数值', slots: { default: 'default_default' } },
    { field: 'operation', title: '操作', width: 60, slots: { default: 'operation_default' } },
  ],
}

watch(() => paramsData.value, (val) => {
  emit('refresh', JSON.stringify(tranformToEnd(val)))
}, { deep: true })

// 转换成前端需要的数据结构
function tranformToFront(paramsArray) {
  return paramsArray.map(item => ({
    id: nanoid(),
    varName: item.varName,
    perVarName: item.varName,
    varValue: {
      formType: { type: 'INPUT_VARIABLE' },
      key: nanoid(),
      title: '',
      value: item.varValue.value,
    },
  }))
}

// 转换成后端需要的数据结构
function tranformToEnd(paramsData) {
  const res = paramsData.map(item => ({
    varName: item.varName,
    varValue: {
      rpa: 'special',
      value: item.varValue.value,
    },
  }))
  // console.log('tranformToEnd', res)
  return res
}

// 生成唯一参数名称
function generateParamName() {
  const baseName = 'para'
  let count = 0
  let finalName = baseName

  while (paramsData.value.some(param => param.varName === finalName)) {
    count += 1
    finalName = `${baseName}_${count}`
  }

  return finalName
}

function addParam() {
  const newName = generateParamName()
  paramsData.value.push({
    id: nanoid(),
    varName: newName,
    perVarName: newName,
    varValue: {
      formType: { type: 'INPUT_VARIABLE' },
      key: nanoid(),
      title: '',
      value: [{
        type: 'other',
        value: '',
      }],
    },
  })
  requestAnimationFrame(() => {
    gird.value?.scrollToRow(paramsData.value[paramsData.value.length - 1])
  })
}

function deleteParam(id: string) {
  console.log(id)
  paramsData.value = paramsData.value.filter(item => item.id !== id)
}

function handleBlur(row: PARAM_MAP) {
  console.log(row)
  // 检查是否存在重名的参数
  const index = paramsData.value.findIndex(item => item.varName === row.varName && item.id !== row.id)
  if (index !== -1) {
    message.warning('参数名称已存在')
    row.varName = row.perVarName
    return
  }
  row.perVarName = row.varName
}
</script>

<template>
  <div class="flex flex-col w-full">
    <VxeGrid
      ref="gird"
      v-bind="gridOptions"
      class="params-table"
      :height="props.height"
      :data="paramsData"
    >
      <template #name_default="{ row }">
        <a-input v-model:value="row.varName" class="text-xs text-inherit" @blur="handleBlur(row)" />
      </template>
      <template #default_default="{ row }">
        <AtomConfig :key="row.id" :form-item="row.varValue" size="small" />
      </template>
      <template #operation_default="{ row }">
        <a-popconfirm title="确定删除么?" @confirm="deleteParam(row.id)">
          <a href="#">删除</a>
        </a-popconfirm>
      </template>
    </VxeGrid>
    <rpa-hint-icon name="python-package-plus" class="mt-2 w-min whitespace-nowrap text-primary" enable-hover-bg @click="addParam">
      <template #suffix>
        <span class="ml-1">添加参数</span>
      </template>
    </rpa-hint-icon>
  </div>
</template>

<style lang="scss">
.params-table {
  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;

  overflow: hidden;
  width: 100%;

  :deep(.vxe-table--body) {
    --vxe-ui-table-cell-padding-left: 0;
    --vxe-ui-table-cell-padding-right: 0;
  }
  .ant-popconfirm-buttons {
    width: 120px;
  }
}
</style>
