<script lang="ts" setup>
import { computed } from 'vue'

import ComponentDetailPanel from '../components/ComponentDetailPanel.vue'
import { useSmartComp } from '../hooks'

const emit = defineEmits<{
  (evt: 'close-version-manage', e: boolean)
}>()

const smartComp = useSmartComp()

const versionList = computed(() => smartComp.versionList.value)
</script>

<template>
  <div class="w-[280px] flex flex-col bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.08] rounded-lg">
    <div class="h-[56px] flex items-center justify-between p-4">
      <span>版本管理</span>
      <rpa-hint-icon name="close" enable-hover-bg size="20" @click="emit('close-version-manage', false)" />
    </div>
    <a-divider class="!my-0" />
    <div class="p-2 flex-1 overflow-hidden">
      <div v-if="versionList.length === 0" class="h-full flex items-center justify-center text-text-tertiary">
        暂无版本
      </div>
      <div v-else class="h-full flex flex-col gap-2 overflow-auto">
        <ComponentDetailPanel
          v-for="(version, index) in versionList"
          :key="version.version || index"
          :version="version"
          show-time
        />
      </div>
    </div>
  </div>
</template>
