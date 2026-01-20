<script lang="ts" setup>
import { Empty } from 'ant-design-vue'
import { computed, onBeforeMount } from 'vue'

import loadingSvg from '@/assets/img/loading.svg'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'

import { injectChatContext } from '../hooks'

const runlogStore = useRunlogStore()
const runningStore = useRunningStore()
const { fixCode } = injectChatContext()

const shouldShowLogView = computed(() => {
  return runlogStore.logList.length > 0
})

const isExecuting = computed(() => {
  return runningStore.running === 'debug' || runningStore.running === 'run'
})

const hasErrors = computed(() => {
  return runlogStore.logList.some(log => log.logLevel === 'error')
})

const errorLogs = computed(() => {
  return runlogStore.logList
    .filter(log => log.logLevel === 'error' && log.error_traceback && log.logType === 'code')
    .map((log) => {
      const traceback = log.error_traceback || ''
      const lines = traceback.split('\n').filter(line => line.trim())

      // 找到最后一个包含 "File " 和 "smart" 的行
      let lastFileLine: string | null = null
      for (let i = lines.length - 1; i >= 0; i--) {
        const line = lines[i]
        if (line.includes('File ') && line.includes('smart')) {
          lastFileLine = line
          break
        }
      }

      // 解析错误信息
      let formattedContent = log.content
      if (lastFileLine) {
        const lineMatch = lastFileLine.match(/line\s+(\d+)/i)
        if (lineMatch) {
          const lineNumber = Number.parseInt(lineMatch[1], 10)
          const execErrorMatch = log.content.match(/执行错误\s*(.+)/)
          const errorMessage = execErrorMatch ? execErrorMatch[1].trim() : log.content
          formattedContent = `源代码第【${lineNumber}】行出错: ${errorMessage}`
        }
      }

      return {
        ...log,
        formattedContent,
      }
    })
})

const normalLogs = computed(() => {
  return runlogStore.logList.filter(log => log.logLevel !== 'error')
})

// 关闭日志窗口
function closeLogView() {
  runlogStore.clearLogs()
}

onBeforeMount(() => closeLogView())
</script>

<template>
  <div v-if="shouldShowLogView" class="h-[280px] flex flex-col bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.08] rounded-lg">
    <section class="flex justify-between items-center px-4 py-[10px]">
      <div class="flex items-center gap-2 font-medium">
        <template v-if="hasErrors">
          <rpa-icon name="error" size="16" />
          <span>执行失败</span>
        </template>
        <template v-else-if="isExecuting">
          <img :src="loadingSvg" alt="loading" class="w-4 h-4 animate-spin">
          <span>执行中</span>
        </template>
        <template v-else>
          <rpa-icon name="success" size="16" />
          <span>执行成功</span>
        </template>
      </div>
      <rpa-hint-icon name="close" size="20" enable-hover-bg @click="closeLogView" />
    </section>

    <a-divider class="!my-0" />

    <section class="flex-1 px-4 py-[10px] overflow-hidden">
      <div v-if="runlogStore.logList.length > 0" class="h-full overflow-y-auto">
        <span
          v-for="(log, index) in normalLogs"
          :key="log.id || index"
          class="block"
        >
          {{ log.content }}
        </span>

        <div
          v-for="(log, index) in errorLogs"
          :key="log.id || index"
          class="flex items-center my-2 px-3 py-2 bg-[#FFF2F0] rounded-lg"
        >
          <rpa-icon name="error" size="16" />
          <span class="ml-2 flex-1 dark:text-[#000000]/[.85]">{{ log.formattedContent }}</span>
          <a-button type="link" class="text-primary" @click="fixCode(log)">
            一键修复
          </a-button>
        </div>
      </div>
      <a-empty v-else :image="Empty.PRESENTED_IMAGE_SIMPLE" />
    </section>
  </div>
</template>
