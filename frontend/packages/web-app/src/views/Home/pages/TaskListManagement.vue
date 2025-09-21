<!-- @format -->

<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'
import QueueModal from '@/views/Home/components/QueueManagement/Index.vue'

import { useTaskTableOption } from './hooks/TaskListManagement/useTaskTableOption.tsx'

const { tableOption, taskListTableRef, hideQueue, showQueue } = useTaskTableOption()
</script>

<template>
  <div class="w-full h-[calc(100vh-90px)] p-5 pb-1 mt-8 rounded-[16px] bg-[#fff] dark:bg-[rgba(255,255,255,0.04)]">
    <NormalTable ref="taskListTableRef" :option="tableOption" />
  </div>
  <QueueModal v-if="showQueue" @cancel="hideQueue" />
</template>
