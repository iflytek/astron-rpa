<script lang="ts" setup>
defineProps<{
  isGenerating?: boolean
  duration?: number // 耗时(S)
}>()
</script>

<template>
  <div v-if="isGenerating" class="flex items-center gap-2 p-2">
    <rpa-icon name="magic-wand" size="16" class="text-primary" />
    <span>智能组件生成助手工作中...</span>
  </div>
  <div v-else-if="duration" class="flex items-center gap-2 p-2">
    <rpa-icon name="magic-wand" size="16" class="text-primary" />
    <span>耗时 {{ duration }}s</span>
  </div>
</template>
