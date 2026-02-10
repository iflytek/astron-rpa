<script lang="ts" setup>
defineProps<{
  isGenerating?: boolean
  duration?: number // 耗时(S)
}>()
</script>

<template>
  <div v-if="isGenerating" class="flex items-center gap-2 p-2">
    <rpa-icon name="magic-wand" size="16" class="text-primary" />
    <span>{{ $t('smartComponent.assistantWorking') }}</span>
  </div>
  <div v-else-if="duration" class="flex items-center gap-2 p-2">
    <rpa-icon name="magic-wand" size="16" class="text-primary" />
    <span>{{ $t('smartComponent.duration', { duration }) }}</span>
  </div>
</template>
