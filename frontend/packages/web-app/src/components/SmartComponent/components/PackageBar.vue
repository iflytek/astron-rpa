<script lang="ts" setup>
import { computed } from 'vue'

import loadingSvg from '@/assets/img/loading.svg'

import CollapsePanel from './CollapsePanel.vue'

const props = defineProps<{
  lackPackages: string[]
  initialLackPackages: string[]
  isInstalling: boolean
  isCompleted: boolean
}>()

const showPanel = computed(() => props.lackPackages.length > 0 || props.isInstalling || props.isCompleted)
const displayPackages = computed(() => props.isCompleted ? props.initialLackPackages : props.lackPackages)
</script>

<template>
  <CollapsePanel v-if="showPanel" class="bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08] rounded-lg p-2">
    <template #title>
      <div v-if="isInstalling" class="flex-1 flex items-center gap-2">
        <img :src="loadingSvg" alt="loading" class="w-4 h-4 animate-spin">
        <span>正在安装缺失依赖库...</span>
      </div>
      <div v-else-if="isCompleted" class="flex-1 flex items-center gap-2">
        <rpa-icon name="success" size="16" />
        <span>已安装缺失依赖库</span>
      </div>
      <div v-else class="flex-1 flex items-center gap-2">
        <rpa-icon name="python-install-warn" size="16" />
        <span>缺失依赖库</span>
      </div>
    </template>
    <div v-if="displayPackages.length > 0" class="space-y-2 text-[12px]">
      <div v-for="item in displayPackages" :key="item" class="flex items-center gap-2">
        <rpa-icon
          name="create-python-process"
          size="16"
        />
        <span class="flex-1 text-text-secondary">{{ item }}</span>
      </div>
    </div>
  </CollapsePanel>
</template>
