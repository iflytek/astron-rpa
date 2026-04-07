<script setup lang="ts">
import { CloseOutlined } from '@ant-design/icons-vue'

import type { PointsModalTabKey } from '../types'
import { POINTS_MODAL_TABS } from '../types'

defineProps<{
  activeTab: PointsModalTabKey
}>()

const emit = defineEmits<{
  'update:activeTab': [PointsModalTabKey]
  close: []
}>()

function selectTab(key: PointsModalTabKey) {
  emit('update:activeTab', key)
}
</script>

<template>
  <div class="flex w-full shrink-0 items-center justify-between self-stretch">
    <div class="flex items-end gap-6">
      <button
        v-for="tab in POINTS_MODAL_TABS"
        :key="tab.key"
        type="button"
        class="border-0 bg-transparent p-0"
        @click="selectTab(tab.key)"
      >
        <span
          class="whitespace-nowrap"
          :class="
            activeTab === tab.key
              ? 'text-[20px] font-bold leading-[28px] text-[#1A1512] dark:text-white'
              : 'text-[16px] font-medium leading-[24px] !text-[rgba(0,0,0,0.45)] dark:!text-[rgba(255,255,255,0.45)]'
          "
        >
          {{ tab.label }}
        </span>
      </button>
    </div>
    <button
      type="button"
      class="inline-flex h-4 w-4 shrink-0 items-center justify-center border-0 bg-transparent p-0 text-black/[0.45] hover:text-black/[0.85] dark:text-white/[0.45] dark:hover:text-white/[0.85]"
      aria-label="关闭"
      @click="emit('close')"
    >
      <CloseOutlined class="text-base" />
    </button>
  </div>
</template>
