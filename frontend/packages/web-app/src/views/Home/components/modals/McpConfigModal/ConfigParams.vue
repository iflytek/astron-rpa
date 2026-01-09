<script lang="ts" setup>
import { useTheme } from '@rpa/components'
import { Input } from 'ant-design-vue'
import { debounce } from 'lodash-es'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import { useProcessStore } from '@/stores/useProcessStore.ts'

const processStore = useProcessStore()
const { isDark } = useTheme()

const gridOptions: VxeGridProps<RPA.ConfigParamData> = {
  size: 'mini',
  scrollY: { enabled: true },
  border: true,
  showOverflow: true,
  keepSource: true,
  rowConfig: { isHover: true },
  columns: [
    { field: 'varName', title: '变量名', slots: { default: 'name_default' } },
    { field: 'varDirection', title: '输入/输出', slots: { default: 'usage_default' } },
    { field: 'varType', title: '类型', slots: { default: 'type_default' } },
    { field: 'varDescribe', title: '简介', slots: { default: 'desc_default' } },
  ],
}

const handleChange = debounce((row: RPA.ConfigParamData) => processStore.updateParameter(row), 300, { leading: true })
</script>

<template>
  <VxeGrid
    v-bind="gridOptions"
    class="config-params"
    border="none"
    :header-cell-style="{
      color: isDark ? 'rgba(255, 255, 255, 0.45)' : 'rgba(0, 0, 0, 0.45)',
      fontWeight: '400',
    }"
    :height="200"
  >
    <template #desc_default="{ row }">
      <Input v-model:value="row.varDescribe" :bordered="false" class="text-xs text-inherit" @blur="handleChange(row)" />
    </template>
  </VxeGrid>
</template>

<style lang="scss" scoped>
.config-params {
  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;

  overflow: hidden;
  width: 100%;

  :deep(.vxe-table--body) {
    --vxe-ui-table-cell-padding-left: 0;
    --vxe-ui-table-cell-padding-right: 0;
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
