<script setup lang="ts">
import { onBeforeUnmount, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'

import { startPickServices, stopPickServices } from '@/api/engine'
import { taskNotify } from '@/api/task'
import Header from '@/components/Header.vue'
import HeaderControl from '@/components/HeaderControl/HeaderControl.vue'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'

const processStore = useProcessStore()
const runningStore = useRunningStore()
const route = useRoute()

async function initByRoute() {
  const projectId = route?.query?.projectId as string
  const projectName = route?.query?.projectName as string
  const projectVersion = Number(route?.query?.projectVersion) || 0

  if (!projectId)
    return

  processStore.setProject({ id: projectId, name: projectName, version: projectVersion })
  await processStore.canvasManager.init(projectId)
}

watch(
  () => [route?.query?.projectId, route?.query?.projectName, route?.query?.projectVersion],
  () => {
    initByRoute()
  },
  { immediate: true },
)

let isStart = false

onMounted(async () => {
  taskNotify({ event: 'login' })
  runningStore.fetchDataTable()
  await startPickServices({})
  isStart = true
})

onUnmounted(async () => {
  if (!isStart) return 
  await stopPickServices({})
  isStart = false
})

onBeforeUnmount(() => {
  useRunlogStore().clearLogs() // 清空日志
  runningStore.closeDataTableListener()
  processStore.canvasManager.reset()
})
</script>

<template>
  <div class="flex flex-col w-full h-full bg-[#ecedf4] dark:bg-[#141414]">
    <Header>
      <template #headControl>
        <HeaderControl :user-info="false" />
      </template>
    </Header>
    <router-view v-slot="{ Component }">
      <keep-alive :include="['EditorPage']">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>
