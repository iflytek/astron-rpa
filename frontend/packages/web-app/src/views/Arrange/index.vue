<script setup lang="ts">
import { onBeforeUnmount, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

import { startPickServices, stopPickServices } from '@/api/engine'
import { taskNotify } from '@/api/task'
import Header from '@/components/Header.vue'
import HeaderControl from '@/components/HeaderControl/HeaderControl.vue'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { useSharedData } from '@/stores/useSharedData'

import ArrangeContent from './Content.vue'

const processStore = useProcessStore()
const sharedData = useSharedData()
const runningStore = useRunningStore()

const projectId = useRoute()?.query?.projectId as string
const projectName = useRoute()?.query?.projectName as string

processStore.setProject({ id: projectId, name: projectName })
sharedData.getSharedVariables()
sharedData.getSharedFiles()

let isStart = false

onMounted(() => {
  startPickServices({}).then(() => {
    isStart = true
  })
  taskNotify({ event: 'login' })
  runningStore.fetchDataTable()
})

onUnmounted(() => {
  if (isStart) {
    stopPickServices({}).then(() => {
      isStart = false
    })
  }
})
onBeforeUnmount(() => {
  useRunlogStore().clearLogs() // 清空日志
  runningStore.closeDataTableListener()
})
</script>

<template>
  <div class="flex flex-col w-full h-full bg-[#ecedf4] dark:bg-[#141414]">
    <Header class="!relative">
      <template #headControl>
        <HeaderControl :user-info="false" />
      </template>
    </Header>
    <ArrangeContent />
  </div>
</template>
