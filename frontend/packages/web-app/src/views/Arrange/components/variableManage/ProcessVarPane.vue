<script setup lang="ts">
import { Table } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import { ATOM_FORM_TYPE } from '@/constants/atom'
import { useProcessStore } from '@/stores/useProcessStore'
import useProjectDocStore from '@/stores/useProjectDocStore'
import { useVariableStore } from '@/stores/useVariableStore'

import { paginationConfig } from '../tools/components/constant'

const processStore = useProcessStore()
const { t } = useTranslation()
const processId = ref(processStore.activeProcessId)
const keyword = ref('')
const varData = ref([])

const columns = [
  { title: '原子能力名', dataIndex: 'anotherName' },
  { title: '变量名', dataIndex: 'name' },
  { title: '类型', dataIndex: 'types' },
  { title: '行号', dataIndex: 'rowNum' },
]

function handleSearchChange() {
  if (!keyword.value)
    return handleProcessChange()
  varData.value = varData.value.filter(item =>
    item.value.find(val => val.value.toLocaleLowerCase().includes(keyword.value.toLocaleLowerCase())),
  )
}
function handleProcessChange() {
  console.log(processId.value)
  getTableData(
    useProjectDocStore().userFlowNode(processId.value).length,
    processId.value,
  )
}

function getTableData(len: number, processId?: string) {
  varData.value = useVariableStore().filterCurrentVariableListByType(
    ATOM_FORM_TYPE.RESULT,
    len,
    processId,
  )
}
getTableData(useProjectDocStore().userFlowNode().length)
</script>

<template>
  <div class="process-var-panel">
    <nav class="flex justify-end  mb-3 items-center gap-2">
      <a-select v-model:value="processId" class="w-[150px] bg-[#F3F3F7] dark:bg-[rgba(255,255,255,0.08)] dark:text-[rgba(255,255,255,0.85)] text-[12px]" @change="handleProcessChange">
        <a-select-option v-for="item in processStore.processList" :key="item.resourceId" :value="item.resourceId">
          {{ item.name }}
        </a-select-option>
      </a-select>
      <a-input
        v-model:value="keyword"
        allow-clear
        class="flex-1 leading-6"
        :placeholder="t('enterVaruableName')"
        @change="handleSearchChange"
      >
        <template #prefix>
          <rpa-icon name="search" class="dark:text-[rgba(255,255,255,0.25)]" />
        </template>
      </a-input>
    </nav>
    <Table size="small" :columns="columns" :data-source="varData" :pagination="paginationConfig">
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'name'">
          <span v-for="(item, index) in record.value" :key="index">
            {{ item.value }}
          </span>
        </template>
        <template v-if="column.dataIndex === 'types'">
          <span>{{ processStore.globalVarTypeList[record.types].desc }}</span>
        </template>
      </template>
    </Table>
  </div>
</template>

<style lang="scss" scoped>
.process-var-panel {
  --table-head-default: rgba(0, 0, 0, 0.45);
  --table-body-default: rgba(0, 0, 0, 0.85);

  .dark & {
    --table-head-default: rgba(255, 255, 255, 0.45);
    --table-body-default: rgba(255, 255, 255, 0.85);
  }
}
.global-variable-plus {
  height: 24px;
  font-size: 12px;
  font-family:
    PingFang SC,
    PingFang SC-400;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.85);
  line-height: 24px;
  margin-left: 10px;
  cursor: pointer;

  &:hover {
    color: $color-primary;
  }
}

:deep(.ant-select-selector) {
  font-size: inherit;
  background-color: inherit !important;
  color: inherit;
}

:deep(.ant-table-thead > tr > th) {
  font-size: 12px;
  color: var(--table-head-default);
  background: transparent;
}

:deep(.ant-table-tbody > tr > td) {
  font-size: 14px;
  color: var(--table-body-default);
}

.ant-table-thead > tr > th,
.ant-table-tbody > tr > td {
  padding: 14px 16px;
  font-weight: 400;
}
</style>
