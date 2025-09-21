<script setup>
import { Segmented } from 'ant-design-vue'
import { ref } from 'vue'

import RecordTable from '../components/RecordTable/index.vue'
import TaskRecordTable from '../components/TaskRecordTable/index.vue'

const tabs = [
  {
    label: '任务执行记录',
    value: 'taskrecord',
  },
  {
    label: '机器人执行记录',
    value: 'robotrecord',
  },
]

const currentTab = ref('taskrecord')
</script>

<template>
  <div>
    <Segmented v-model:value="currentTab" :options="tabs" class="mt-[12px] mb-[20px]" />
    <div class="w-full h-[calc(100vh-120px)] p-5 pb-1 mb-5 rounded-[16px] bg-[#fff] dark:bg-[rgba(255,255,255,0.04)]">
      <TaskRecordTable v-if="currentTab === 'taskrecord'" />
      <RecordTable v-else />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ant-modal-confirm-body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
}
</style>
