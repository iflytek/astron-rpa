<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'
import { useApplicationTable } from '@/views/Home/components/TeamMarket/hooks/useApplicationTable'

const { tableRef, tableOption } = useApplicationTable()
</script>

<template>
  <div class="h-[calc(100%-40px)] bg-[#fff] dark:bg-[rgba(255,255,255,0.04)] rounded-[16px] p-4 m-5 ml-0 ">
    <NormalTable ref="tableRef" :option="tableOption" />
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-table) {
  background-color: transparent;

  .ant-table-cell::before {
    display: none;
  }
}
</style>
