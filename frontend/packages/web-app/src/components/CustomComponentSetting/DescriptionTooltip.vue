<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

const props = defineProps<{
  descriptionValue?: Array<{ type: string; value: string }>
}>()

const processStore = useProcessStore()

const defaultDescriptionValue = [
  { type: 'other', value: '将' },
  { type: 'p_var', value: '参数1' },
  { type: 'other', value: '赋值给变量' },
  { type: 'p_var', value: '参数2' },
]

const displayValue = computed(() => {
  const hasContent = props.descriptionValue?.some(item => item.value?.trim())
  return hasContent ? props.descriptionValue : defaultDescriptionValue
})
</script>

<template>
  <div class="min-w-[160px] p-2 flex flex-col gap-2 text-[12px]">
    <button class="flex justify-center items-center w-[48px] h-[18px] rounded bg-[#FFFFFF]/[.1]">示例</button>
    <div class="flex items-center gap-2">
      <rpa-icon name="avatar-comp-1" />
      <span>{{ processStore.project?.name || '' }}</span>
    </div>
    <div>
      <template v-for="(item, index) in displayValue" :key="index">
        <span v-if="item.type === 'p_var' || item.type === 'var'" class="mx-[4px] py-[2px] px-[4px] text-[#726FFF] bg-[#726FFF]/[.1] rounded">
          {{ item.value }}
        </span>
        <span v-else class="text-[#FFFFFF]/[.65]">{{ item.value }}</span>
      </template>
    </div>
  </div>
</template>