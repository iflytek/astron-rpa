<script setup>
import NormalTable from '@/components/NormalTable/index.vue'

import useTaskRecordTableOption from './hooks/useTaskRecordTableOption.tsx'

const props = defineProps({
  robotId: String,
})

const { homeTableRef, tableOption } = useTaskRecordTableOption(props)
</script>

<template>
  <div class="task-record-table h-full">
    <NormalTable ref="homeTableRef" :option="tableOption" />
  </div>
</template>

<style lang="scss">
.task-record-table {
  .ant-table-expand-icon-col {
    width: 0 !important;
  }
  .ant-table-expanded-row {
    > td {
      padding: 8px 0 !important;
      .ant-table {
        margin: 0 !important;
        background: transparent !important;
        td,
        th,
        tr {
          background: transparent !important;
        }
        .ant-table-thead > tr > th:first-child::before {
          display: none !important;
        }
      }
    }
  }
}
</style>
