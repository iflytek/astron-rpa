<template>
  <div class="relative w-[45%] h-full whitespace-pre-line overflow-hidden flex flex-col bg-bg-elevated rounded-2xl">
    <div class="flex items-center justify-between h-[50px] px-4 gap-4">
      <p class="text-sm font-medium truncate">{{ props.fileInfo.name }}</p>
      <CloseOutlined class="text-xl" @click="emit('close')" />
    </div>
    <div class="flex-1 overflow-y-auto px-4 scroller">
      <p v-if="props.fileInfo.suffix === 'txt'">{{ props.fileInfo.previewContent }}</p>
      <PDFPreview v-else-if="props.fileInfo.suffix === 'pdf'" :source="props.fileInfo.previewContent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { CloseOutlined } from '@ant-design/icons-vue'

import PDFPreview from './PDFPreview.vue'
import type { FileInfo } from './utils';

const props = defineProps<{ fileInfo: FileInfo }>()
const emit = defineEmits(['close'])
</script>

<style scoped>
.scroller {
  --scrollbar-color-thumb: var(--color-text-quaternary);
  --scrollbar-color-track: transparent;
  --scrollbar-width: thin;
  --scrollbar-width-legacy: 4px;
}

/* Modern browsers with `scrollbar-*` support */
@supports (scrollbar-width: auto) {
  .scroller {
    scrollbar-color: var(--scrollbar-color-thumb) var(--scrollbar-color-track);
    scrollbar-width: var(--scrollbar-width);
  }
}

/* Legacy browsers with `::-webkit-scrollbar-*` support */
@supports selector(::-webkit-scrollbar) {
  .scroller::-webkit-scrollbar-thumb {
    background: var(--scrollbar-color-thumb);
  }
  .scroller::-webkit-scrollbar-track {
    background: var(--scrollbar-color-track);
  }
  .scroller::-webkit-scrollbar {
    max-width: var(--scrollbar-width-legacy);
    max-height: var(--scrollbar-width-legacy);
  }
}
</style>
